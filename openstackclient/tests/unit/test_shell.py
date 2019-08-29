#   Copyright 2012-2013 OpenStack Foundation
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

import os
import sys

import mock
from osc_lib.tests import utils as osc_lib_test_utils
from oslo_utils import importutils
import wrapt

from openstackclient import shell


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
    '--os-profile': ('SECRET_KEY', True, False),
    '--os-interface': (DEFAULT_INTERFACE, True, True)
}


def get_cloud(log_file):
    CLOUD = {
        'clouds': {
            'megacloud': {
                'cloud': 'megadodo',
                'auth': {
                    'project_name': 'heart-o-gold',
                    'username': 'zaphod',
                },
                'region_name': 'occ-cloud,krikkit,occ-env',
                'log_file': log_file,
                'log_level': 'debug',
                'cert': 'mycert',
                'key': 'mickey',
            }
        }
    }
    return CLOUD


# Wrap the osc_lib make_shell() function to set the shell class since
# osc-lib's TestShell class doesn't allow us to specify it yet.
# TODO(dtroyer): remove this once the shell_class_patch patch is released
#                in osc-lib
def make_shell_wrapper(func, inst, args, kwargs):
    if 'shell_class' not in kwargs:
        kwargs['shell_class'] = shell.OpenStackShell
    return func(*args, **kwargs)


wrapt.wrap_function_wrapper(
    osc_lib_test_utils,
    'make_shell',
    make_shell_wrapper,
)


class TestShell(osc_lib_test_utils.TestShell):

    # Full name of the OpenStackShell class to test (cliff.app.App subclass)
    shell_class_name = "openstackclient.shell.OpenStackShell"

    # TODO(dtroyer): remove this once the shell_class_patch patch is released
    #                in osc-lib
    app_patch = shell_class_name

    def setUp(self):
        super(TestShell, self).setUp()
        # TODO(dtroyer): remove this once the shell_class_patch patch is
        #                released in osc-lib
        self.shell_class = importutils.import_class(self.shell_class_name)

    def _assert_admin_token_auth(self, cmd_options, default_args):
        with mock.patch(
                self.shell_class_name + ".initialize_app",
                self.app,
        ):
            _shell = osc_lib_test_utils.make_shell(
                shell_class=self.shell_class,
            )
            _cmd = cmd_options + " list role"
            osc_lib_test_utils.fake_execute(_shell, _cmd)
            print("_shell: %s" % _shell)

            self.app.assert_called_with(["list", "role"])
            self.assertEqual(
                default_args.get("token", ''),
                _shell.options.token,
                "token",
            )
            self.assertEqual(
                default_args.get("endpoint", ''),
                _shell.options.endpoint,
                "endpoint",
            )

    def _assert_token_auth(self, cmd_options, default_args):
        with mock.patch(
                self.app_patch + ".initialize_app",
                self.app,
        ):
            _shell = osc_lib_test_utils.make_shell(
                shell_class=self.shell_class,
            )
            _cmd = cmd_options + " list role"
            osc_lib_test_utils.fake_execute(_shell, _cmd)
            print("_shell: %s" % _shell)

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

    def _assert_cli(self, cmd_options, default_args):
        with mock.patch(
                self.shell_class_name + ".initialize_app",
                self.app,
        ):
            _shell = osc_lib_test_utils.make_shell(
                shell_class=self.shell_class,
            )
            _cmd = cmd_options + " list server"
            osc_lib_test_utils.fake_execute(_shell, _cmd)

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


class TestShellOptions(TestShell):

    def setUp(self):
        super(TestShellOptions, self).setUp()
        self.useFixture(osc_lib_test_utils.EnvFixture())

    def _test_options_init_app(self, test_opts):
        for opt in test_opts.keys():
            if not test_opts[opt][1]:
                continue
            key = osc_lib_test_utils.opt2attr(opt)
            if isinstance(test_opts[opt][0], str):
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
            key = osc_lib_test_utils.opt2attr(opt)
            if isinstance(test_opts[opt][0], str):
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
            key = osc_lib_test_utils.opt2attr(opt)
            kwargs = {
                key: test_opts[opt][0],
            }
            env = {
                osc_lib_test_utils.opt2env(opt): test_opts[opt][0],
            }
            os.environ = env.copy()
            self._assert_initialize_app_arg("", kwargs)

    def _test_env_get_one_cloud(self, test_opts):
        for opt in test_opts.keys():
            if not test_opts[opt][2]:
                continue
            key = osc_lib_test_utils.opt2attr(opt)
            kwargs = {
                key: test_opts[opt][0],
            }
            env = {
                osc_lib_test_utils.opt2env(opt): test_opts[opt][0],
            }
            os.environ = env.copy()
            self._assert_cloud_config_arg("", kwargs)


class TestShellTokenAuthEnv(TestShell):

    def setUp(self):
        super(TestShellTokenAuthEnv, self).setUp()
        env = {
            "OS_TOKEN": DEFAULT_TOKEN,
            "OS_AUTH_URL": DEFAULT_AUTH_URL,
        }
        self.useFixture(osc_lib_test_utils.EnvFixture(env.copy()))

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
            "OS_ENDPOINT": DEFAULT_SERVICE_URL,
        }
        self.useFixture(osc_lib_test_utils.EnvFixture(env.copy()))

    def test_env(self):
        flag = ""
        kwargs = {
            "token": DEFAULT_TOKEN,
            "endpoint": DEFAULT_SERVICE_URL,
        }
        self._assert_admin_token_auth(flag, kwargs)

    def test_only_token(self):
        flag = "--os-token xyzpdq"
        kwargs = {
            "token": "xyzpdq",
            "endpoint": DEFAULT_SERVICE_URL,
        }
        self._assert_token_auth(flag, kwargs)

    def test_only_url(self):
        flag = "--os-endpoint http://cloud.local:555"
        kwargs = {
            "token": DEFAULT_TOKEN,
            "endpoint": "http://cloud.local:555",
        }
        self._assert_token_auth(flag, kwargs)

    def test_empty_auth(self):
        os.environ = {}
        flag = ""
        kwargs = {
            "token": '',
            "endpoint": '',
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
        self.useFixture(osc_lib_test_utils.EnvFixture(env.copy()))

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


class TestShellArgV(TestShell):
    """Test the deferred help flag"""

    def test_shell_argv(self):
        """Test argv decoding

        Python 2 does nothing with argv while Python 3 decodes it into
        Unicode before we ever see it.  We manually decode when running
        under Python 2 so verify that we get the right argv types.

        Use the argv supplied by the test runner so we get actual Python
        runtime behaviour; we only need to check the type of argv[0]
        which will always be present.
        """

        with mock.patch(
                self.shell_class_name + ".run",
                self.app,
        ):
            # Ensure type gets through unmolested through shell.main()
            argv = sys.argv
            shell.main(sys.argv)
            self.assertEqual(type(argv[0]), type(self.app.call_args[0][0][0]))

            # When shell.main() gets sys.argv itself it should be decoded
            shell.main()
            self.assertEqual(type(u'x'), type(self.app.call_args[0][0][0]))
