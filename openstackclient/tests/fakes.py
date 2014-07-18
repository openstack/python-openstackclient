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

import json
import six
import sys

import requests


AUTH_TOKEN = "foobar"
AUTH_URL = "http://0.0.0.0"
USERNAME = "itchy"
PASSWORD = "scratchy"
TEST_RESPONSE_DICT = {
    "access": {
        "metadata": {
            "is_admin": 0,
            "roles": [
                "1234",
            ]
        },
        "serviceCatalog": [
            {
                "endpoints": [
                    {
                        "adminURL": AUTH_URL + "/v2.0",
                        "id": "1234",
                        "internalURL": AUTH_URL + "/v2.0",
                        "publicURL": AUTH_URL + "/v2.0",
                        "region": "RegionOne"
                    }
                ],
                "endpoints_links": [],
                "name": "keystone",
                "type": "identity"
            }
        ],
        "token": {
            "expires": "2035-01-01T00:00:01Z",
            "id": AUTH_TOKEN,
            "issued_at": "2013-01-01T00:00:01.692048",
            "tenant": {
                "description": None,
                "enabled": True,
                "id": "1234",
                "name": "testtenant"
            }
        },
        "user": {
            "id": "5678",
            "name": USERNAME,
            "roles": [
                {
                    "name": "testrole"
                },
            ],
            "roles_links": [],
            "username": USERNAME
        }
    }
}
TEST_RESPONSE_DICT_V3 = {
    "token": {
        "audit_ids": [
            "a"
        ],
        "catalog": [
        ],
        "expires_at": "2034-09-29T18:27:15.978064Z",
        "extras": {},
        "issued_at": "2014-09-29T17:27:15.978097Z",
        "methods": [
            "password"
        ],
        "project": {
            "domain": {
                "id": "default",
                "name": "Default"
            },
            "id": "bbb",
            "name": "project"
        },
        "roles": [
        ],
        "user": {
            "domain": {
                "id": "default",
                "name": "Default"
            },
            "id": "aaa",
            "name": USERNAME
        }
    }
}
TEST_VERSIONS = {
    "versions": {
        "values": [
            {
                "id": "v3.0",
                "links": [
                    {
                        "href": AUTH_URL,
                        "rel": "self"
                    }
                ],
                "media-types": [
                    {
                        "base": "application/json",
                        "type": "application/vnd.openstack.identity-v3+json"
                    },
                    {
                        "base": "application/xml",
                        "type": "application/vnd.openstack.identity-v3+xml"
                    }
                ],
                "status": "stable",
                "updated": "2013-03-06T00:00:00Z"
            },
            {
                "id": "v2.0",
                "links": [
                    {
                        "href": AUTH_URL,
                        "rel": "self"
                    },
                    {
                        "href": "http://docs.openstack.org/",
                        "rel": "describedby",
                        "type": "text/html"
                    }
                ],
                "media-types": [
                    {
                        "base": "application/json",
                        "type": "application/vnd.openstack.identity-v2.0+json"
                    },
                    {
                        "base": "application/xml",
                        "type": "application/vnd.openstack.identity-v2.0+xml"
                    }
                ],
                "status": "stable",
                "updated": "2014-04-17T00:00:00Z"
            }
        ]
    }
}


class FakeStdout:
    def __init__(self):
        self.content = []

    def write(self, text):
        self.content.append(text)

    def make_string(self):
        result = ''
        for line in self.content:
            result = result + line
        return result


class FakeApp(object):
    def __init__(self, _stdout):
        self.stdout = _stdout
        self.client_manager = None
        self.stdin = sys.stdin
        self.stdout = _stdout or sys.stdout
        self.stderr = sys.stderr


class FakeClient(object):
    def __init__(self, **kwargs):
        self.endpoint = kwargs['endpoint']
        self.token = kwargs['token']


class FakeClientManager(object):
    def __init__(self):
        self.compute = None
        self.identity = None
        self.image = None
        self.object_store = None
        self.volume = None
        self.network = None
        self.session = None
        self.auth_ref = None


class FakeModule(object):
    def __init__(self, name, version):
        self.name = name
        self.__version__ = version


class FakeResource(object):
    def __init__(self, manager, info, loaded=False):
        self.manager = manager
        self._info = info
        self._add_details(info)
        self._loaded = loaded

    def _add_details(self, info):
        for (k, v) in six.iteritems(info):
            setattr(self, k, v)

    def __repr__(self):
        reprkeys = sorted(k for k in self.__dict__.keys() if k[0] != '_' and
                          k != 'manager')
        info = ", ".join("%s=%s" % (k, getattr(self, k)) for k in reprkeys)
        return "<%s %s>" % (self.__class__.__name__, info)


class FakeResponse(requests.Response):
    def __init__(self, headers={}, status_code=200, data=None, encoding=None):
        super(FakeResponse, self).__init__()

        self.status_code = status_code

        self.headers.update(headers)
        self._content = json.dumps(data)
        if not isinstance(self._content, six.binary_type):
            self._content = self._content.encode()
