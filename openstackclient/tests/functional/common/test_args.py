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

import json

from openstackclient.tests.functional import base


class ArgumentTests(base.TestCase):
    """Functional tests for command line arguments"""

    def test_default_auth_type(self):
        cmd_output = json.loads(self.openstack(
            'configuration show -f json',
            cloud='',
        ))
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
        cmd_output = json.loads(self.openstack(
            'configuration show -f json',
            cloud=None,
        ))
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
        cmd_output = json.loads(self.openstack(
            'configuration show -f json --os-auth-type token_endpoint',
            cloud=None,
        ))
        self.assertIsNotNone(cmd_output)
        self.assertIn(
            'auth_type',
            cmd_output.keys(),
        )
        self.assertEqual(
            'token_endpoint',
            cmd_output['auth_type'],
        )

    def test_auth_type_password_opt(self):
        cmd_output = json.loads(self.openstack(
            'configuration show -f json --os-auth-type password',
            cloud=None,
        ))
        self.assertIsNotNone(cmd_output)
        self.assertIn(
            'auth_type',
            cmd_output.keys(),
        )
        self.assertEqual(
            'password',
            cmd_output['auth_type'],
        )
