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

"""Compute v2 API Library"""

from keystoneauth1 import exceptions as ksa_exceptions
from osc_lib.api import api
from osc_lib import exceptions
from osc_lib.i18n import _


# TODO(dtroyer): Mingrate this to osc-lib
class InvalidValue(Exception):
    """An argument value is not valid: wrong type, out of range, etc"""
    message = "Supplied value is not valid"


class APIv2(api.BaseAPI):
    """Compute v2 API"""

    def __init__(self, **kwargs):
        super(APIv2, self).__init__(**kwargs)

    # Overrides

    def _check_integer(self, value, msg=None):
        """Attempt to convert value to an integer

        Raises InvalidValue on failure

        :param value:
            Convert this to an integer.  None is converted to 0 (zero).
        :param msg:
            An alternate message for the exception, must include exactly
            one substitution to receive the attempted value.
        """

        if value is None:
            return 0

        try:
            value = int(value)
        except (TypeError, ValueError):
            if not msg:
                msg = "%s is not an integer" % value
            raise InvalidValue(msg)
        return value

    # TODO(dtroyer): Override find() until these fixes get into an osc-lib
    #                minimum release
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
            search expression (required, really)
        :param string attr:
            name of attribute for secondary search
        """

        try:
            ret = self._request('GET', "/%s/%s" % (path, value)).json()
            if isinstance(ret, dict):
                # strip off the enclosing dict
                key = list(ret.keys())[0]
                ret = ret[key]
        except (
            ksa_exceptions.NotFound,
            ksa_exceptions.BadRequest,
        ):
            kwargs = {attr: value}
            try:
                ret = self.find_one(path, **kwargs)
            except ksa_exceptions.NotFound:
                msg = _("%s not found") % value
                raise exceptions.NotFound(msg)

        return ret

    # Security Groups

    def security_group_create(
        self,
        name=None,
        description=None,
    ):
        """Create a new security group

        https://developer.openstack.org/api-ref/compute/#create-security-group

        :param string name:
            Security group name
        :param integer description:
            Security group description
        """

        url = "/os-security-groups"

        params = {
            'name': name,
            'description': description,
        }

        return self.create(
            url,
            json={'security_group': params},
        )['security_group']

    def security_group_delete(
        self,
        security_group=None,
    ):
        """Delete a security group

        https://developer.openstack.org/api-ref/compute/#delete-security-group

        :param string security_group:
            Security group name or ID
        """

        url = "/os-security-groups"

        security_group = self.find(
            url,
            attr='name',
            value=security_group,
        )['id']
        if security_group is not None:
            return self.delete('/%s/%s' % (url, security_group))

        return None

    def security_group_find(
        self,
        security_group=None,
    ):
        """Return a security group given name or ID

        https://developer.openstack.org/api-ref/compute/#show-security-group-details

        :param string security_group:
            Security group name or ID
        :returns: A dict of the security group attributes
        """

        url = "/os-security-groups"

        return self.find(
            url,
            attr='name',
            value=security_group,
        )

    def security_group_list(
        self,
        limit=None,
        marker=None,
        search_opts=None,
    ):
        """Get security groups

        https://developer.openstack.org/api-ref/compute/#list-security-groups

        :param integer limit:
            query return count limit
        :param string marker:
            query marker
        :param search_opts:
            (undocumented) Search filter dict
            all_tenants: True|False - return all projects
        :returns:
            list of security groups names
        """

        params = {}
        if search_opts is not None:
            params = dict((k, v) for (k, v) in search_opts.items() if v)
        if limit:
            params['limit'] = limit
        if marker:
            params['offset'] = marker

        url = "/os-security-groups"
        return self.list(url, **params)["security_groups"]

    def security_group_set(
        self,
        security_group=None,
        # name=None,
        # description=None,
        **params
    ):
        """Update a security group

        https://developer.openstack.org/api-ref/compute/#update-security-group

        :param string security_group:
            Security group name or ID

        TODO(dtroyer): Create an update method in osc-lib
        """

        # Short-circuit no-op
        if params is None:
            return None

        url = "/os-security-groups"

        security_group = self.find(
            url,
            attr='name',
            value=security_group,
        )
        if security_group is not None:
            for (k, v) in params.items():
                # Only set a value if it is already present
                if k in security_group:
                    security_group[k] = v
            return self._request(
                "PUT",
                "/%s/%s" % (url, security_group['id']),
                json={'security_group': security_group},
            ).json()['security_group']
        return None

    # Security Group Rules

    def security_group_rule_create(
        self,
        security_group_id=None,
        ip_protocol=None,
        from_port=None,
        to_port=None,
        remote_ip=None,
        remote_group=None,
    ):
        """Create a new security group rule

        https://developer.openstack.org/api-ref/compute/#create-security-group-rule

        :param string security_group_id:
            Security group ID
        :param ip_protocol:
            IP protocol, 'tcp', 'udp' or 'icmp'
        :param from_port:
            Source port
        :param to_port:
            Destination port
        :param remote_ip:
            Source IP address in CIDR notation
        :param remote_group:
            Remote security group
        """

        url = "/os-security-group-rules"

        if ip_protocol.lower() not in ['icmp', 'tcp', 'udp']:
            raise InvalidValue(
                "%(s) is not one of 'icmp', 'tcp', or 'udp'" % ip_protocol
            )

        params = {
            'parent_group_id': security_group_id,
            'ip_protocol': ip_protocol,
            'from_port': self._check_integer(from_port),
            'to_port': self._check_integer(to_port),
            'cidr': remote_ip,
            'group_id': remote_group,
        }

        return self.create(
            url,
            json={'security_group_rule': params},
        )['security_group_rule']

    def security_group_rule_delete(
        self,
        security_group_rule_id=None,
    ):
        """Delete a security group rule

        https://developer.openstack.org/api-ref/compute/#delete-security-group-rule

        :param string security_group_rule_id:
            Security group rule ID
        """

        url = "/os-security-group-rules"
        if security_group_rule_id is not None:
            return self.delete('/%s/%s' % (url, security_group_rule_id))

        return None
