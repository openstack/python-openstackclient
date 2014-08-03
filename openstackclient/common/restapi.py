#   Copyright 2013 Nebula Inc.
#
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

"""REST API bits"""

import json
import logging
import requests

try:
    from urllib.parse import urlencode  # noqa
except ImportError:
    from urllib import urlencode  # noqa


USER_AGENT = 'RAPI'

_logger = logging.getLogger(__name__)


class RESTApi(object):
    """A REST API client that handles the interface from us to the server

    RESTApi is requests.Session wrapper that knows how to do:
    * JSON serialization/deserialization
    * log requests in 'curl' format
    * basic API boilerplate for create/delete/list/set/show verbs

    * authentication is handled elsewhere and a token is passed in

    The expectation that there will be a RESTApi object per authentication
    token in use, i.e. project/username/auth_endpoint

    On the other hand, a Client knows details about the specific REST Api that
    it communicates with, such as the available endpoints, API versions, etc.
    """

    def __init__(
        self,
        session=None,
        auth_header=None,
        user_agent=USER_AGENT,
        verify=True,
        logger=None,
        debug=None,
    ):
        """Construct a new REST client

        :param object session: A Session object to be used for
                               communicating with the identity service.
        :param string auth_header: A token from an initialized auth_reference
                                   to be used in the X-Auth-Token header
        :param string user_agent: Set the User-Agent header in the requests
        :param boolean/string verify: If ``True``, the SSL cert will be
                                      verified. A CA_BUNDLE path can also be
                                      provided.
        :param logging.Logger logger: A logger to output to. (optional)
        :param boolean debug: Enables debug logging of all request and
                              responses to identity service.
                              default False (optional)
        """

        self.set_auth(auth_header)
        self.debug = debug

        if not session:
            # We create a default session object
            session = requests.Session()
        self.session = session
        self.session.verify = verify
        self.session.user_agent = user_agent

        if logger:
            self.logger = logger
        else:
            self.logger = _logger

    def set_auth(self, auth_header):
        """Sets the current auth blob"""
        self.auth_header = auth_header

    def set_header(self, header, content):
        """Sets passed in headers into the session headers

        Replaces existing headers!!
        """
        if content is None:
            del self.session.headers[header]
        else:
            self.session.headers[header] = content

    def request(self, method, url, **kwargs):
        """Make an authenticated (if token available) request

        :param method: Request HTTP method
        :param url: Request URL
        :param data: Request body
        :param json: Request body to be encoded as JSON
                     Overwrites ``data`` argument if present
        """

        kwargs.setdefault('headers', {})
        if self.auth_header:
            kwargs['headers']['X-Auth-Token'] = self.auth_header

        if 'json' in kwargs and isinstance(kwargs['json'], type({})):
            kwargs['data'] = json.dumps(kwargs.pop('json'))
            kwargs['headers']['Content-Type'] = 'application/json'

        kwargs.setdefault('allow_redirects', True)

        if self.debug:
            self._log_request(method, url, **kwargs)

        response = self.session.request(method, url, **kwargs)

        if self.debug:
            self._log_response(response)

        return self._error_handler(response)

    def _error_handler(self, response):
        if response.status_code < 200 or response.status_code >= 300:
            self.logger.debug(
                "ERROR: %s",
                response.text,
            )
            response.raise_for_status()
        return response

    # Convenience methods to mimic the ones provided by requests.Session

    def delete(self, url, **kwargs):
        """Send a DELETE request. Returns :class:`requests.Response` object.

        :param url: Request URL
        :param \*\*kwargs: Optional arguments passed to ``request``
        """

        return self.request('DELETE', url, **kwargs)

    def get(self, url, **kwargs):
        """Send a GET request. Returns :class:`requests.Response` object.

        :param url: Request URL
        :param \*\*kwargs: Optional arguments passed to ``request``
        """

        return self.request('GET', url, **kwargs)

    def head(self, url, **kwargs):
        """Send a HEAD request. Returns :class:`requests.Response` object.

        :param url: Request URL
        :param \*\*kwargs: Optional arguments passed to ``request``
        """

        kwargs.setdefault('allow_redirects', False)
        return self.request('HEAD', url, **kwargs)

    def options(self, url, **kwargs):
        """Send an OPTIONS request. Returns :class:`requests.Response` object.

        :param url: Request URL
        :param \*\*kwargs: Optional arguments passed to ``request``
        """

        return self.request('OPTIONS', url, **kwargs)

    def patch(self, url, data=None, json=None, **kwargs):
        """Send a PUT request. Returns :class:`requests.Response` object.

        :param url: Request URL
        :param data: Request body
        :param json: Request body to be encoded as JSON
                     Overwrites ``data`` argument if present
        :param \*\*kwargs: Optional arguments passed to ``request``
        """

        if json:
            kwargs['json'] = json
        if data:
            kwargs['data'] = data
        return self.request('PATCH', url, **kwargs)

    def post(self, url, data=None, json=None, **kwargs):
        """Send a POST request. Returns :class:`requests.Response` object.

        :param url: Request URL
        :param data: Request body
        :param json: Request body to be encoded as JSON
                     Overwrites ``data`` argument if present
        :param \*\*kwargs: Optional arguments passed to ``request``
        """

        if json:
            kwargs['json'] = json
        if data:
            kwargs['data'] = data
        return self.request('POST', url, **kwargs)

    def put(self, url, data=None, json=None, **kwargs):
        """Send a PUT request. Returns :class:`requests.Response` object.

        :param url: Request URL
        :param data: Request body
        :param json: Request body to be encoded as JSON
                     Overwrites ``data`` argument if present
        :param \*\*kwargs: Optional arguments passed to ``request``
        """

        if json:
            kwargs['json'] = json
        if data:
            kwargs['data'] = data
        return self.request('PUT', url, **kwargs)

    # Command verb methods

    def create(self, url, data=None, response_key=None, **kwargs):
        """Create a new object via a POST request

        :param url: Request URL
        :param data: Request body, wil be JSON encoded
        :param response_key: Dict key in response body to extract
        :param \*\*kwargs: Optional arguments passed to ``request``
        """

        response = self.request('POST', url, json=data, **kwargs)
        if response_key:
            return response.json()[response_key]
        else:
            return response.json()

    def list(self, url, data=None, response_key=None, **kwargs):
        """Retrieve a list of objects via a GET or POST request

        :param url: Request URL
        :param data: Request body, will be JSON encoded
        :param response_key: Dict key in response body to extract
        :param \*\*kwargs: Optional arguments passed to ``request``
        """

        if data:
            response = self.request('POST', url, json=data, **kwargs)
        else:
            response = self.request('GET', url, **kwargs)

        if response_key:
            return response.json()[response_key]
        else:
            return response.json()

    def set(self, url, data=None, response_key=None, **kwargs):
        """Update an object via a PUT request

        :param url: Request URL
        :param data: Request body
        :param json: Request body to be encoded as JSON
                     Overwrites ``data`` argument if present
        :param \*\*kwargs: Optional arguments passed to ``request``
        """

        response = self.request('PUT', url, json=data)
        if data:
            if response_key:
                return response.json()[response_key]
            else:
                return response.json()
        else:
            # Nothing to do here
            return None

    def show(self, url, response_key=None, **kwargs):
        """Retrieve a single object via a GET request

        :param url: Request URL
        :param response_key: Dict key in response body to extract
        :param \*\*kwargs: Optional arguments passed to ``request``
        """

        response = self.request('GET', url, **kwargs)
        if response_key:
            return response.json()[response_key]
        else:
            return response.json()

    def _log_request(self, method, url, **kwargs):
        if 'params' in kwargs and kwargs['params'] != {}:
            url += '?' + urlencode(kwargs['params'])

        string_parts = [
            "curl -i",
            "-X '%s'" % method,
            "'%s'" % url,
        ]

        for element in kwargs['headers']:
            header = " -H '%s: %s'" % (element, kwargs['headers'][element])
            string_parts.append(header)

        self.logger.debug("REQ: %s" % " ".join(string_parts))
        if 'data' in kwargs:
            self.logger.debug("  REQ BODY: %r\n" % (kwargs['data']))

    def _log_response(self, response):
        self.logger.debug(
            "RESP: [%s] %r\n",
            response.status_code,
            response.headers,
        )
        if response._content_consumed:
            self.logger.debug(
                "  RESP BODY: %s\n",
                response.text,
            )
        self.logger.debug(
            "  encoding: %s",
            response.encoding,
        )
