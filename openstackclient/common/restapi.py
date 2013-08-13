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
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode


_logger = logging.getLogger(__name__)


class RESTApi(object):
    """A REST api client that handles the interface from us to the server

    RESTApi is an extension of a requests.Session that knows
    how to do:
    * JSON serialization/deserialization
    * log requests in 'curl' format
    * basic API boilerplate for create/delete/list/set/show verbs

    * authentication is handled elsewhere and a token is passed in

    The expectation that there will be a RESTApi object per authentication
    token in use, i.e. project/username/auth_endpoint

    On the other hand, a Client knows details about the specific REST Api that
    it communicates with, such as the available endpoints, API versions, etc.
    """

    USER_AGENT = 'RAPI'

    def __init__(
        self,
        os_auth=None,
        user_agent=USER_AGENT,
        debug=None,
        **kwargs
    ):
        self.set_auth(os_auth)
        self.debug = debug
        self.session = requests.Session(**kwargs)

        self.set_header('User-Agent', user_agent)
        self.set_header('Content-Type', 'application/json')

    def set_auth(self, os_auth):
        """Sets the current auth blob"""
        self.os_auth = os_auth

    def set_header(self, header, content):
        """Sets passed in headers into the session headers

        Replaces existing headers!!
        """
        if content is None:
            del self.session.headers[header]
        else:
            self.session.headers[header] = content

    def request(self, method, url, **kwargs):
        if self.os_auth:
            self.session.headers.setdefault('X-Auth-Token', self.os_auth)
        if 'data' in kwargs and isinstance(kwargs['data'], type({})):
            kwargs['data'] = json.dumps(kwargs['data'])
        log_request(method, url, headers=self.session.headers, **kwargs)
        response = self.session.request(method, url, **kwargs)
        log_response(response)
        return self._error_handler(response)

    def create(self, url, data=None, response_key=None, **kwargs):
        response = self.request('POST', url, data=data, **kwargs)
        if response_key:
            return response.json()[response_key]
        else:
            return response.json()

        #with self.completion_cache('human_id', self.resource_class, mode="a"):
        #    with self.completion_cache('uuid', self.resource_class, mode="a"):
        #        return self.resource_class(self, body[response_key])

    def delete(self, url):
        self.request('DELETE', url)

    def list(self, url, data=None, response_key=None, **kwargs):
        if data:
            response = self.request('POST', url, data=data, **kwargs)
        else:
            kwargs.setdefault('allow_redirects', True)
            response = self.request('GET', url, **kwargs)

        return response.json()[response_key]

        ###hack this for keystone!!!
        #data = body[response_key]
        # NOTE(ja): keystone returns values as list as {'values': [ ... ]}
        #           unlike other services which just return the list...
        #if isinstance(data, dict):
        #    try:
        #        data = data['values']
        #    except KeyError:
        #        pass

        #with self.completion_cache('human_id', obj_class, mode="w"):
        #    with self.completion_cache('uuid', obj_class, mode="w"):
        #        return [obj_class(self, res, loaded=True)
        #                for res in data if res]

    def set(self, url, data=None, response_key=None, **kwargs):
        response = self.request('PUT', url, data=data)
        if data:
            if response_key:
                return response.json()[response_key]
            else:
                return response.json()
        else:
            return None

    def show(self, url, response_key=None, **kwargs):
        response = self.request('GET', url, **kwargs)
        if response_key:
            return response.json()[response_key]
        else:
            return response.json()

    def _error_handler(self, response):
        if response.status_code < 200 or response.status_code >= 300:
            _logger.debug(
                "ERROR: %s",
                response.text,
            )
            response.raise_for_status()
        return response


def log_request(method, url, **kwargs):
    # put in an early exit if debugging is not enabled?
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

    _logger.debug("REQ: %s" % " ".join(string_parts))
    if 'data' in kwargs:
        _logger.debug("REQ BODY: %s\n" % (kwargs['data']))


def log_response(response):
    _logger.debug(
        "RESP: [%s] %s\n",
        response.status_code,
        response.headers,
    )
    if response._content_consumed:
        _logger.debug(
            "RESP BODY: %s\n",
            response.text,
        )
    _logger.debug(
        "encoding: %s",
        response.encoding,
    )
