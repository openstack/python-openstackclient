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

import copy
import mock

from keystoneauth1 import fixture as ksa_fixture
from osc_lib.tests import utils as osc_lib_utils
from requests_mock.contrib import fixture

from openstackclient import shell
from openstackclient.tests import test_shell
from openstackclient.tests import utils

HOST = "192.168.5.41"
URL_BASE = "http://%s/identity" % HOST

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
        "media-types": [{
            "base": "application/json",
            "type": "application/vnd.openstack.identity-v3+json",
        }],
        "id": "v3.6",
        "links": [{
            "href": V3_AUTH_URL,
            "rel": "self",
        }]
    }
}


class TestShellInteg(utils.TestCase):

    def setUp(self):
        super(TestShellInteg, self).setUp()

        self.requests_mock = self.useFixture(fixture.Fixture())


class TestShellCliV2Integ(TestShellInteg):

    def setUp(self):
        super(TestShellCliV2Integ, self).setUp()
        env = {
            "OS_AUTH_URL": V2_AUTH_URL,
            "OS_PROJECT_NAME": test_shell.DEFAULT_PROJECT_NAME,
            "OS_USERNAME": test_shell.DEFAULT_USERNAME,
            "OS_PASSWORD": test_shell.DEFAULT_PASSWORD,
            "OS_IDENTITY_API_VERSION": "2",
        }
        self.useFixture(osc_lib_utils.EnvFixture(copy.deepcopy(env)))

        self.token = ksa_fixture.V2Token(
            tenant_name=test_shell.DEFAULT_PROJECT_NAME,
            user_name=test_shell.DEFAULT_USERNAME,
        )

        # Set up the v2 auth routes
        self.requests_mock.register_uri(
            'GET',
            V2_AUTH_URL,
            json=V2_VERSION_RESP,
            status_code=200,
        )
        self.requests_mock.register_uri(
            'POST',
            V2_AUTH_URL + 'tokens',
            json=self.token,
            status_code=200,
        )

    def test_shell_args_no_options(self):
        _shell = shell.OpenStackShell()
        _shell.run("configuration show".split())

        # Check general calls
        self.assertEqual(len(self.requests_mock.request_history), 2)

        # Check discovery request
        self.assertEqual(
            V2_AUTH_URL,
            self.requests_mock.request_history[0].url,
        )

        # Check auth request
        auth_req = self.requests_mock.request_history[1].json()

        self.assertEqual(
            test_shell.DEFAULT_PROJECT_NAME,
            auth_req['auth']['tenantName'],
        )
        self.assertEqual(
            test_shell.DEFAULT_USERNAME,
            auth_req['auth']['passwordCredentials']['username'],
        )
        self.assertEqual(
            test_shell.DEFAULT_PASSWORD,
            auth_req['auth']['passwordCredentials']['password'],
        )

    def test_shell_args_verify(self):
        _shell = shell.OpenStackShell()
        _shell.run("--verify configuration show".split())

        # Check general calls
        self.assertEqual(len(self.requests_mock.request_history), 2)

        # Check verify
        self.assertTrue(self.requests_mock.request_history[0].verify)

    def test_shell_args_insecure(self):
        _shell = shell.OpenStackShell()
        _shell.run("--insecure configuration show".split())

        # Check general calls
        self.assertEqual(len(self.requests_mock.request_history), 2)

        # Check verify
        self.assertFalse(self.requests_mock.request_history[0].verify)

    def test_shell_args_cacert(self):
        _shell = shell.OpenStackShell()
        _shell.run("--os-cacert xyzpdq configuration show".split())

        # Check general calls
        self.assertEqual(len(self.requests_mock.request_history), 2)

        # Check verify
        self.assertEqual(
            'xyzpdq',
            self.requests_mock.request_history[0].verify,
        )

    def test_shell_args_cacert_insecure(self):
        _shell = shell.OpenStackShell()
        _shell.run("--os-cacert xyzpdq --insecure configuration show".split())

        # Check general calls
        self.assertEqual(len(self.requests_mock.request_history), 2)

        # Check verify
        self.assertFalse(self.requests_mock.request_history[0].verify)


class TestShellCliV2IgnoreInteg(TestShellInteg):

    def setUp(self):
        super(TestShellCliV2IgnoreInteg, self).setUp()
        env = {
            "OS_AUTH_URL": V2_AUTH_URL,
            "OS_PROJECT_NAME": test_shell.DEFAULT_PROJECT_NAME,
            "OS_USERNAME": test_shell.DEFAULT_USERNAME,
            "OS_PASSWORD": test_shell.DEFAULT_PASSWORD,
            "OS_PROJECT_DOMAIN_ID": test_shell.DEFAULT_PROJECT_DOMAIN_ID,
            "OS_USER_DOMAIN_ID": test_shell.DEFAULT_USER_DOMAIN_ID,
            "OS_IDENTITY_API_VERSION": "2",
        }
        self.useFixture(osc_lib_utils.EnvFixture(copy.deepcopy(env)))

        self.token = ksa_fixture.V2Token(
            tenant_name=test_shell.DEFAULT_PROJECT_NAME,
            user_name=test_shell.DEFAULT_USERNAME,
        )

        # Set up the v2 auth routes
        self.requests_mock.register_uri(
            'GET',
            V2_AUTH_URL,
            json=V2_VERSION_RESP,
            status_code=200,
        )
        self.requests_mock.register_uri(
            'POST',
            V2_AUTH_URL + 'tokens',
            json=self.token,
            status_code=200,
        )

    def test_shell_args_ignore_v3(self):
        _shell = shell.OpenStackShell()
        _shell.run("configuration show".split())

        # Check general calls
        self.assertEqual(len(self.requests_mock.request_history), 2)

        # Check discovery request
        self.assertEqual(
            V2_AUTH_URL,
            self.requests_mock.request_history[0].url,
        )

        # Check auth request
        auth_req = self.requests_mock.request_history[1].json()

        self.assertEqual(
            test_shell.DEFAULT_PROJECT_NAME,
            auth_req['auth']['tenantName'],
        )
        self.assertEqual(
            test_shell.DEFAULT_USERNAME,
            auth_req['auth']['passwordCredentials']['username'],
        )
        self.assertEqual(
            test_shell.DEFAULT_PASSWORD,
            auth_req['auth']['passwordCredentials']['password'],
        )


class TestShellCliV3Integ(TestShellInteg):

    def setUp(self):
        super(TestShellCliV3Integ, self).setUp()
        env = {
            "OS_AUTH_URL": V3_AUTH_URL,
            "OS_PROJECT_DOMAIN_ID": test_shell.DEFAULT_PROJECT_DOMAIN_ID,
            "OS_USER_DOMAIN_ID": test_shell.DEFAULT_USER_DOMAIN_ID,
            "OS_USERNAME": test_shell.DEFAULT_USERNAME,
            "OS_PASSWORD": test_shell.DEFAULT_PASSWORD,
            "OS_IDENTITY_API_VERSION": "3",
        }
        self.useFixture(osc_lib_utils.EnvFixture(copy.deepcopy(env)))

        self.token = ksa_fixture.V3Token(
            project_domain_id=test_shell.DEFAULT_PROJECT_DOMAIN_ID,
            user_domain_id=test_shell.DEFAULT_USER_DOMAIN_ID,
            user_name=test_shell.DEFAULT_USERNAME,
        )

        # Set up the v3 auth routes
        self.requests_mock.register_uri(
            'GET',
            V3_AUTH_URL,
            json=V3_VERSION_RESP,
            status_code=200,
        )
        self.requests_mock.register_uri(
            'POST',
            V3_AUTH_URL + 'auth/tokens',
            json=self.token,
            status_code=200,
        )

    def test_shell_args_no_options(self):
        _shell = shell.OpenStackShell()
        _shell.run("configuration show".split())

        # Check general calls
        self.assertEqual(len(self.requests_mock.request_history), 2)

        # Check discovery request
        self.assertEqual(
            V3_AUTH_URL,
            self.requests_mock.request_history[0].url,
        )

        # Check auth request
        auth_req = self.requests_mock.request_history[1].json()

        self.assertEqual(
            test_shell.DEFAULT_PROJECT_DOMAIN_ID,
            auth_req['auth']['identity']['password']['user']['domain']['id'],
        )
        self.assertEqual(
            test_shell.DEFAULT_USERNAME,
            auth_req['auth']['identity']['password']['user']['name'],
        )
        self.assertEqual(
            test_shell.DEFAULT_PASSWORD,
            auth_req['auth']['identity']['password']['user']['password'],
        )

    def test_shell_args_verify(self):
        _shell = shell.OpenStackShell()
        _shell.run("--verify configuration show".split())

        # Check general calls
        self.assertEqual(len(self.requests_mock.request_history), 2)

        # Check verify
        self.assertTrue(self.requests_mock.request_history[0].verify)

    def test_shell_args_insecure(self):
        _shell = shell.OpenStackShell()
        _shell.run("--insecure configuration show".split())

        # Check general calls
        self.assertEqual(len(self.requests_mock.request_history), 2)

        # Check verify
        self.assertFalse(self.requests_mock.request_history[0].verify)

    def test_shell_args_cacert(self):
        _shell = shell.OpenStackShell()
        _shell.run("--os-cacert xyzpdq configuration show".split())

        # Check general calls
        self.assertEqual(len(self.requests_mock.request_history), 2)

        # Check verify
        self.assertEqual(
            'xyzpdq',
            self.requests_mock.request_history[0].verify,
        )

    def test_shell_args_cacert_insecure(self):
        # This test verifies the outcome of bug 1447784
        # https://bugs.launchpad.net/python-openstackclient/+bug/1447784
        _shell = shell.OpenStackShell()
        _shell.run("--os-cacert xyzpdq --insecure configuration show".split())

        # Check general calls
        self.assertEqual(len(self.requests_mock.request_history), 2)

        # Check verify
        self.assertFalse(self.requests_mock.request_history[0].verify)


class TestShellCliPrecedence(TestShellInteg):
    """Validate option precedence rules without clouds.yaml

    Global option values may be set in three places:
    * command line options
    * environment variables
    * clouds.yaml

    Verify that the above order is the precedence used,
    i.e. a command line option overrides all others, etc
    """

    def setUp(self):
        super(TestShellCliPrecedence, self).setUp()
        env = {
            "OS_AUTH_URL": V3_AUTH_URL,
            "OS_PROJECT_DOMAIN_ID": test_shell.DEFAULT_PROJECT_DOMAIN_ID,
            "OS_USER_DOMAIN_ID": test_shell.DEFAULT_USER_DOMAIN_ID,
            "OS_USERNAME": test_shell.DEFAULT_USERNAME,
            "OS_IDENTITY_API_VERSION": "3",
        }
        self.useFixture(osc_lib_utils.EnvFixture(copy.deepcopy(env)))

        self.token = ksa_fixture.V3Token(
            project_domain_id=test_shell.DEFAULT_PROJECT_DOMAIN_ID,
            user_domain_id=test_shell.DEFAULT_USER_DOMAIN_ID,
            user_name=test_shell.DEFAULT_USERNAME,
        )

        # Set up the v3 auth routes
        self.requests_mock.register_uri(
            'GET',
            V3_AUTH_URL,
            json=V3_VERSION_RESP,
            status_code=200,
        )
        self.requests_mock.register_uri(
            'POST',
            V3_AUTH_URL + 'auth/tokens',
            json=self.token,
            status_code=200,
        )

        # Patch a v3 auth URL into the o-c-c data
        test_shell.PUBLIC_1['public-clouds']['megadodo']['auth']['auth_url'] \
            = V3_AUTH_URL

    def test_shell_args_options(self):
        """Verify command line options override environment variables"""

        _shell = shell.OpenStackShell()
        _shell.run(
            "--os-username zarquon --os-password qaz "
            "configuration show".split(),
        )

        # Check general calls
        self.assertEqual(len(self.requests_mock.request_history), 2)

        # Check discovery request
        self.assertEqual(
            V3_AUTH_URL,
            self.requests_mock.request_history[0].url,
        )

        # Check auth request
        auth_req = self.requests_mock.request_history[1].json()

        # -env, -cli
        # No test, everything not specified tests this

        # -env, +cli
        self.assertEqual(
            'qaz',
            auth_req['auth']['identity']['password']['user']['password'],
        )

        # +env, -cli
        self.assertEqual(
            test_shell.DEFAULT_PROJECT_DOMAIN_ID,
            auth_req['auth']['identity']['password']['user']['domain']['id'],
        )

        # +env, +cli
        self.assertEqual(
            'zarquon',
            auth_req['auth']['identity']['password']['user']['name'],
        )


class TestShellCliPrecedenceOCC(TestShellInteg):
    """Validate option precedence rules with clouds.yaml

    Global option values may be set in three places:
    * command line options
    * environment variables
    * clouds.yaml

    Verify that the above order is the precedence used,
    i.e. a command line option overrides all others, etc
    """

    def setUp(self):
        super(TestShellCliPrecedenceOCC, self).setUp()
        env = {
            "OS_CLOUD": "megacloud",
            "OS_AUTH_URL": V3_AUTH_URL,
            "OS_PROJECT_DOMAIN_ID": test_shell.DEFAULT_PROJECT_DOMAIN_ID,
            "OS_USER_DOMAIN_ID": test_shell.DEFAULT_USER_DOMAIN_ID,
            "OS_USERNAME": test_shell.DEFAULT_USERNAME,
            "OS_IDENTITY_API_VERSION": "3",
            "OS_CLOUD_NAME": "qaz",
        }
        self.useFixture(osc_lib_utils.EnvFixture(copy.deepcopy(env)))

        self.token = ksa_fixture.V3Token(
            project_domain_id=test_shell.DEFAULT_PROJECT_DOMAIN_ID,
            user_domain_id=test_shell.DEFAULT_USER_DOMAIN_ID,
            user_name=test_shell.DEFAULT_USERNAME,
        )

        # Set up the v3 auth routes
        self.requests_mock.register_uri(
            'GET',
            V3_AUTH_URL,
            json=V3_VERSION_RESP,
            status_code=200,
        )
        self.requests_mock.register_uri(
            'POST',
            V3_AUTH_URL + 'auth/tokens',
            json=self.token,
            status_code=200,
        )

        # Patch a v3 auth URL into the o-c-c data
        test_shell.PUBLIC_1['public-clouds']['megadodo']['auth']['auth_url'] \
            = V3_AUTH_URL

    @mock.patch("os_client_config.config.OpenStackConfig._load_vendor_file")
    @mock.patch("os_client_config.config.OpenStackConfig._load_config_file")
    def test_shell_args_precedence_1(self, config_mock, vendor_mock):
        """Precedence run 1

        Run 1 has --os-password on CLI
        """

        config_mock.return_value = (
            'file.yaml',
            copy.deepcopy(test_shell.CLOUD_2),
        )
        vendor_mock.return_value = (
            'file.yaml',
            copy.deepcopy(test_shell.PUBLIC_1),
        )
        _shell = shell.OpenStackShell()
        _shell.run(
            "--os-password qaz configuration show".split(),
        )

        # Check general calls
        self.assertEqual(len(self.requests_mock.request_history), 2)

        # Check discovery request
        self.assertEqual(
            V3_AUTH_URL,
            self.requests_mock.request_history[0].url,
        )

        # Check auth request
        auth_req = self.requests_mock.request_history[1].json()

        # -env, -cli, -occ
        # No test, everything not specified tests this

        # -env, -cli, +occ
        self.assertEqual(
            "heart-o-gold",
            auth_req['auth']['scope']['project']['name'],
        )

        # -env, +cli, -occ
        self.assertEqual(
            'qaz',
            auth_req['auth']['identity']['password']['user']['password'],
        )

        # -env, +cli, +occ

        # +env, -cli, -occ
        self.assertEqual(
            test_shell.DEFAULT_USER_DOMAIN_ID,
            auth_req['auth']['identity']['password']['user']['domain']['id'],
        )

        # +env, -cli, +occ
        print("auth_req: %s" % auth_req['auth'])
        self.assertEqual(
            test_shell.DEFAULT_USERNAME,
            auth_req['auth']['identity']['password']['user']['name'],
        )

        # +env, +cli, -occ
        # see test_shell_args_precedence_2()

        # +env, +cli, +occ
        # see test_shell_args_precedence_2()

    @mock.patch("os_client_config.config.OpenStackConfig._load_vendor_file")
    @mock.patch("os_client_config.config.OpenStackConfig._load_config_file")
    def test_shell_args_precedence_2(self, config_mock, vendor_mock):
        """Precedence run 2

        Run 2 has --os-username, --os-password, --os-project-domain-id on CLI
        """

        config_mock.return_value = (
            'file.yaml',
            copy.deepcopy(test_shell.CLOUD_2),
        )
        vendor_mock.return_value = (
            'file.yaml',
            copy.deepcopy(test_shell.PUBLIC_1),
        )
        _shell = shell.OpenStackShell()
        _shell.run(
            "--os-username zarquon --os-password qaz "
            "--os-project-domain-id 5678 configuration show".split(),
        )

        # Check general calls
        self.assertEqual(len(self.requests_mock.request_history), 2)

        # Check discovery request
        self.assertEqual(
            V3_AUTH_URL,
            self.requests_mock.request_history[0].url,
        )

        # Check auth request
        auth_req = self.requests_mock.request_history[1].json()

        # +env, +cli, -occ
        self.assertEqual(
            '5678',
            auth_req['auth']['scope']['project']['domain']['id'],
        )

        # +env, +cli, +occ
        print("auth_req: %s" % auth_req['auth'])
        self.assertEqual(
            'zarquon',
            auth_req['auth']['identity']['password']['user']['name'],
        )
