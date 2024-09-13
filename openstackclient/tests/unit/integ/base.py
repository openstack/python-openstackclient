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

from keystoneauth1 import fixture as ksa_fixture
from requests_mock.contrib import fixture

from openstackclient.tests.unit import test_shell
from openstackclient.tests.unit import utils


HOST = "192.168.5.41"
URL_BASE = f"http://{HOST}/identity"

V2_AUTH_URL = URL_BASE + "/v2.0/"
V2_VERSION_RESP = {
    "version": {
        "status": "stable",
        "updated": "2014-04-17T00:00:00Z",
        "media-types": [
            {
                "base": "application/json",
                "type": "application/vnd.openstack.identity-v2.0+json",
            },
        ],
        "id": "v2.0",
        "links": [
            {
                "href": V2_AUTH_URL,
                "rel": "self",
            },
            {
                "href": "http://docs.openstack.org/",
                "type": "text/html",
                "rel": "describedby",
            },
        ],
    },
}

V3_AUTH_URL = URL_BASE + "/v3/"
V3_VERSION_RESP = {
    "version": {
        "status": "stable",
        "updated": "2016-04-04T00:00:00Z",
        "media-types": [
            {
                "base": "application/json",
                "type": "application/vnd.openstack.identity-v3+json",
            }
        ],
        "id": "v3.6",
        "links": [
            {
                "href": V3_AUTH_URL,
                "rel": "self",
            }
        ],
    }
}


def make_v2_token(req_mock):
    """Create an Identity v2 token and register the responses"""

    token = ksa_fixture.V2Token(
        tenant_name=test_shell.DEFAULT_PROJECT_NAME,
        user_name=test_shell.DEFAULT_USERNAME,
    )

    # Set up the v2 auth routes
    req_mock.register_uri(
        'GET',
        V2_AUTH_URL,
        json=V2_VERSION_RESP,
        status_code=200,
    )
    req_mock.register_uri(
        'POST',
        V2_AUTH_URL + 'tokens',
        json=token,
        status_code=200,
    )
    return token


def make_v3_token(req_mock):
    """Create an Identity v3 token and register the response"""

    token = ksa_fixture.V3Token(
        # project_domain_id=test_shell.DEFAULT_PROJECT_DOMAIN_ID,
        user_domain_id=test_shell.DEFAULT_USER_DOMAIN_ID,
        user_name=test_shell.DEFAULT_USERNAME,
    )

    # Set up the v3 auth routes
    req_mock.register_uri(
        'GET',
        V3_AUTH_URL,
        json=V3_VERSION_RESP,
        status_code=200,
    )
    req_mock.register_uri(
        'POST',
        V3_AUTH_URL + 'auth/tokens',
        json=token,
        status_code=200,
    )
    return token


class TestInteg(utils.TestCase):
    def setUp(self):
        super().setUp()

        self.requests_mock = self.useFixture(fixture.Fixture())
