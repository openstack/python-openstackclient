#   Copyright 2012-2013 OpenStack, LLC.
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

import mock
import os

from openstackclient import shell
from openstackclient.tests import utils


DEFAULT_AUTH_URL = "http://127.0.0.1:5000/v2.0/"
DEFAULT_PROJECT_ID = "xxxx-yyyy-zzzz"
DEFAULT_PROJECT_NAME = "project"
DEFAULT_DOMAIN_ID = "aaaa-bbbb-cccc"
DEFAULT_DOMAIN_NAME = "domain"
DEFAULT_USER_DOMAIN_ID = "aaaa-bbbb-cccc"
DEFAULT_USER_DOMAIN_NAME = "domain"
DEFAULT_PROJECT_DOMAIN_ID = "aaaa-bbbb-cccc"
DEFAULT_PROJECT_DOMAIN_NAME = "domain"
DEFAULT_USERNAME = "username"
DEFAULT_PASSWORD = "password"
DEFAULT_REGION_NAME = "ZZ9_Plural_Z_Alpha"
DEFAULT_TOKEN = "token"
DEFAULT_SERVICE_URL = "http://127.0.0.1:8771/v3.0/"
DEFAULT_AUTH_PLUGIN = "v2password"


DEFAULT_COMPUTE_API_VERSION = "2"
DEFAULT_IDENTITY_API_VERSION = "2"
DEFAULT_IMAGE_API_VERSION = "2"
DEFAULT_VOLUME_API_VERSION = "1"
DEFAULT_NETWORK_API_VERSION = "2"

LIB_COMPUTE_API_VERSION = "2"
LIB_IDENTITY_API_VERSION = "2"
LIB_IMAGE_API_VERSION = "1"
LIB_VOLUME_API_VERSION = "1"
LIB_NETWORK_API_VERSION = "2"


def make_shell():
    """Create a new command shell and mock out some bits."""
    _shell = shell.OpenStackShell()
    _shell.command_manager = mock.Mock()

    return _shell


def fake_execute(shell, cmd):
    """Pretend to execute shell commands."""
    return shell.run(cmd.split())


class TestShell(utils.TestCase):
    def setUp(self):
        super(TestShell, self).setUp()
        patch = "openstackclient.shell.OpenStackShell.run_subcommand"
        self.cmd_patch = mock.patch(patch)
        self.cmd_save = self.cmd_patch.start()
        self.app = mock.Mock("Test Shell")

    def tearDown(self):
        super(TestShell, self).tearDown()
        self.cmd_patch.stop()

    def _assert_password_auth(self, cmd_options, default_args):
        with mock.patch("openstackclient.shell.OpenStackShell.initialize_app",
                        self.app):
            _shell, _cmd = make_shell(), cmd_options + " list project"
            fake_execute(_shell, _cmd)

            self.app.assert_called_with(["list", "project"])
            self.assertEqual(default_args["auth_url"],
                             _shell.options.os_auth_url)
            self.assertEqual(default_args["project_id"],
                             _shell.options.os_project_id)
            self.assertEqual(default_args["project_name"],
                             _shell.options.os_project_name)
            self.assertEqual(default_args["domain_id"],
                             _shell.options.os_domain_id)
            self.assertEqual(default_args["domain_name"],
                             _shell.options.os_domain_name)
            self.assertEqual(default_args["user_domain_id"],
                             _shell.options.os_user_domain_id)
            self.assertEqual(default_args["user_domain_name"],
                             _shell.options.os_user_domain_name)
            self.assertEqual(default_args["project_domain_id"],
                             _shell.options.os_project_domain_id)
            self.assertEqual(default_args["project_domain_name"],
                             _shell.options.os_project_domain_name)
            self.assertEqual(default_args["username"],
                             _shell.options.os_username)
            self.assertEqual(default_args["password"],
                             _shell.options.os_password)
            self.assertEqual(default_args["region_name"],
                             _shell.options.os_region_name)
            self.assertEqual(default_args["trust_id"],
                             _shell.options.os_trust_id)
            self.assertEqual(default_args['auth_type'],
                             _shell.options.os_auth_type)

    def _assert_token_auth(self, cmd_options, default_args):
        with mock.patch("openstackclient.shell.OpenStackShell.initialize_app",
                        self.app):
            _shell, _cmd = make_shell(), cmd_options + " list role"
            fake_execute(_shell, _cmd)

            self.app.assert_called_with(["list", "role"])
            self.assertEqual(default_args["os_token"], _shell.options.os_token)
            self.assertEqual(default_args["os_auth_url"],
                             _shell.options.os_auth_url)

    def _assert_cli(self, cmd_options, default_args):
        with mock.patch("openstackclient.shell.OpenStackShell.initialize_app",
                        self.app):
            _shell, _cmd = make_shell(), cmd_options + " list server"
            fake_execute(_shell, _cmd)

            self.app.assert_called_with(["list", "server"])
            self.assertEqual(default_args["compute_api_version"],
                             _shell.options.os_compute_api_version)
            self.assertEqual(default_args["identity_api_version"],
                             _shell.options.os_identity_api_version)
            self.assertEqual(default_args["image_api_version"],
                             _shell.options.os_image_api_version)
            self.assertEqual(default_args["volume_api_version"],
                             _shell.options.os_volume_api_version)
            self.assertEqual(default_args["network_api_version"],
                             _shell.options.os_network_api_version)


class TestShellHelp(TestShell):
    """Test the deferred help flag"""
    def setUp(self):
        super(TestShellHelp, self).setUp()
        self.orig_env, os.environ = os.environ, {}

    def tearDown(self):
        super(TestShellHelp, self).tearDown()
        os.environ = self.orig_env

    def test_help_options(self):
        flag = "-h list server"
        kwargs = {
            "deferred_help": True,
        }
        with mock.patch("openstackclient.shell.OpenStackShell.initialize_app",
                        self.app):
            _shell, _cmd = make_shell(), flag
            fake_execute(_shell, _cmd)

            self.assertEqual(kwargs["deferred_help"],
                             _shell.options.deferred_help)


class TestShellPasswordAuth(TestShell):
    def setUp(self):
        super(TestShellPasswordAuth, self).setUp()
        self.orig_env, os.environ = os.environ, {}

    def tearDown(self):
        super(TestShellPasswordAuth, self).tearDown()
        os.environ = self.orig_env

    def test_only_url_flow(self):
        flag = "--os-auth-url " + DEFAULT_AUTH_URL
        kwargs = {
            "auth_url": DEFAULT_AUTH_URL,
            "project_id": "",
            "project_name": "",
            "user_domain_id": "",
            "domain_id": "",
            "domain_name": "",
            "user_domain_name": "",
            "project_domain_id": "",
            "project_domain_name": "",
            "username": "",
            "password": "",
            "region_name": "",
            "trust_id": "",
            "auth_type": "",
        }
        self._assert_password_auth(flag, kwargs)

    def test_only_project_id_flow(self):
        flag = "--os-project-id " + DEFAULT_PROJECT_ID
        kwargs = {
            "auth_url": "",
            "project_id": DEFAULT_PROJECT_ID,
            "project_name": "",
            "domain_id": "",
            "domain_name": "",
            "user_domain_id": "",
            "user_domain_name": "",
            "project_domain_id": "",
            "project_domain_name": "",
            "username": "",
            "password": "",
            "region_name": "",
            "trust_id": "",
            "auth_type": "",
        }
        self._assert_password_auth(flag, kwargs)

    def test_only_project_name_flow(self):
        flag = "--os-project-name " + DEFAULT_PROJECT_NAME
        kwargs = {
            "auth_url": "",
            "project_id": "",
            "project_name": DEFAULT_PROJECT_NAME,
            "domain_id": "",
            "domain_name": "",
            "user_domain_id": "",
            "user_domain_name": "",
            "project_domain_id": "",
            "project_domain_name": "",
            "username": "",
            "password": "",
            "region_name": "",
            "trust_id": "",
            "auth_type": "",
        }
        self._assert_password_auth(flag, kwargs)

    def test_only_domain_id_flow(self):
        flag = "--os-domain-id " + DEFAULT_DOMAIN_ID
        kwargs = {
            "auth_url": "",
            "project_id": "",
            "project_name": "",
            "domain_id": DEFAULT_DOMAIN_ID,
            "domain_name": "",
            "user_domain_id": "",
            "user_domain_name": "",
            "project_domain_id": "",
            "project_domain_name": "",
            "username": "",
            "password": "",
            "region_name": "",
            "trust_id": "",
            "auth_type": "",
        }
        self._assert_password_auth(flag, kwargs)

    def test_only_domain_name_flow(self):
        flag = "--os-domain-name " + DEFAULT_DOMAIN_NAME
        kwargs = {
            "auth_url": "",
            "project_id": "",
            "project_name": "",
            "domain_id": "",
            "domain_name": DEFAULT_DOMAIN_NAME,
            "user_domain_id": "",
            "user_domain_name": "",
            "project_domain_id": "",
            "project_domain_name": "",
            "username": "",
            "password": "",
            "region_name": "",
            "trust_id": "",
            "auth_type": "",
        }
        self._assert_password_auth(flag, kwargs)

    def test_only_user_domain_id_flow(self):
        flag = "--os-user-domain-id " + DEFAULT_USER_DOMAIN_ID
        kwargs = {
            "auth_url": "",
            "project_id": "",
            "project_name": "",
            "domain_id": "",
            "domain_name": "",
            "user_domain_id": DEFAULT_USER_DOMAIN_ID,
            "user_domain_name": "",
            "project_domain_id": "",
            "project_domain_name": "",
            "username": "",
            "password": "",
            "region_name": "",
            "trust_id": "",
            "auth_type": "",
        }
        self._assert_password_auth(flag, kwargs)

    def test_only_user_domain_name_flow(self):
        flag = "--os-user-domain-name " + DEFAULT_USER_DOMAIN_NAME
        kwargs = {
            "auth_url": "",
            "project_id": "",
            "project_name": "",
            "domain_id": "",
            "domain_name": "",
            "user_domain_id": "",
            "user_domain_name": DEFAULT_USER_DOMAIN_NAME,
            "project_domain_id": "",
            "project_domain_name": "",
            "username": "",
            "password": "",
            "region_name": "",
            "trust_id": "",
            "auth_type": "",
        }
        self._assert_password_auth(flag, kwargs)

    def test_only_project_domain_id_flow(self):
        flag = "--os-project-domain-id " + DEFAULT_PROJECT_DOMAIN_ID
        kwargs = {
            "auth_url": "",
            "project_id": "",
            "project_name": "",
            "domain_id": "",
            "domain_name": "",
            "user_domain_id": "",
            "user_domain_name": "",
            "project_domain_id": DEFAULT_PROJECT_DOMAIN_ID,
            "project_domain_name": "",
            "username": "",
            "password": "",
            "region_name": "",
            "trust_id": "",
            "auth_type": "",
        }
        self._assert_password_auth(flag, kwargs)

    def test_only_project_domain_name_flow(self):
        flag = "--os-project-domain-name " + DEFAULT_PROJECT_DOMAIN_NAME
        kwargs = {
            "auth_url": "",
            "project_id": "",
            "project_name": "",
            "domain_id": "",
            "domain_name": "",
            "user_domain_id": "",
            "user_domain_name": "",
            "project_domain_id": "",
            "project_domain_name": DEFAULT_PROJECT_DOMAIN_NAME,
            "username": "",
            "password": "",
            "region_name": "",
            "trust_id": "",
            "auth_type": "",
        }
        self._assert_password_auth(flag, kwargs)

    def test_only_username_flow(self):
        flag = "--os-username " + DEFAULT_USERNAME
        kwargs = {
            "auth_url": "",
            "project_id": "",
            "project_name": "",
            "domain_id": "",
            "domain_name": "",
            "user_domain_id": "",
            "user_domain_name": "",
            "project_domain_id": "",
            "project_domain_name": "",
            "username": DEFAULT_USERNAME,
            "password": "",
            "region_name": "",
            "trust_id": "",
            "auth_type": "",
        }
        self._assert_password_auth(flag, kwargs)

    def test_only_password_flow(self):
        flag = "--os-password " + DEFAULT_PASSWORD
        kwargs = {
            "auth_url": "",
            "project_id": "",
            "project_name": "",
            "domain_id": "",
            "domain_name": "",
            "user_domain_id": "",
            "user_domain_name": "",
            "project_domain_id": "",
            "project_domain_name": "",
            "username": "",
            "password": DEFAULT_PASSWORD,
            "region_name": "",
            "trust_id": "",
            "auth_type": "",
        }
        self._assert_password_auth(flag, kwargs)

    def test_only_region_name_flow(self):
        flag = "--os-region-name " + DEFAULT_REGION_NAME
        kwargs = {
            "auth_url": "",
            "project_id": "",
            "project_name": "",
            "domain_id": "",
            "domain_name": "",
            "user_domain_id": "",
            "user_domain_name": "",
            "project_domain_id": "",
            "project_domain_name": "",
            "username": "",
            "password": "",
            "region_name": DEFAULT_REGION_NAME,
            "trust_id": "",
            "auth_type": "",
        }
        self._assert_password_auth(flag, kwargs)

    def test_only_trust_id_flow(self):
        flag = "--os-trust-id " + "1234"
        kwargs = {
            "auth_url": "",
            "project_id": "",
            "project_name": "",
            "domain_id": "",
            "domain_name": "",
            "user_domain_id": "",
            "user_domain_name": "",
            "project_domain_id": "",
            "project_domain_name": "",
            "username": "",
            "password": "",
            "region_name": "",
            "trust_id": "1234",
            "auth_type": "",
        }
        self._assert_password_auth(flag, kwargs)

    def test_only_auth_type_flow(self):
        flag = "--os-auth-type " + "v2password"
        kwargs = {
            "auth_url": "",
            "project_id": "",
            "project_name": "",
            "domain_id": "",
            "domain_name": "",
            "user_domain_id": "",
            "user_domain_name": "",
            "project_domain_id": "",
            "project_domain_name": "",
            "username": "",
            "password": "",
            "region_name": "",
            "trust_id": "",
            "auth_type": DEFAULT_AUTH_PLUGIN
        }
        self._assert_password_auth(flag, kwargs)


class TestShellTokenAuth(TestShell):
    def setUp(self):
        super(TestShellTokenAuth, self).setUp()
        env = {
            "OS_TOKEN": DEFAULT_TOKEN,
            "OS_AUTH_URL": DEFAULT_SERVICE_URL,
        }
        self.orig_env, os.environ = os.environ, env.copy()

    def tearDown(self):
        super(TestShellTokenAuth, self).tearDown()
        os.environ = self.orig_env

    def test_default_auth(self):
        flag = ""
        kwargs = {
            "os_token": DEFAULT_TOKEN,
            "os_auth_url": DEFAULT_SERVICE_URL
        }
        self._assert_token_auth(flag, kwargs)

    def test_empty_auth(self):
        os.environ = {}
        flag = ""
        kwargs = {
            "os_token": "",
            "os_auth_url": ""
        }
        self._assert_token_auth(flag, kwargs)


class TestShellCli(TestShell):
    def setUp(self):
        super(TestShellCli, self).setUp()
        env = {
            "OS_COMPUTE_API_VERSION": DEFAULT_COMPUTE_API_VERSION,
            "OS_IDENTITY_API_VERSION": DEFAULT_IDENTITY_API_VERSION,
            "OS_IMAGE_API_VERSION": DEFAULT_IMAGE_API_VERSION,
            "OS_VOLUME_API_VERSION": DEFAULT_VOLUME_API_VERSION,
            "OS_NETWORK_API_VERSION": DEFAULT_NETWORK_API_VERSION,
        }
        self.orig_env, os.environ = os.environ, env.copy()

    def tearDown(self):
        super(TestShellCli, self).tearDown()
        os.environ = self.orig_env

    def test_shell_args(self):
        _shell = make_shell()
        with mock.patch("openstackclient.shell.OpenStackShell.initialize_app",
                        self.app):
            fake_execute(_shell, "list user")
            self.app.assert_called_with(["list", "user"])

    def test_default_env(self):
        flag = ""
        kwargs = {
            "compute_api_version": DEFAULT_COMPUTE_API_VERSION,
            "identity_api_version": DEFAULT_IDENTITY_API_VERSION,
            "image_api_version": DEFAULT_IMAGE_API_VERSION,
            "volume_api_version": DEFAULT_VOLUME_API_VERSION,
            "network_api_version": DEFAULT_NETWORK_API_VERSION,
        }
        self._assert_cli(flag, kwargs)

    def test_empty_env(self):
        os.environ = {}
        flag = ""
        kwargs = {
            "compute_api_version": LIB_COMPUTE_API_VERSION,
            "identity_api_version": LIB_IDENTITY_API_VERSION,
            "image_api_version": LIB_IMAGE_API_VERSION,
            "volume_api_version": LIB_VOLUME_API_VERSION,
            "network_api_version": LIB_NETWORK_API_VERSION
        }
        self._assert_cli(flag, kwargs)
