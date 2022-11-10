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

from tempest.lib import exceptions as tempest_exc

from openstackclient.tests.functional import base


class ArgumentTests(base.TestCase):
    """Functional tests for command line arguments"""

    def test_default_auth_type(self):
        cmd_output = self.openstack(
            'configuration show',
            cloud='',
            parse_output=True,
        )
        self.assertIsNotNone(cmd_output)
        self.assertIn(
            'auth_type',
            cmd_output.keys(),
        )
        self.assertEqual(
            'password',
            cmd_output['auth_type'],
        )

    def test_auth_type_none(self):
        cmd_output = self.openstack(
            'configuration show',
            cloud=None,
            parse_output=True,
        )
        self.assertIsNotNone(cmd_output)
        self.assertIn(
            'auth_type',
            cmd_output.keys(),
        )
        self.assertEqual(
            'none',
            cmd_output['auth_type'],
        )

    def test_auth_type_token_endpoint_opt(self):
        # Make sure token_endpoint is really gone
        try:
            self.openstack(
                'configuration show --os-auth-type token_endpoint',
                cloud=None,
            )
        except tempest_exc.CommandFailed as e:
            self.assertIn('--os-auth-type: invalid choice:', str(e))
            self.assertIn('token_endpoint', str(e))
        else:
            self.fail('CommandFailed should be raised')

    def test_auth_type_password_opt(self):
        cmd_output = self.openstack(
            'configuration show --os-auth-type password',
            cloud=None,
            parse_output=True,
        )
        self.assertIsNotNone(cmd_output)
        self.assertIn(
            'auth_type',
            cmd_output.keys(),
        )
        self.assertEqual(
            'password',
            cmd_output['auth_type'],
        )
