# Copyright 2012 OpenStack LLC.
# All Rights Reserved
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#
# vim: tabstop=4 shiftwidth=4 softtabstop=4

import os
import mock

from openstackclient import shell as os_shell
from tests import utils


DEFAULT_AUTH_URL = 'http://127.0.0.1:5000/v2.0/'
DEFAULT_TENANT_ID = 'xxxx-yyyy-zzzz'
DEFAULT_TENANT_NAME = 'joe_tenant'
DEFAULT_USERNAME = 'joe_user'
DEFAULT_PASSWORD = 'password'
DEFAULT_REGION_NAME = 'ZZ9_Plural_Z_Alpha'
DEFAULT_TOKEN = 'xyzpdq'
DEFAULT_SERVICE_URL = 'http://127.0.0.1:8771/v3.0/'

DEFAULT_COMPUTE_API_VERSION = '42'
DEFAULT_IDENTITY_API_VERSION = '42.0'
DEFAULT_IMAGE_API_VERSION = 'v42'

# These values are hard-coded in the client libs
LIB_COMPUTE_API_VERSION = '2'
LIB_IDENTITY_API_VERSION = '2.0'
LIB_IMAGE_API_VERSION = '1.0'


def make_shell():
    """Create a new command shell and mock out some bits"""
    _shell = os_shell.OpenStackShell()
    _shell.command_manager = mock.Mock()
    return _shell


class ShellTest(utils.TestCase):

    def setUp(self):
        """ Patch os.environ to avoid required auth info"""
        global _old_env
        fake_env = {
            'OS_AUTH_URL': DEFAULT_AUTH_URL,
            'OS_TENANT_ID': DEFAULT_TENANT_ID,
            'OS_TENANT_NAME': DEFAULT_TENANT_NAME,
            'OS_USERNAME': DEFAULT_USERNAME,
            'OS_PASSWORD': DEFAULT_PASSWORD,
            'OS_REGION_NAME': DEFAULT_REGION_NAME,
        }
        _old_env, os.environ = os.environ, fake_env.copy()

        # Make a fake shell object, a helping wrapper to call it, and a quick
        # way of asserting that certain API calls were made.
        global shell, _shell, assert_called, assert_called_anytime
        shell = lambda sh,cmd: sh.run(cmd.split())

        # Patch out some common methods
        #self.auth_patch = mock.patch(
        #    'openstackclient.shell.OpenStackShell.authenticate_user')
        #self.auth_save = self.auth_patch.start()
        self.cmd_patch = mock.patch(
            'openstackclient.shell.OpenStackShell.run_subcommand')
        self.cmd_save = self.cmd_patch.start()

    def tearDown(self):
        global _old_env
        os.environ = _old_env
        #self.auth_patch.stop()
        self.cmd_patch.stop()

    def test_shell_args(self):
        sh = make_shell()
        initapp_mock = mock.Mock('default environment')
        with mock.patch(
            'openstackclient.shell.OpenStackShell.initialize_app',
            initapp_mock):
                shell(sh, 'list user')
                initapp_mock.assert_called_with((['list', 'user']))

    def test_shell_auth_password_flow(self):

        def test_auth(desc, cmd_options, default_args):
            initapp_mock = mock.Mock(desc)
            with mock.patch(
                'openstackclient.shell.OpenStackShell.initialize_app',
                initapp_mock):
                    cmd = cmd_options + ' list tenant'
                    shell(sh, cmd)
                    initapp_mock.assert_called_with(['list', 'tenant'])
                    assert sh.options.os_auth_url == default_args['auth_url']
                    assert sh.options.os_tenant_id == \
                        default_args['tenant_id']
                    assert sh.options.os_tenant_name == \
                        default_args['tenant_name']
                    assert sh.options.os_username == default_args['username']
                    assert sh.options.os_password == default_args['password']
                    assert sh.options.os_region_name == \
                        default_args['region_name']

        # Test the default
        sh = make_shell()
        test_auth('default environment', '',
            {'auth_url': DEFAULT_AUTH_URL,
            'tenant_id': DEFAULT_TENANT_ID,
            'tenant_name': DEFAULT_TENANT_NAME,
            'username': DEFAULT_USERNAME,
            'password': DEFAULT_PASSWORD,
            'region_name': DEFAULT_REGION_NAME,
            })

        # Test an empty environment
        save_env, os.environ = os.environ, {}
        sh = make_shell()
        test_auth('empty environment', '',
            {'auth_url': '',
            'tenant_id': '',
            'tenant_name': '',
            'username': '',
            'password': '',
            'region_name': '',
            })

        # Test command-line arguments
        sh = make_shell()
        test_auth('cli arguments', '--os-auth-url ' + DEFAULT_AUTH_URL,
            {'auth_url': DEFAULT_AUTH_URL,
            'tenant_id': '',
            'tenant_name': '',
            'username': '',
            'password': '',
            'region_name': '',
            })

        sh = make_shell()
        test_auth('cli arguments', '--os-tenant-id ' + DEFAULT_TENANT_ID,
            {'auth_url': '',
            'tenant_id': DEFAULT_TENANT_ID,
            'tenant_name': '',
            'username': '',
            'password': '',
            'region_name': '',
            })

        sh = make_shell()
        test_auth('cli arguments', '--os-tenant-name ' + DEFAULT_TENANT_NAME,
            {'auth_url': '',
            'tenant_id': '',
            'tenant_name': DEFAULT_TENANT_NAME,
            'username': '',
            'password': '',
            'region_name': '',
            })

        sh = make_shell()
        test_auth('cli arguments', '--os-username ' + DEFAULT_USERNAME,
            {'auth_url': '',
            'tenant_id': '',
            'tenant_name': '',
            'username': DEFAULT_USERNAME,
            'password': '',
            'region_name': '',
            })

        sh = make_shell()
        test_auth('cli arguments', '--os-password ' + DEFAULT_PASSWORD,
            {'auth_url': '',
            'tenant_id': '',
            'tenant_name': '',
            'username': '',
            'password': DEFAULT_PASSWORD,
            'region_name': '',
            })

        sh = make_shell()
        test_auth('cli arguments', '--os-region-name ' + DEFAULT_REGION_NAME,
            {'auth_url': '',
            'tenant_id': '',
            'tenant_name': '',
            'username': '',
            'password': '',
            'region_name': DEFAULT_REGION_NAME,
            })

        # Restore environment
        os.environ = save_env

    def test_shell_auth_token_flow(self):

        def test_auth(desc, cmd_options, default_args):
            initapp_mock = mock.Mock(desc)
            with mock.patch(
                'openstackclient.shell.OpenStackShell.initialize_app',
                initapp_mock):
                    cmd = cmd_options + ' list role'
                    shell(sh, cmd)
                    initapp_mock.assert_called_with(['list', 'role'])
                    assert sh.options.os_token == default_args['os_token']
                    assert sh.options.os_url == default_args['os_url']

        token_env = {
            'OS_TOKEN': DEFAULT_TOKEN,
            'OS_URL': DEFAULT_SERVICE_URL,
        }
        save_env, os.environ = os.environ, token_env.copy()

        # Test the default
        sh = make_shell()
        test_auth('default environment', '',
            {'os_token': DEFAULT_TOKEN,
            'os_url': DEFAULT_SERVICE_URL,
            })

        # Test an empty environment
        os.environ = {}
        sh = make_shell()
        test_auth('empty environment', '',
            {'os_token': '',
            'os_url': '',
            })

        # Test command-line arguments
        sh = make_shell()
        test_auth('cli arguments', '--os-token ' + DEFAULT_TOKEN,
            {'os_token': DEFAULT_TOKEN,
            'os_url': '',
            })

        sh = make_shell()
        test_auth('cli arguments', '--os-url ' + DEFAULT_SERVICE_URL,
            {'os_token': '',
            'os_url': DEFAULT_SERVICE_URL,
            })

        # Restore environment
        os.environ = save_env

    def test_shell_cli_options(self):

        def test_vars(desc, cmd_options, default_args):
            initapp_mock = mock.Mock(desc)
            with mock.patch(
                'openstackclient.shell.OpenStackShell.initialize_app',
                initapp_mock):
                    cmd = cmd_options + ' list server'
                    shell(sh, cmd)
                    initapp_mock.assert_called_with(['list', 'server'])
                    print "options: %s" % sh.options
                    print "args: %s" % default_args
                    assert sh.options.os_compute_api_version == \
                        default_args['compute_api_version']
                    assert sh.options.os_identity_api_version == \
                        default_args['identity_api_version']
                    assert sh.options.os_image_api_version == \
                        default_args['image_api_version']

        option_env = {
            'OS_COMPUTE_API_VERSION': DEFAULT_COMPUTE_API_VERSION,
            'OS_IDENTITY_API_VERSION': DEFAULT_IDENTITY_API_VERSION,
            'OS_IMAGE_API_VERSION': DEFAULT_IMAGE_API_VERSION,
        }
        save_env, os.environ = os.environ, option_env.copy()

        # Test the default
        sh = make_shell()
        test_vars('default environment', '',
            {'compute_api_version': DEFAULT_COMPUTE_API_VERSION,
            'identity_api_version': DEFAULT_IDENTITY_API_VERSION,
            'image_api_version': DEFAULT_IMAGE_API_VERSION,
            })

        # Test an empty environment
        os.environ = {}
        sh = make_shell()
        # This should fall back to the defaults hard-coded in the client libs
        test_vars('empty environment', '',
            {'compute_api_version': LIB_COMPUTE_API_VERSION,
            'identity_api_version': LIB_IDENTITY_API_VERSION,
            'image_api_version': LIB_IMAGE_API_VERSION,
            })

        # Test command-line arguments
        sh = make_shell()
        test_vars('cli arguments',
            '--os-compute-api-version ' + DEFAULT_COMPUTE_API_VERSION,
            {'compute_api_version': DEFAULT_COMPUTE_API_VERSION,
            'identity_api_version': LIB_IDENTITY_API_VERSION,
            'image_api_version': LIB_IMAGE_API_VERSION,
            })

        sh = make_shell()
        test_vars('cli arguments',
            '--os-identity-api-version ' + DEFAULT_IDENTITY_API_VERSION,
            {'compute_api_version': LIB_COMPUTE_API_VERSION,
            'identity_api_version': DEFAULT_IDENTITY_API_VERSION,
            'image_api_version': LIB_IMAGE_API_VERSION,
            })

        sh = make_shell()
        test_vars('cli arguments',
            '--os-image-api-version ' + DEFAULT_IMAGE_API_VERSION,
            {'compute_api_version': LIB_COMPUTE_API_VERSION,
            'identity_api_version': LIB_IDENTITY_API_VERSION,
            'image_api_version': DEFAULT_IMAGE_API_VERSION,
            })

        # Restore environment
        os.environ = save_env
