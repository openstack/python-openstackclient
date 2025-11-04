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

# TODO(stephenfin): Remove the contents of this module in favour of the osc_lib
# version once our min version is bumped to 4.3.0

import json
from unittest import mock

from keystoneauth1 import fixture
from osc_lib.tests.fakes import (
    FakeApp,
    FakeClientManager as BaseFakeClientManager,
    FakeLog,
    FakeOptions,
    FakeResource as BaseFakeResource,
    FakeStdout,
)
import requests

__all__ = [
    'AUTH_TOKEN',
    'AUTH_URL',
    'INTERFACE',
    'PASSWORD',
    'PROJECT_NAME',
    'REGION_NAME',
    'TEST_RESPONSE_DICT',
    'TEST_RESPONSE_DICT_V3',
    'TEST_VERSIONS',
    'USERNAME',
    'VERSION',
    'FakeApp',
    'FakeClientManager',
    'FakeLog',
    'FakeOptions',
    'FakeResource',
    'FakeResponse',
    'FakeStdout',
]

AUTH_TOKEN = "foobar"
AUTH_URL = "http://0.0.0.0"
USERNAME = "itchy"
PASSWORD = "scratchy"
PROJECT_NAME = "poochie"
REGION_NAME = "richie"
INTERFACE = "catchy"
VERSION = "3"

TEST_RESPONSE_DICT = fixture.V2Token(token_id=AUTH_TOKEN, user_name=USERNAME)
_s = TEST_RESPONSE_DICT.add_service('identity', name='keystone')
_s.add_endpoint(AUTH_URL + ':5000/v2.0')
_s = TEST_RESPONSE_DICT.add_service('network', name='neutron')
_s.add_endpoint(AUTH_URL + ':9696')
_s = TEST_RESPONSE_DICT.add_service('compute', name='nova')
_s.add_endpoint(AUTH_URL + ':8774/v2.1')
_s = TEST_RESPONSE_DICT.add_service('image', name='glance')
_s.add_endpoint(AUTH_URL + ':9292')
_s = TEST_RESPONSE_DICT.add_service('object', name='swift')
_s.add_endpoint(AUTH_URL + ':8080/v1')

TEST_RESPONSE_DICT_V3 = fixture.V3Token(user_name=USERNAME)
TEST_RESPONSE_DICT_V3.set_project_scope()

TEST_VERSIONS = fixture.DiscoveryList(href=AUTH_URL)


class FakeClientManager(BaseFakeClientManager):
    _api_version = {
        'image': '2',
    }

    def __init__(self):
        super().__init__()

        self.sdk_connection = mock.Mock()

        self.network_endpoint_enabled = True
        self.compute_endpoint_enabled = True
        self.volume_endpoint_enabled = True

        # The source of configuration. This is either 'cloud_config' (a
        # clouds.yaml file) or 'global_env' ('OS_'-prefixed envvars)
        self.configuration_type = 'cloud_config'

    def get_configuration(self):
        config = {
            'region': REGION_NAME,
            'identity_api_version': VERSION,
        }

        if self.configuration_type == 'cloud_config':
            config['auth'] = {
                'username': USERNAME,
                'password': PASSWORD,
                'token': AUTH_TOKEN,
            }
        elif self.configuration_type == 'global_env':
            config['username'] = USERNAME
            config['password'] = PASSWORD
            config['token'] = AUTH_TOKEN

        return config

    def is_network_endpoint_enabled(self):
        return self.network_endpoint_enabled

    def is_compute_endpoint_enabled(self):
        return self.compute_endpoint_enabled

    def is_volume_endpoint_enabled(self, client=None):
        return self.volume_endpoint_enabled


class FakeResource(BaseFakeResource):
    def to_dict(self):
        return self._info

    @property
    def info(self):
        return self._info

    def __getitem__(self, item):
        return self._info.get(item)

    def get(self, item, default=None):
        return self._info.get(item, default)

    def pop(self, key, default_value=None):
        return self.info.pop(key, default_value)


class FakeResponse(requests.Response):
    def __init__(
        self, headers=None, status_code=200, data=None, encoding=None
    ):
        super().__init__()

        headers = headers or {}

        self.status_code = status_code

        self.headers.update(headers)
        self._content = json.dumps(data)
        if not isinstance(self._content, bytes):
            self._content = self._content.encode()
