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

from openstackclient.network.v2 import address_scope
from openstackclient.tests import fakes
from openstackclient.tests.identity.v3 import fakes as identity_fakes_v3
from openstackclient.tests.network.v2 import fakes as network_fakes
from openstackclient.tests import utils as tests_utils


class TestAddressScope(network_fakes.TestNetworkV2):

    def setUp(self):
        super(TestAddressScope, self).setUp()

        # Get a shortcut to the network client
        self.network = self.app.client_manager.network


class TestCreateAddressScope(TestAddressScope):

    # The new address scope created.
    new_address_scope = (
        network_fakes.FakeAddressScope.create_one_address_scope(
            attrs={
                'tenant_id': identity_fakes_v3.project_id,
            }
        ))
    columns = (
        'id',
        'ip_version',
        'name',
        'project_id',
        'shared'
    )
    data = (
        new_address_scope.id,
        new_address_scope.ip_version,
        new_address_scope.name,
        new_address_scope.project_id,
        new_address_scope.shared,
    )

    def setUp(self):
        super(TestCreateAddressScope, self).setUp()
        self.network.create_address_scope = mock.Mock(
            return_value=self.new_address_scope)

        # Get the command object to test
        self.cmd = address_scope.CreateAddressScope(self.app, self.namespace)

        # Set identity client v3. And get a shortcut to Identity client.
        identity_client = identity_fakes_v3.FakeIdentityv3Client(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN,
        )
        self.app.client_manager.identity = identity_client
        self.identity = self.app.client_manager.identity

        # Get a shortcut to the ProjectManager Mock
        self.projects_mock = self.identity.projects
        self.projects_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes_v3.PROJECT),
            loaded=True,
        )

        # Get a shortcut to the DomainManager Mock
        self.domains_mock = self.identity.domains
        self.domains_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes_v3.DOMAIN),
            loaded=True,
        )

    def test_create_no_options(self):
        arglist = []
        verifylist = []

        # Missing required args should bail here
        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_create_default_options(self):
        arglist = [
            self.new_address_scope.name,
        ]
        verifylist = [
            ('project', None),
            ('ip_version', self.new_address_scope.ip_version),
            ('name', self.new_address_scope.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = (self.cmd.take_action(parsed_args))

        self.network.create_address_scope.assert_called_once_with(**{
            'ip_version': self.new_address_scope.ip_version,
            'name': self.new_address_scope.name,
        })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_all_options(self):
        arglist = [
            '--ip-version', str(self.new_address_scope.ip_version),
            '--share',
            '--project', identity_fakes_v3.project_name,
            '--project-domain', identity_fakes_v3.domain_name,
            self.new_address_scope.name,
        ]
        verifylist = [
            ('ip_version', self.new_address_scope.ip_version),
            ('share', True),
            ('project', identity_fakes_v3.project_name),
            ('project_domain', identity_fakes_v3.domain_name),
            ('name', self.new_address_scope.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = (self.cmd.take_action(parsed_args))

        self.network.create_address_scope.assert_called_once_with(**{
            'ip_version': self.new_address_scope.ip_version,
            'shared': True,
            'tenant_id': identity_fakes_v3.project_id,
            'name': self.new_address_scope.name,
        })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_no_share(self):
        arglist = [
            '--no-share',
            self.new_address_scope.name,
        ]
        verifylist = [
            ('no_share', True),
            ('name', self.new_address_scope.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network.create_address_scope.assert_called_once_with(**{
            'ip_version': self.new_address_scope.ip_version,
            'shared': False,
            'name': self.new_address_scope.name,
        })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)
