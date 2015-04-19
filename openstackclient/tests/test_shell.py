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
            self.assertEqual(
                default_args.get("auth_url", ''),
                _shell.options.auth_url,
            )
            self.assertEqual(
                default_args.get("project_id", ''),
                _shell.options.project_id,
            )
            self.assertEqual(
                default_args.get("project_name", ''),
                _shell.options.project_name,
            )
            self.assertEqual(
                default_args.get("domain_id", ''),
                _shell.options.domain_id,
            )
            self.assertEqual(
                default_args.get("domain_name", ''),
                _shell.options.domain_name,
            )
            self.assertEqual(
                default_args.get("user_domain_id", ''),
                _shell.options.user_domain_id,
            )
            self.assertEqual(
                default_args.get("user_domain_name", ''),
                _shell.options.user_domain_name,
            )
            self.assertEqual(
                default_args.get("project_domain_id", ''),
                _shell.options.project_domain_id,
            )
            self.assertEqual(
                default_args.get("project_domain_name", ''),
                _shell.options.project_domain_name,
            )
            self.assertEqual(
                default_args.get("username", ''),
                _shell.options.username,
            )
            self.assertEqual(
                default_args.get("password", ''),
                _shell.options.password,
            )
            self.assertEqual(
                default_args.get("region_name", ''),
                _shell.options.region_name,
            )
            self.assertEqual(
                default_args.get("trust_id", ''),
                _shell.options.trust_id,
            )
            self.assertEqual(
                default_args.get('auth_type', ''),
                _shell.options.auth_type,
            )

    def _assert_token_auth(self, cmd_options, default_args):
        with mock.patch("openstackclient.shell.OpenStackShell.initialize_app",
                        self.app):
            _shell, _cmd = make_shell(), cmd_options + " list role"
            fake_execute(_shell, _cmd)

            self.app.assert_called_with(["list", "role"])
            self.assertEqual(
                default_args.get("token", ''),
                _shell.options.token,
                "token"
            )
            self.assertEqual(
                default_args.get("auth_url", ''),
                _shell.options.auth_url,
                "auth_url"
            )

    def _assert_token_endpoint_auth(self, cmd_options, default_args):
        with mock.patch("openstackclient.shell.OpenStackShell.initialize_app",
                        self.app):
            _shell, _cmd = make_shell(), cmd_options + " list role"
            fake_execute(_shell, _cmd)

            self.app.assert_called_with(["list", "role"])
            self.assertEqual(
                default_args.get("token", ''),
                _shell.options.token,
                "token",
            )
            self.assertEqual(
                default_args.get("url", ''),
                _shell.options.url,
                "url",
            )

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
        }
        self._assert_password_auth(flag, kwargs)

    def test_only_project_id_flow(self):
        flag = "--os-project-id " + DEFAULT_PROJECT_ID
        kwargs = {
            "project_id": DEFAULT_PROJECT_ID,
        }
        self._assert_password_auth(flag, kwargs)

    def test_only_project_name_flow(self):
        flag = "--os-project-name " + DEFAULT_PROJECT_NAME
        kwargs = {
            "project_name": DEFAULT_PROJECT_NAME,
        }
        self._assert_password_auth(flag, kwargs)

    def test_only_domain_id_flow(self):
        flag = "--os-domain-id " + DEFAULT_DOMAIN_ID
        kwargs = {
            "domain_id": DEFAULT_DOMAIN_ID,
        }
        self._assert_password_auth(flag, kwargs)

    def test_only_domain_name_flow(self):
        flag = "--os-domain-name " + DEFAULT_DOMAIN_NAME
        kwargs = {
            "domain_name": DEFAULT_DOMAIN_NAME,
        }
        self._assert_password_auth(flag, kwargs)

    def test_only_user_domain_id_flow(self):
        flag = "--os-user-domain-id " + DEFAULT_USER_DOMAIN_ID
        kwargs = {
            "user_domain_id": DEFAULT_USER_DOMAIN_ID,
        }
        self._assert_password_auth(flag, kwargs)

    def test_only_user_domain_name_flow(self):
        flag = "--os-user-domain-name " + DEFAULT_USER_DOMAIN_NAME
        kwargs = {
            "user_domain_name": DEFAULT_USER_DOMAIN_NAME,
        }
        self._assert_password_auth(flag, kwargs)

    def test_only_project_domain_id_flow(self):
        flag = "--os-project-domain-id " + DEFAULT_PROJECT_DOMAIN_ID
        kwargs = {
            "project_domain_id": DEFAULT_PROJECT_DOMAIN_ID,
        }
        self._assert_password_auth(flag, kwargs)

    def test_only_project_domain_name_flow(self):
        flag = "--os-project-domain-name " + DEFAULT_PROJECT_DOMAIN_NAME
        kwargs = {
            "project_domain_name": DEFAULT_PROJECT_DOMAIN_NAME,
        }
        self._assert_password_auth(flag, kwargs)

    def test_only_username_flow(self):
        flag = "--os-username " + DEFAULT_USERNAME
        kwargs = {
            "username": DEFAULT_USERNAME,
        }
        self._assert_password_auth(flag, kwargs)

    def test_only_password_flow(self):
        flag = "--os-password " + DEFAULT_PASSWORD
        kwargs = {
            "password": DEFAULT_PASSWORD,
        }
        self._assert_password_auth(flag, kwargs)

    def test_only_region_name_flow(self):
        flag = "--os-region-name " + DEFAULT_REGION_NAME
        kwargs = {
            "region_name": DEFAULT_REGION_NAME,
        }
        self._assert_password_auth(flag, kwargs)

    def test_only_trust_id_flow(self):
        flag = "--os-trust-id " + "1234"
        kwargs = {
            "trust_id": "1234",
        }
        self._assert_password_auth(flag, kwargs)

    def test_only_auth_type_flow(self):
        flag = "--os-auth-type " + "v2password"
        kwargs = {
            "auth_type": DEFAULT_AUTH_PLUGIN
        }
        self._assert_password_auth(flag, kwargs)


class TestShellTokenAuth(TestShell):
    def test_only_token(self):
        flag = "--os-token " + DEFAULT_TOKEN
        kwargs = {
            "token": DEFAULT_TOKEN,
            "auth_url": '',
        }
        self._assert_token_auth(flag, kwargs)

    def test_only_auth_url(self):
        flag = "--os-auth-url " + DEFAULT_AUTH_URL
        kwargs = {
            "token": '',
            "auth_url": DEFAULT_AUTH_URL,
        }
        self._assert_token_auth(flag, kwargs)

    def test_empty_auth(self):
        os.environ = {}
        flag = ""
        kwargs = {}
        self._assert_token_auth(flag, kwargs)


class TestShellTokenAuthEnv(TestShell):
    def setUp(self):
        super(TestShellTokenAuthEnv, self).setUp()
        env = {
            "OS_TOKEN": DEFAULT_TOKEN,
            "OS_AUTH_URL": DEFAULT_AUTH_URL,
        }
        self.orig_env, os.environ = os.environ, env.copy()

    def tearDown(self):
        super(TestShellTokenAuthEnv, self).tearDown()
        os.environ = self.orig_env

    def test_env(self):
        flag = ""
        kwargs = {
            "token": DEFAULT_TOKEN,
            "auth_url": DEFAULT_AUTH_URL,
        }
        self._assert_token_auth(flag, kwargs)

    def test_only_token(self):
        flag = "--os-token xyzpdq"
        kwargs = {
            "token": "xyzpdq",
            "auth_url": DEFAULT_AUTH_URL,
        }
        self._assert_token_auth(flag, kwargs)

    def test_only_auth_url(self):
        flag = "--os-auth-url http://cloud.local:555"
        kwargs = {
            "token": DEFAULT_TOKEN,
            "auth_url": "http://cloud.local:555",
        }
        self._assert_token_auth(flag, kwargs)

    def test_empty_auth(self):
        os.environ = {}
        flag = ""
        kwargs = {
            "token": '',
            "auth_url": '',
        }
        self._assert_token_auth(flag, kwargs)


class TestShellTokenEndpointAuth(TestShell):
    def test_only_token(self):
        flag = "--os-token " + DEFAULT_TOKEN
        kwargs = {
            "token": DEFAULT_TOKEN,
            "url": '',
        }
        self._assert_token_endpoint_auth(flag, kwargs)

    def test_only_url(self):
        flag = "--os-url " + DEFAULT_SERVICE_URL
        kwargs = {
            "token": '',
            "url": DEFAULT_SERVICE_URL,
        }
        self._assert_token_endpoint_auth(flag, kwargs)

    def test_empty_auth(self):
        os.environ = {}
        flag = ""
        kwargs = {
            "token": '',
            "auth_url": '',
        }
        self._assert_token_endpoint_auth(flag, kwargs)


class TestShellTokenEndpointAuthEnv(TestShell):
    def setUp(self):
        super(TestShellTokenEndpointAuthEnv, self).setUp()
        env = {
            "OS_TOKEN": DEFAULT_TOKEN,
            "OS_URL": DEFAULT_SERVICE_URL,
        }
        self.orig_env, os.environ = os.environ, env.copy()

    def tearDown(self):
        super(TestShellTokenEndpointAuthEnv, self).tearDown()
        os.environ = self.orig_env

    def test_env(self):
        flag = ""
        kwargs = {
            "token": DEFAULT_TOKEN,
            "url": DEFAULT_SERVICE_URL,
        }
        self._assert_token_auth(flag, kwargs)

    def test_only_token(self):
        flag = "--os-token xyzpdq"
        kwargs = {
            "token": "xyzpdq",
            "url": DEFAULT_SERVICE_URL,
        }
        self._assert_token_auth(flag, kwargs)

    def test_only_url(self):
        flag = "--os-url http://cloud.local:555"
        kwargs = {
            "token": DEFAULT_TOKEN,
            "url": "http://cloud.local:555",
        }
        self._assert_token_auth(flag, kwargs)

    def test_empty_auth(self):
        os.environ = {}
        flag = ""
        kwargs = {
            "token": '',
            "url": '',
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
