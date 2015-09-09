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

import copy
import mock
import os
import testtools

from openstackclient import shell
from openstackclient.tests import utils


DEFAULT_AUTH_URL = "http://127.0.0.1:5000/v2.0/"
DEFAULT_PROJECT_ID = "xxxx-yyyy-zzzz"
DEFAULT_PROJECT_NAME = "project"
DEFAULT_DOMAIN_ID = "aaaa-bbbb-cccc"
DEFAULT_DOMAIN_NAME = "default"
DEFAULT_USER_DOMAIN_ID = "aaaa-bbbb-cccc"
DEFAULT_USER_DOMAIN_NAME = "domain"
DEFAULT_PROJECT_DOMAIN_ID = "aaaa-bbbb-cccc"
DEFAULT_PROJECT_DOMAIN_NAME = "domain"
DEFAULT_USERNAME = "username"
DEFAULT_PASSWORD = "password"

DEFAULT_CLOUD = "altocumulus"
DEFAULT_REGION_NAME = "ZZ9_Plural_Z_Alpha"
DEFAULT_TOKEN = "token"
DEFAULT_SERVICE_URL = "http://127.0.0.1:8771/v3.0/"
DEFAULT_AUTH_PLUGIN = "v2password"
DEFAULT_INTERFACE = "internal"

DEFAULT_COMPUTE_API_VERSION = ""
DEFAULT_IDENTITY_API_VERSION = ""
DEFAULT_IMAGE_API_VERSION = ""
DEFAULT_VOLUME_API_VERSION = ""
DEFAULT_NETWORK_API_VERSION = ""

LIB_COMPUTE_API_VERSION = ""
LIB_IDENTITY_API_VERSION = ""
LIB_IMAGE_API_VERSION = ""
LIB_VOLUME_API_VERSION = ""
LIB_NETWORK_API_VERSION = ""

CLOUD_1 = {
    'clouds': {
        'scc': {
            'auth': {
                'auth_url': DEFAULT_AUTH_URL,
                'project_name': DEFAULT_PROJECT_NAME,
                'username': 'zaphod',
            },
            'region_name': 'occ-cloud',
            'donut': 'glazed',
            'interface': 'public',
        }
    }
}

CLOUD_2 = {
    'clouds': {
        'megacloud': {
            'cloud': 'megadodo',
            'auth': {
                'project_name': 'heart-o-gold',
                'username': 'zaphod',
            },
            'region_name': 'occ-cloud',
            'log_file': '/tmp/test_log_file',
            'log_level': 'debug',
        }
    }
}

PUBLIC_1 = {
    'public-clouds': {
        'megadodo': {
            'auth': {
                'auth_url': DEFAULT_AUTH_URL,
                'project_name': DEFAULT_PROJECT_NAME,
            },
            'region_name': 'occ-public',
            'donut': 'cake',
        }
    }
}


# The option table values is a tuple of (<value>, <test-opt>, <test-env>)
# where <value> is the test value to use, <test-opt> is True if this option
# should be tested as a CLI option and <test-env> is True of this option
# should be tested as an environment variable.

# Global options that should be parsed before shell.initialize_app() is called
global_options = {
    '--os-cloud': (DEFAULT_CLOUD, True, True),
    '--os-region-name': (DEFAULT_REGION_NAME, True, True),
    '--os-default-domain': (DEFAULT_DOMAIN_NAME, True, True),
    '--os-cacert': ('/dev/null', True, True),
    '--timing': (True, True, False),
    '--os-interface': (DEFAULT_INTERFACE, True, True)
}

auth_options = {
    '--os-auth-url': (DEFAULT_AUTH_URL, True, True),
    '--os-project-id': (DEFAULT_PROJECT_ID, True, True),
    '--os-project-name': (DEFAULT_PROJECT_NAME, True, True),
    '--os-domain-id': (DEFAULT_DOMAIN_ID, True, True),
    '--os-domain-name': (DEFAULT_DOMAIN_NAME, True, True),
    '--os-user-domain-id': (DEFAULT_USER_DOMAIN_ID, True, True),
    '--os-user-domain-name': (DEFAULT_USER_DOMAIN_NAME, True, True),
    '--os-project-domain-id': (DEFAULT_PROJECT_DOMAIN_ID, True, True),
    '--os-project-domain-name': (DEFAULT_PROJECT_DOMAIN_NAME, True, True),
    '--os-username': (DEFAULT_USERNAME, True, True),
    '--os-password': (DEFAULT_PASSWORD, True, True),
    '--os-region-name': (DEFAULT_REGION_NAME, True, True),
    '--os-trust-id': ("1234", True, True),
    '--os-auth-type': ("v2password", True, True),
    '--os-token': (DEFAULT_TOKEN, True, True),
    '--os-url': (DEFAULT_SERVICE_URL, True, True),
    '--os-interface': (DEFAULT_INTERFACE, True, True),
}


def opt2attr(opt):
    if opt.startswith('--os-'):
        attr = opt[5:]
    elif opt.startswith('--'):
        attr = opt[2:]
    else:
        attr = opt
    return attr.lower().replace('-', '_')


def opt2env(opt):
    return opt[2:].upper().replace('-', '_')


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

    def _assert_initialize_app_arg(self, cmd_options, default_args):
        """Check the args passed to initialize_app()

        The argv argument to initialize_app() is the remainder from parsing
        global options declared in both cliff.app and
        openstackclient.OpenStackShell build_option_parser().  Any global
        options passed on the commmad line should not be in argv but in
        _shell.options.
        """

        with mock.patch(
                "openstackclient.shell.OpenStackShell.initialize_app",
                self.app,
        ):
            _shell, _cmd = make_shell(), cmd_options + " list project"
            fake_execute(_shell, _cmd)

            self.app.assert_called_with(["list", "project"])
            for k in default_args.keys():
                self.assertEqual(
                    default_args[k],
                    vars(_shell.options)[k],
                    "%s does not match" % k,
                )

    def _assert_cloud_config_arg(self, cmd_options, default_args):
        """Check the args passed to cloud_config.get_one_cloud()

        The argparse argument to get_one_cloud() is an argparse.Namespace
        object that contains all of the options processed to this point in
        initialize_app().
        """

        cloud = mock.Mock(name="cloudy")
        cloud.config = {}
        self.occ_get_one = mock.Mock(return_value=cloud)
        with mock.patch(
                "os_client_config.config.OpenStackConfig.get_one_cloud",
                self.occ_get_one,
        ):
            _shell, _cmd = make_shell(), cmd_options + " list project"
            fake_execute(_shell, _cmd)

            opts = self.occ_get_one.call_args[1]['argparse']
            for k in default_args.keys():
                self.assertEqual(
                    default_args[k],
                    vars(opts)[k],
                    "%s does not match" % k,
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

    @testtools.skip("skip until bug 1444983 is resolved")
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


class TestShellOptions(TestShell):
    def setUp(self):
        super(TestShellOptions, self).setUp()
        self.orig_env, os.environ = os.environ, {}

    def tearDown(self):
        super(TestShellOptions, self).tearDown()
        os.environ = self.orig_env

    def _test_options_init_app(self, test_opts):
        for opt in test_opts.keys():
            if not test_opts[opt][1]:
                continue
            key = opt2attr(opt)
            if type(test_opts[opt][0]) is str:
                cmd = opt + " " + test_opts[opt][0]
            else:
                cmd = opt
            kwargs = {
                key: test_opts[opt][0],
            }
            self._assert_initialize_app_arg(cmd, kwargs)

    def _test_options_get_one_cloud(self, test_opts):
        for opt in test_opts.keys():
            if not test_opts[opt][1]:
                continue
            key = opt2attr(opt)
            if type(test_opts[opt][0]) is str:
                cmd = opt + " " + test_opts[opt][0]
            else:
                cmd = opt
            kwargs = {
                key: test_opts[opt][0],
            }
            self._assert_cloud_config_arg(cmd, kwargs)

    def _test_env_init_app(self, test_opts):
        for opt in test_opts.keys():
            if not test_opts[opt][2]:
                continue
            key = opt2attr(opt)
            kwargs = {
                key: test_opts[opt][0],
            }
            env = {
                opt2env(opt): test_opts[opt][0],
            }
            os.environ = env.copy()
            self._assert_initialize_app_arg("", kwargs)

    def _test_env_get_one_cloud(self, test_opts):
        for opt in test_opts.keys():
            if not test_opts[opt][2]:
                continue
            key = opt2attr(opt)
            kwargs = {
                key: test_opts[opt][0],
            }
            env = {
                opt2env(opt): test_opts[opt][0],
            }
            os.environ = env.copy()
            self._assert_cloud_config_arg("", kwargs)

    def test_empty_auth(self):
        os.environ = {}
        self._assert_initialize_app_arg("", {})
        self._assert_cloud_config_arg("", {})

    def test_global_options(self):
        self._test_options_init_app(global_options)
        self._test_options_get_one_cloud(global_options)

    def test_auth_options(self):
        self._test_options_init_app(auth_options)
        self._test_options_get_one_cloud(auth_options)

    def test_global_env(self):
        self._test_env_init_app(global_options)
        self._test_env_get_one_cloud(global_options)

    def test_auth_env(self):
        self._test_env_init_app(auth_options)
        self._test_env_get_one_cloud(auth_options)


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

    def test_shell_args_no_options(self):
        _shell = make_shell()
        with mock.patch("openstackclient.shell.OpenStackShell.initialize_app",
                        self.app):
            fake_execute(_shell, "list user")
            self.app.assert_called_with(["list", "user"])

    def test_shell_args_ca_options(self):
        _shell = make_shell()

        # NOTE(dtroyer): The commented out asserts below are the desired
        #                behaviour and will be uncommented when the
        #                handling for --verify and --insecure is fixed.

        # Default
        fake_execute(_shell, "list user")
        self.assertIsNone(_shell.options.verify)
        self.assertIsNone(_shell.options.insecure)
        self.assertEqual('', _shell.options.cacert)
        self.assertTrue(_shell.verify)

        # --verify
        fake_execute(_shell, "--verify list user")
        self.assertTrue(_shell.options.verify)
        self.assertIsNone(_shell.options.insecure)
        self.assertEqual('', _shell.options.cacert)
        self.assertTrue(_shell.verify)

        # --insecure
        fake_execute(_shell, "--insecure list user")
        self.assertIsNone(_shell.options.verify)
        self.assertTrue(_shell.options.insecure)
        self.assertEqual('', _shell.options.cacert)
        self.assertFalse(_shell.verify)

        # --os-cacert
        fake_execute(_shell, "--os-cacert foo list user")
        self.assertIsNone(_shell.options.verify)
        self.assertIsNone(_shell.options.insecure)
        self.assertEqual('foo', _shell.options.cacert)
        self.assertTrue(_shell.verify)

        # --os-cacert and --verify
        fake_execute(_shell, "--os-cacert foo --verify list user")
        self.assertTrue(_shell.options.verify)
        self.assertIsNone(_shell.options.insecure)
        self.assertEqual('foo', _shell.options.cacert)
        self.assertTrue(_shell.verify)

        # --os-cacert and --insecure
        # NOTE(dtroyer): Per bug https://bugs.launchpad.net/bugs/1447784
        #                in this combination --insecure now overrides any
        #                --os-cacert setting, where before --insecure
        #                was ignored if --os-cacert was set.
        fake_execute(_shell, "--os-cacert foo --insecure list user")
        self.assertIsNone(_shell.options.verify)
        self.assertTrue(_shell.options.insecure)
        self.assertEqual('foo', _shell.options.cacert)
        self.assertFalse(_shell.verify)

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

    @mock.patch("os_client_config.config.OpenStackConfig._load_config_file")
    def test_shell_args_cloud_no_vendor(self, config_mock):
        config_mock.return_value = ('file.yaml', copy.deepcopy(CLOUD_1))
        _shell = make_shell()

        fake_execute(
            _shell,
            "--os-cloud scc list user",
        )
        self.assertEqual(
            'scc',
            _shell.cloud.name,
        )

        # These come from clouds.yaml
        self.assertEqual(
            DEFAULT_AUTH_URL,
            _shell.cloud.config['auth']['auth_url'],
        )
        self.assertEqual(
            DEFAULT_PROJECT_NAME,
            _shell.cloud.config['auth']['project_name'],
        )
        self.assertEqual(
            'zaphod',
            _shell.cloud.config['auth']['username'],
        )
        self.assertEqual(
            'occ-cloud',
            _shell.cloud.config['region_name'],
        )
        self.assertEqual(
            'glazed',
            _shell.cloud.config['donut'],
        )
        self.assertEqual(
            'public',
            _shell.cloud.config['interface'],
        )

    @mock.patch("os_client_config.config.OpenStackConfig._load_vendor_file")
    @mock.patch("os_client_config.config.OpenStackConfig._load_config_file")
    def test_shell_args_cloud_public(self, config_mock, public_mock):
        config_mock.return_value = ('file.yaml', copy.deepcopy(CLOUD_2))
        public_mock.return_value = ('file.yaml', copy.deepcopy(PUBLIC_1))
        _shell = make_shell()

        fake_execute(
            _shell,
            "--os-cloud megacloud list user",
        )
        self.assertEqual(
            'megacloud',
            _shell.cloud.name,
        )

        # These come from clouds-public.yaml
        self.assertEqual(
            DEFAULT_AUTH_URL,
            _shell.cloud.config['auth']['auth_url'],
        )
        self.assertEqual(
            'cake',
            _shell.cloud.config['donut'],
        )

        # These come from clouds.yaml
        self.assertEqual(
            'heart-o-gold',
            _shell.cloud.config['auth']['project_name'],
        )
        self.assertEqual(
            'zaphod',
            _shell.cloud.config['auth']['username'],
        )
        self.assertEqual(
            'occ-cloud',
            _shell.cloud.config['region_name'],
        )

    @mock.patch("os_client_config.config.OpenStackConfig._load_vendor_file")
    @mock.patch("os_client_config.config.OpenStackConfig._load_config_file")
    def test_shell_args_precedence(self, config_mock, vendor_mock):
        config_mock.return_value = ('file.yaml', copy.deepcopy(CLOUD_2))
        vendor_mock.return_value = ('file.yaml', copy.deepcopy(PUBLIC_1))
        _shell = make_shell()

        # Test command option overriding config file value
        fake_execute(
            _shell,
            "--os-cloud megacloud --os-region-name krikkit list user",
        )
        self.assertEqual(
            'megacloud',
            _shell.cloud.name,
        )

        # These come from clouds-public.yaml
        self.assertEqual(
            DEFAULT_AUTH_URL,
            _shell.cloud.config['auth']['auth_url'],
        )
        self.assertEqual(
            'cake',
            _shell.cloud.config['donut'],
        )

        # These come from clouds.yaml
        self.assertEqual(
            'heart-o-gold',
            _shell.cloud.config['auth']['project_name'],
        )
        self.assertEqual(
            'zaphod',
            _shell.cloud.config['auth']['username'],
        )
        self.assertEqual(
            'krikkit',
            _shell.cloud.config['region_name'],
        )


class TestShellCliEnv(TestShell):
    def setUp(self):
        super(TestShellCliEnv, self).setUp()
        env = {
            'OS_REGION_NAME': 'occ-env',
        }
        self.orig_env, os.environ = os.environ, env.copy()

    def tearDown(self):
        super(TestShellCliEnv, self).tearDown()
        os.environ = self.orig_env

    @mock.patch("os_client_config.config.OpenStackConfig._load_vendor_file")
    @mock.patch("os_client_config.config.OpenStackConfig._load_config_file")
    def test_shell_args_precedence_1(self, config_mock, vendor_mock):
        config_mock.return_value = ('file.yaml', copy.deepcopy(CLOUD_2))
        vendor_mock.return_value = ('file.yaml', copy.deepcopy(PUBLIC_1))
        _shell = make_shell()

        # Test env var
        fake_execute(
            _shell,
            "--os-cloud megacloud list user",
        )
        self.assertEqual(
            'megacloud',
            _shell.cloud.name,
        )

        # These come from clouds-public.yaml
        self.assertEqual(
            DEFAULT_AUTH_URL,
            _shell.cloud.config['auth']['auth_url'],
        )
        self.assertEqual(
            'cake',
            _shell.cloud.config['donut'],
        )

        # These come from clouds.yaml
        self.assertEqual(
            'heart-o-gold',
            _shell.cloud.config['auth']['project_name'],
        )
        self.assertEqual(
            'zaphod',
            _shell.cloud.config['auth']['username'],
        )
        self.assertEqual(
            'occ-env',
            _shell.cloud.config['region_name'],
        )

    @mock.patch("os_client_config.config.OpenStackConfig._load_vendor_file")
    @mock.patch("os_client_config.config.OpenStackConfig._load_config_file")
    def test_shell_args_precedence_2(self, config_mock, vendor_mock):
        config_mock.return_value = ('file.yaml', copy.deepcopy(CLOUD_2))
        vendor_mock.return_value = ('file.yaml', copy.deepcopy(PUBLIC_1))
        _shell = make_shell()

        # Test command option overriding config file value
        fake_execute(
            _shell,
            "--os-cloud megacloud --os-region-name krikkit list user",
        )
        self.assertEqual(
            'megacloud',
            _shell.cloud.name,
        )

        # These come from clouds-public.yaml
        self.assertEqual(
            DEFAULT_AUTH_URL,
            _shell.cloud.config['auth']['auth_url'],
        )
        self.assertEqual(
            'cake',
            _shell.cloud.config['donut'],
        )

        # These come from clouds.yaml
        self.assertEqual(
            'heart-o-gold',
            _shell.cloud.config['auth']['project_name'],
        )
        self.assertEqual(
            'zaphod',
            _shell.cloud.config['auth']['username'],
        )

        # These come from the command line
        self.assertEqual(
            'krikkit',
            _shell.cloud.config['region_name'],
        )
