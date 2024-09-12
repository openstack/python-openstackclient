#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

"""Base API Library"""

from keystoneauth1 import exceptions as ks_exceptions
from keystoneauth1 import session as ks_session
from osc_lib import exceptions
import requests

from openstackclient.i18n import _


class KeystoneSession:
    """Wrapper for the Keystone Session

    Restore some requests.session.Session compatibility;
    keystoneauth1.session.Session.request() has the method and url
    arguments swapped from the rest of the requests-using world.

    """

    def __init__(self, session=None, endpoint=None, **kwargs):
        """Base object that contains some common API objects and methods

        :param Session session:
            The default session to be used for making the HTTP API calls.
        :param string endpoint:
            The URL from the Service Catalog to be used as the base for API
            requests on this API.
        """

        super().__init__()

        # a requests.Session-style interface
        self.session = session
        self.endpoint = endpoint

    def _request(self, method, url, session=None, **kwargs):
        """Perform call into session

        All API calls are funneled through this method to provide a common
        place to finalize the passed URL and other things.

        :param string method:
            The HTTP method name, i.e. ``GET``, ``PUT``, etc
        :param string url:
            The API-specific portion of the URL path
        :param Session session:
            HTTP client session
        :param kwargs:
            keyword arguments passed to requests.request().
        :return: the requests.Response object
        """

        if not session:
            session = self.session
        if not session:
            session = ks_session.Session()

        if self.endpoint:
            if url:
                url = '/'.join([self.endpoint.rstrip('/'), url.lstrip('/')])
            else:
                url = self.endpoint.rstrip('/')

        # Why is ksc session backwards???
        return session.request(url, method, **kwargs)


class BaseAPI(KeystoneSession):
    """Base API"""

    def __init__(
        self, session=None, service_type=None, endpoint=None, **kwargs
    ):
        """Base object that contains some common API objects and methods

        :param Session session:
            The default session to be used for making the HTTP API calls.
        :param string service_type:
            API name, i.e. ``identity`` or ``compute``
        :param string endpoint:
            The URL from the Service Catalog to be used as the base for API
            requests on this API.
        """

        super().__init__(session=session, endpoint=endpoint)

        self.service_type = service_type

    # The basic action methods all take a Session and return dict/lists

    def create(self, url, session=None, method=None, **params):
        """Create a new resource

        :param string url:
            The API-specific portion of the URL path
        :param Session session:
            HTTP client session
        :param string method:
            HTTP method (default POST)
        """

        if not method:
            method = 'POST'
        ret = self._request(method, url, session=session, **params)
        # Should this move into _requests()?
        try:
            return ret.json()
        except requests.JSONDecodeError:
            return ret

    def delete(self, url, session=None, **params):
        """Delete a resource

        :param string url:
            The API-specific portion of the URL path
        :param Session session:
            HTTP client session
        """

        return self._request('DELETE', url, **params)

    def list(self, path, session=None, body=None, detailed=False, **params):
        """Return a list of resources

        GET ${ENDPOINT}/${PATH}?${PARAMS}

        path is often the object's plural resource type

        :param string path:
            The API-specific portion of the URL path
        :param Session session:
            HTTP client session
        :param body: data that will be encoded as JSON and passed in POST
            request (GET will be sent by default)
        :param bool detailed:
            Adds '/details' to path for some APIs to return extended attributes
        :returns:
            JSON-decoded response, could be a list or a dict-wrapped-list
        """

        if detailed:
            path = '/'.join([path.rstrip('/'), 'details'])

        if body:
            ret = self._request(
                'POST',
                path,
                json=body,
                params=params,
            )
        else:
            ret = self._request(
                'GET',
                path,
                params=params,
            )
        try:
            return ret.json()
        except requests.JSONDecodeError:
            return ret

    # Layered actions built on top of the basic action methods do not
    # explicitly take a Session but one may still be passed in kwargs

    def find_attr(
        self,
        path,
        value=None,
        attr=None,
        resource=None,
    ):
        """Find a resource via attribute or ID

        Most APIs return a list wrapped by a dict with the resource
        name as key.  Some APIs (Identity) return a dict when a query
        string is present and there is one return value.  Take steps to
        unwrap these bodies and return a single dict without any resource
        wrappers.

        :param string path:
            The API-specific portion of the URL path
        :param string value:
            value to search for
        :param string attr:
            attribute to use for resource search
        :param string resource:
            plural of the object resource name; defaults to path

        For example:
            n = find(netclient, 'network', 'networks', 'matrix')
        """

        # Default attr is 'name'
        if attr is None:
            attr = 'name'

        # Default resource is path - in many APIs they are the same
        if resource is None:
            resource = path

        def getlist(kw):
            """Do list call, unwrap resource dict if present"""
            ret = self.list(path, **kw)
            if isinstance(ret, dict) and resource in ret:
                ret = ret[resource]
            return ret

        # Search by attribute
        kwargs = {attr: value}
        data = getlist(kwargs)
        if isinstance(data, dict):
            return data
        if len(data) == 1:
            return data[0]
        if len(data) > 1:
            msg = _("Multiple %(resource)s exist with %(attr)s='%(value)s'")
            raise exceptions.CommandError(
                msg % {'resource': resource, 'attr': attr, 'value': value}
            )

        # Search by id
        kwargs = {'id': value}
        data = getlist(kwargs)
        if len(data) == 1:
            return data[0]
        msg = _("No %(resource)s with a %(attr)s or ID of '%(value)s' found")
        raise exceptions.CommandError(
            msg % {'resource': resource, 'attr': attr, 'value': value}
        )

    def find_bulk(self, path, **kwargs):
        """Bulk load and filter locally

        :param string path:
            The API-specific portion of the URL path
        :param kwargs:
            A dict of AVPs to match - logical AND
        :returns: list of resource dicts
        """

        items = self.list(path)
        if isinstance(items, dict):
            # strip off the enclosing dict
            key = list(items.keys())[0]
            items = items[key]

        ret = []
        for o in items:
            try:
                if all(o[attr] == kwargs[attr] for attr in kwargs.keys()):
                    ret.append(o)
            except KeyError:
                continue

        return ret

    def find_one(self, path, **kwargs):
        """Find a resource by name or ID

        :param string path:
            The API-specific portion of the URL path
        :returns:
            resource dict
        """

        bulk_list = self.find_bulk(path, **kwargs)
        num_bulk = len(bulk_list)
        if num_bulk == 0:
            msg = _("none found")
            raise exceptions.NotFound(msg)
        elif num_bulk > 1:
            msg = _("many found")
            raise RuntimeError(msg)
        return bulk_list[0]

    def find(
        self,
        path,
        value=None,
        attr=None,
    ):
        """Find a single resource by name or ID

        :param string path:
            The API-specific portion of the URL path
        :param string value:
            search expression
        :param string attr:
            name of attribute for secondary search
        """

        try:
            ret = self._request('GET', f"/{path}/{value}").json()
        except ks_exceptions.NotFound:
            kwargs = {attr: value}
            try:
                ret = self.find_one(f"/{path}/detail", **kwargs)
            except ks_exceptions.NotFound:
                msg = _("%s not found") % value
                raise exceptions.NotFound(msg)

        return ret
