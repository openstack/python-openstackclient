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
from unittest import mock

import fixtures
from osc_lib.tests import utils as osc_lib_utils

from openstackclient import shell
from openstackclient.tests.unit.integ import base as test_base
from openstackclient.tests.unit import test_shell


class TestIntegShellCliNoAuth(test_base.TestInteg):
    def setUp(self):
        super().setUp()
        env = {}
        self.useFixture(osc_lib_utils.EnvFixture(copy.deepcopy(env)))

        # self.token = test_base.make_v2_token(self.requests_mock)

    def test_shell_args_no_options(self):
        _shell = shell.OpenStackShell()
        _shell.run("configuration show".split())

        # Check general calls
        self.assertEqual(len(self.requests_mock.request_history), 0)

    def test_shell_args_verify(self):
        _shell = shell.OpenStackShell()
        _shell.run("--verify configuration show".split())

        # Check general calls
        self.assertEqual(len(self.requests_mock.request_history), 0)

    def test_shell_args_insecure(self):
        _shell = shell.OpenStackShell()
        _shell.run("--insecure configuration show".split())

        # Check general calls
        self.assertEqual(len(self.requests_mock.request_history), 0)

    def test_shell_args_cacert(self):
        _shell = shell.OpenStackShell()
        _shell.run("--os-cacert xyzpdq configuration show".split())

        # Check general calls
        self.assertEqual(len(self.requests_mock.request_history), 0)

    def test_shell_args_cacert_insecure(self):
        _shell = shell.OpenStackShell()
        _shell.run("--os-cacert xyzpdq --insecure configuration show".split())

        # Check general calls
        self.assertEqual(len(self.requests_mock.request_history), 0)


class TestIntegShellCliV2(test_base.TestInteg):
    def setUp(self):
        super().setUp()
        env = {
            "OS_AUTH_URL": test_base.V2_AUTH_URL,
            "OS_PROJECT_NAME": test_shell.DEFAULT_PROJECT_NAME,
            "OS_USERNAME": test_shell.DEFAULT_USERNAME,
            "OS_PASSWORD": test_shell.DEFAULT_PASSWORD,
            "OS_IDENTITY_API_VERSION": "2",
        }
        self.useFixture(osc_lib_utils.EnvFixture(copy.deepcopy(env)))

        self.token = test_base.make_v2_token(self.requests_mock)

    def test_shell_args_no_options(self):
        _shell = shell.OpenStackShell()
        _shell.run("extension list".split())

        # Check general calls
        self.assertNotEqual(len(self.requests_mock.request_history), 0)

        # Check discovery request
        self.assertEqual(
            test_base.V2_AUTH_URL,
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
        _shell.run("--verify extension list".split())

        # Check general calls
        self.assertNotEqual(len(self.requests_mock.request_history), 0)

        # Check verify
        self.assertTrue(self.requests_mock.request_history[0].verify)

    def test_shell_args_insecure(self):
        _shell = shell.OpenStackShell()
        _shell.run("--insecure extension list".split())

        # Check general calls
        self.assertNotEqual(len(self.requests_mock.request_history), 0)

        # Check verify
        self.assertFalse(self.requests_mock.request_history[0].verify)

    def test_shell_args_cacert(self):
        _shell = shell.OpenStackShell()
        _shell.run("--os-cacert xyzpdq extension list".split())

        # Check general calls
        self.assertNotEqual(len(self.requests_mock.request_history), 0)

        # Check verify
        self.assertEqual(
            'xyzpdq',
            self.requests_mock.request_history[0].verify,
        )

    def test_shell_args_cacert_insecure(self):
        _shell = shell.OpenStackShell()
        _shell.run("--os-cacert xyzpdq --insecure extension list".split())

        # Check general calls
        self.assertNotEqual(len(self.requests_mock.request_history), 0)

        # Check verify
        self.assertFalse(self.requests_mock.request_history[0].verify)


class TestIntegShellCliV2Ignore(test_base.TestInteg):
    def setUp(self):
        super().setUp()
        env = {
            "OS_AUTH_URL": test_base.V2_AUTH_URL,
            "OS_PROJECT_NAME": test_shell.DEFAULT_PROJECT_NAME,
            "OS_USERNAME": test_shell.DEFAULT_USERNAME,
            "OS_PASSWORD": test_shell.DEFAULT_PASSWORD,
            "OS_PROJECT_DOMAIN_ID": test_shell.DEFAULT_PROJECT_DOMAIN_ID,
            "OS_USER_DOMAIN_ID": test_shell.DEFAULT_USER_DOMAIN_ID,
            "OS_IDENTITY_API_VERSION": "2",
        }
        self.useFixture(osc_lib_utils.EnvFixture(copy.deepcopy(env)))

        self.token = test_base.make_v2_token(self.requests_mock)

    def test_shell_args_ignore_v3(self):
        _shell = shell.OpenStackShell()
        _shell.run("extension list".split())

        # Check general calls
        self.assertNotEqual(len(self.requests_mock.request_history), 0)

        # Check discovery request
        self.assertEqual(
            test_base.V2_AUTH_URL,
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


class TestIntegShellCliV3(test_base.TestInteg):
    def setUp(self):
        super().setUp()
        env = {
            "OS_AUTH_URL": test_base.V3_AUTH_URL,
            "OS_PROJECT_DOMAIN_ID": test_shell.DEFAULT_PROJECT_DOMAIN_ID,
            "OS_USER_DOMAIN_ID": test_shell.DEFAULT_USER_DOMAIN_ID,
            "OS_USERNAME": test_shell.DEFAULT_USERNAME,
            "OS_PASSWORD": test_shell.DEFAULT_PASSWORD,
            "OS_IDENTITY_API_VERSION": "3",
        }
        self.useFixture(osc_lib_utils.EnvFixture(copy.deepcopy(env)))

        self.token = test_base.make_v3_token(self.requests_mock)

    def test_shell_args_no_options(self):
        _shell = shell.OpenStackShell()
        _shell.run("extension list".split())

        # Check general calls
        self.assertNotEqual(len(self.requests_mock.request_history), 0)

        # Check discovery request
        self.assertEqual(
            test_base.V3_AUTH_URL,
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
        _shell.run("--verify extension list".split())

        # Check general calls
        self.assertNotEqual(len(self.requests_mock.request_history), 0)

        # Check verify
        self.assertTrue(self.requests_mock.request_history[0].verify)

    def test_shell_args_insecure(self):
        _shell = shell.OpenStackShell()
        _shell.run("--insecure extension list".split())

        # Check general calls
        self.assertNotEqual(len(self.requests_mock.request_history), 0)

        # Check verify
        self.assertFalse(self.requests_mock.request_history[0].verify)

    def test_shell_args_cacert(self):
        _shell = shell.OpenStackShell()
        _shell.run("--os-cacert xyzpdq extension list".split())

        # Check general calls
        self.assertNotEqual(len(self.requests_mock.request_history), 0)

        # Check verify
        self.assertEqual(
            'xyzpdq',
            self.requests_mock.request_history[0].verify,
        )

    def test_shell_args_cacert_insecure(self):
        # This test verifies the outcome of bug 1447784
        # https://bugs.launchpad.net/python-openstackclient/+bug/1447784
        _shell = shell.OpenStackShell()
        _shell.run("--os-cacert xyzpdq --insecure extension list".split())

        # Check general calls
        self.assertNotEqual(len(self.requests_mock.request_history), 0)

        # Check verify
        self.assertFalse(self.requests_mock.request_history[0].verify)


class TestIntegShellCliV3Prompt(test_base.TestInteg):
    def setUp(self):
        super().setUp()
        env = {
            "OS_AUTH_URL": test_base.V3_AUTH_URL,
            "OS_PROJECT_DOMAIN_ID": test_shell.DEFAULT_PROJECT_DOMAIN_ID,
            "OS_USER_DOMAIN_ID": test_shell.DEFAULT_USER_DOMAIN_ID,
            "OS_USERNAME": test_shell.DEFAULT_USERNAME,
            "OS_IDENTITY_API_VERSION": "3",
        }
        self.useFixture(osc_lib_utils.EnvFixture(copy.deepcopy(env)))

        self.token = test_base.make_v3_token(self.requests_mock)

    @mock.patch("osc_lib.shell.prompt_for_password")
    def test_shell_callback(self, mock_prompt):
        mock_prompt.return_value = "qaz"
        _shell = shell.OpenStackShell()
        _shell.run("extension list".split())

        # Check general calls
        self.assertNotEqual(len(self.requests_mock.request_history), 0)

        # Check password callback set correctly
        self.assertEqual(
            mock_prompt, _shell.cloud._openstack_config._pw_callback
        )

        # Check auth request
        auth_req = self.requests_mock.request_history[1].json()

        # Check returned password from prompt function
        self.assertEqual(
            "qaz",
            auth_req['auth']['identity']['password']['user']['password'],
        )


class TestIntegShellCliPrecedence(test_base.TestInteg):
    """Validate option precedence rules without clouds.yaml

    Global option values may be set in three places:
    * command line options
    * environment variables
    * clouds.yaml

    Verify that the above order is the precedence used,
    i.e. a command line option overrides all others, etc
    """

    def setUp(self):
        super().setUp()
        env = {
            "OS_AUTH_URL": test_base.V3_AUTH_URL,
            "OS_PROJECT_DOMAIN_ID": test_shell.DEFAULT_PROJECT_DOMAIN_ID,
            "OS_USER_DOMAIN_ID": test_shell.DEFAULT_USER_DOMAIN_ID,
            "OS_USERNAME": test_shell.DEFAULT_USERNAME,
            "OS_IDENTITY_API_VERSION": "3",
        }
        self.useFixture(osc_lib_utils.EnvFixture(copy.deepcopy(env)))

        self.token = test_base.make_v3_token(self.requests_mock)

        # Patch a v3 auth URL into the o-c-c data
        test_shell.PUBLIC_1['public-clouds']['megadodo']['auth'][
            'auth_url'
        ] = test_base.V3_AUTH_URL

    def test_shell_args_options(self):
        """Verify command line options override environment variables"""

        _shell = shell.OpenStackShell()
        _shell.run(
            "--os-username zarquon --os-password qaz extension list".split(),
        )

        # Check general calls
        self.assertNotEqual(len(self.requests_mock.request_history), 0)

        # Check discovery request
        self.assertEqual(
            test_base.V3_AUTH_URL,
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


class TestIntegShellCliPrecedenceOCC(test_base.TestInteg):
    """Validate option precedence rules with clouds.yaml

    Global option values may be set in three places:
    * command line options
    * environment variables
    * clouds.yaml

    Verify that the above order is the precedence used,
    i.e. a command line option overrides all others, etc
    """

    def setUp(self):
        super().setUp()
        env = {
            "OS_CLOUD": "megacloud",
            "OS_AUTH_URL": test_base.V3_AUTH_URL,
            "OS_PROJECT_DOMAIN_ID": test_shell.DEFAULT_PROJECT_DOMAIN_ID,
            "OS_USER_DOMAIN_ID": test_shell.DEFAULT_USER_DOMAIN_ID,
            "OS_USERNAME": test_shell.DEFAULT_USERNAME,
            "OS_IDENTITY_API_VERSION": "3",
            "OS_CLOUD_NAME": "qaz",
        }
        self.useFixture(osc_lib_utils.EnvFixture(copy.deepcopy(env)))

        self.token = test_base.make_v3_token(self.requests_mock)

        # Patch a v3 auth URL into the o-c-c data
        test_shell.PUBLIC_1['public-clouds']['megadodo']['auth'][
            'auth_url'
        ] = test_base.V3_AUTH_URL

    def get_temp_file_path(self, filename):
        """Returns an absolute path for a temporary file.

        :param filename: filename
        :type filename: string
        :returns: absolute file path string
        """
        temp_dir = self.useFixture(fixtures.TempDir())
        return temp_dir.join(filename)

    @mock.patch("openstack.config.loader.OpenStackConfig._load_vendor_file")
    @mock.patch("openstack.config.loader.OpenStackConfig._load_config_file")
    def test_shell_args_precedence_1(self, config_mock, vendor_mock):
        """Precedence run 1

        Run 1 has --os-password on CLI
        """

        def config_mock_return():
            log_file = self.get_temp_file_path('test_log_file')
            cloud2 = test_shell.get_cloud(log_file)
            return ('file.yaml', cloud2)

        config_mock.side_effect = config_mock_return

        def vendor_mock_return():
            return ('file.yaml', copy.deepcopy(test_shell.PUBLIC_1))

        vendor_mock.side_effect = vendor_mock_return

        _shell = shell.OpenStackShell()
        _shell.run(
            "--os-password qaz extension list".split(),
        )

        # Check general calls
        self.assertNotEqual(len(self.requests_mock.request_history), 0)

        # Check discovery request
        self.assertEqual(
            test_base.V3_AUTH_URL,
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
        self.assertEqual(
            test_shell.DEFAULT_USERNAME,
            auth_req['auth']['identity']['password']['user']['name'],
        )

        # +env, +cli, -occ
        # see test_shell_args_precedence_2()

        # +env, +cli, +occ
        # see test_shell_args_precedence_2()

    @mock.patch("openstack.config.loader.OpenStackConfig._load_vendor_file")
    @mock.patch("openstack.config.loader.OpenStackConfig._load_config_file")
    def test_shell_args_precedence_2(self, config_mock, vendor_mock):
        """Precedence run 2

        Run 2 has --os-username, --os-password, --os-project-domain-id on CLI
        """

        def config_mock_return():
            log_file = self.get_temp_file_path('test_log_file')
            cloud2 = test_shell.get_cloud(log_file)
            return ('file.yaml', cloud2)

        config_mock.side_effect = config_mock_return

        def vendor_mock_return():
            return ('file.yaml', copy.deepcopy(test_shell.PUBLIC_1))

        vendor_mock.side_effect = vendor_mock_return

        _shell = shell.OpenStackShell()
        _shell.run(
            "--os-username zarquon --os-password qaz "
            "--os-project-domain-id 5678 extension list".split(),
        )

        # Check general calls
        self.assertNotEqual(len(self.requests_mock.request_history), 0)

        # Check discovery request
        self.assertEqual(
            test_base.V3_AUTH_URL,
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
        self.assertEqual(
            'zarquon',
            auth_req['auth']['identity']['password']['user']['name'],
        )
