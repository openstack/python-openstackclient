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

from openstackclient.common import exceptions
from openstackclient.common import utils
from openstackclient.network.v2 import network
from openstackclient.tests import fakes
from openstackclient.tests.identity.v2_0 import fakes as identity_fakes_v2
from openstackclient.tests.identity.v3 import fakes as identity_fakes_v3
from openstackclient.tests.network.v2 import fakes as network_fakes

RESOURCE = 'network'
RESOURCES = 'networks'
FAKE_ID = 'iditty'
FAKE_NAME = 'noo'
FAKE_PROJECT = 'yaa'
RECORD = {
    'id': FAKE_ID,
    'name': FAKE_NAME,
    'admin_state_up': True,
    'router:external': True,
    'status': 'ACTIVE',
    'subnets': ['a', 'b'],
    'tenant_id': FAKE_PROJECT,
}
RESPONSE = {RESOURCE: copy.deepcopy(RECORD)}
FILTERED = [
    (
        'id',
        'name',
        'project_id',
        'router_type',
        'state',
        'status',
        'subnets',
    ),
    (
        FAKE_ID,
        FAKE_NAME,
        FAKE_PROJECT,
        'External',
        'UP',
        'ACTIVE',
        'a, b',
    ),
]


class TestNetwork(network_fakes.TestNetworkV2):

    def setUp(self):
        super(TestNetwork, self).setUp()

        # Get a shortcut to the network client
        self.network = self.app.client_manager.network

        # Get a shortcut to the APIManager
        self.api = self.app.client_manager.network.api


@mock.patch('openstackclient.network.v2.network._make_client_sdk')
class TestCreateNetworkIdentityV3(TestNetwork):

    # The new network created.
    _network = network_fakes.FakeNetwork.create_one_network(
        attrs={'tenant_id': identity_fakes_v3.project_id}
    )

    columns = (
        'admin_state_up',
        'id',
        'name',
        'router_external',
        'status',
        'subnets',
        'tenant_id',
    )

    data = (
        network._format_admin_state(_network.admin_state_up),
        _network.id,
        _network.name,
        network._format_router_external(_network.router_external),
        _network.status,
        utils.format_list(_network.subnets),
        _network.tenant_id,
    )

    def setUp(self):
        super(TestCreateNetworkIdentityV3, self).setUp()

        self.network.create_network = mock.Mock(return_value=self._network)

        # Get the command object to test
        self.cmd = network.CreateNetwork(self.app, self.namespace)

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

    def test_create_no_options(self, _make_client_sdk):
        _make_client_sdk.return_value = self.app.client_manager.network

        arglist = [
            self._network.name,
        ]
        verifylist = [
            ('name', self._network.name),
            ('admin_state', True),
            ('shared', None),
            ('project', None),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network.create_network.assert_called_with(**{
            'admin_state_up': True,
            'name': self._network.name,
        })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_all_options(self, _make_client_sdk):
        _make_client_sdk.return_value = self.app.client_manager.network

        arglist = [
            "--disable",
            "--share",
            "--project", identity_fakes_v3.project_name,
            "--project-domain", identity_fakes_v3.domain_name,
            self._network.name,
        ]
        verifylist = [
            ('admin_state', False),
            ('shared', True),
            ('project', identity_fakes_v3.project_name),
            ('project_domain', identity_fakes_v3.domain_name),
            ('name', self._network.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = (self.cmd.take_action(parsed_args))

        self.network.create_network.assert_called_with(**{
            'admin_state_up': False,
            'name': self._network.name,
            'shared': True,
            'tenant_id': identity_fakes_v3.project_id,
        })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_other_options(self, _make_client_sdk):
        _make_client_sdk.return_value = self.app.client_manager.network

        arglist = [
            "--enable",
            "--no-share",
            self._network.name,
        ]
        verifylist = [
            ('admin_state', True),
            ('shared', False),
            ('name', self._network.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network.create_network.assert_called_with(**{
            'admin_state_up': True,
            'name': self._network.name,
            'shared': False,
        })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


@mock.patch('openstackclient.network.v2.network._make_client_sdk')
class TestCreateNetworkIdentityV2(TestNetwork):

    # The new network created.
    _network = network_fakes.FakeNetwork.create_one_network(
        attrs={'tenant_id': identity_fakes_v2.project_id}
    )

    columns = (
        'admin_state_up',
        'id',
        'name',
        'router_external',
        'status',
        'subnets',
        'tenant_id',
    )

    data = (
        network._format_admin_state(_network.admin_state_up),
        _network.id,
        _network.name,
        network._format_router_external(_network.router_external),
        _network.status,
        utils.format_list(_network.subnets),
        _network.tenant_id,
    )

    def setUp(self):
        super(TestCreateNetworkIdentityV2, self).setUp()

        self.network.create_network = mock.Mock(return_value=self._network)

        # Get the command object to test
        self.cmd = network.CreateNetwork(self.app, self.namespace)

        # Set identity client v2. And get a shortcut to Identity client.
        identity_client = identity_fakes_v2.FakeIdentityv2Client(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN,
        )
        self.app.client_manager.identity = identity_client
        self.identity = self.app.client_manager.identity

        # Get a shortcut to the ProjectManager Mock
        self.projects_mock = self.identity.tenants
        self.projects_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes_v2.PROJECT),
            loaded=True,
        )

        # There is no DomainManager Mock in fake identity v2.

    def test_create_with_project_identityv2(self, _make_client_sdk):
        _make_client_sdk.return_value = self.app.client_manager.network

        arglist = [
            "--project", identity_fakes_v2.project_name,
            self._network.name,
        ]
        verifylist = [
            ('admin_state', True),
            ('shared', None),
            ('name', self._network.name),
            ('project', identity_fakes_v2.project_name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network.create_network.assert_called_with(**{
            'admin_state_up': True,
            'name': self._network.name,
            'tenant_id': identity_fakes_v2.project_id,
        })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_with_domain_identityv2(self, _make_client_sdk):
        _make_client_sdk.return_value = self.app.client_manager.network

        arglist = [
            "--project", identity_fakes_v3.project_name,
            "--project-domain", identity_fakes_v3.domain_name,
            self._network.name,
        ]
        verifylist = [
            ('admin_state', True),
            ('shared', None),
            ('project', identity_fakes_v3.project_name),
            ('project_domain', identity_fakes_v3.domain_name),
            ('name', self._network.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            AttributeError,
            self.cmd.take_action,
            parsed_args,
        )


class TestDeleteNetwork(TestNetwork):

    def setUp(self):
        super(TestDeleteNetwork, self).setUp()

        self.network.delete_network = mock.Mock(
            return_value=None
        )

        self.network.list_networks = mock.Mock(
            return_value={RESOURCES: [copy.deepcopy(RECORD)]}
        )

        # Get the command object to test
        self.cmd = network.DeleteNetwork(self.app, self.namespace)

    def test_delete(self):
        arglist = [
            FAKE_NAME,
        ]
        verifylist = [
            ('networks', [FAKE_NAME]),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.network.delete_network.assert_called_with(FAKE_ID)
        self.assertEqual(None, result)


@mock.patch('openstackclient.network.v2.network._make_client_sdk')
class TestListNetwork(TestNetwork):

    # The networks going to be listed up.
    _network = network_fakes.FakeNetwork.create_networks(count=3)

    columns = (
        'ID',
        'Name',
        'Subnets',
    )
    columns_long = (
        'ID',
        'Name',
        'Status',
        'Project',
        'State',
        'Shared',
        'Subnets',
        'Network Type',
        'Router Type',
    )

    data = []
    for net in _network:
        data.append((
            net.id,
            net.name,
            utils.format_list(net.subnets),
        ))

    data_long = []
    for net in _network:
        data_long.append((
            net.id,
            net.name,
            net.status,
            net.tenant_id,
            network._format_admin_state(net.admin_state_up),
            net.shared,
            utils.format_list(net.subnets),
            net.provider_network_type,
            network._format_router_external(net.router_external),
        ))

    def setUp(self):
        super(TestListNetwork, self).setUp()

        # Get the command object to test
        self.cmd = network.ListNetwork(self.app, self.namespace)

        self.network.networks = mock.Mock(return_value=self._network)

    def test_network_list_no_options(self, _make_client_sdk):
        _make_client_sdk.return_value = self.app.client_manager.network

        arglist = []
        verifylist = [
            ('external', False),
            ('long', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        self.network.networks.assert_called_with()
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_list_external(self, _make_client_sdk):
        _make_client_sdk.return_value = self.app.client_manager.network

        arglist = [
            '--external',
        ]
        verifylist = [
            ('external', True),
            ('long', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        self.network.networks.assert_called_with(
            **{'router:external': True}
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_network_list_long(self, _make_client_sdk):
        _make_client_sdk.return_value = self.app.client_manager.network

        arglist = [
            '--long',
        ]
        verifylist = [
            ('long', True),
            ('external', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        self.network.networks.assert_called_with()
        self.assertEqual(self.columns_long, columns)
        self.assertEqual(self.data_long, list(data))


class TestSetNetwork(TestNetwork):

    def setUp(self):
        super(TestSetNetwork, self).setUp()

        self.network.update_network = mock.Mock(
            return_value=None
        )

        self.network.list_networks = mock.Mock(
            return_value={RESOURCES: [copy.deepcopy(RECORD)]}
        )

        # Get the command object to test
        self.cmd = network.SetNetwork(self.app, self.namespace)

    def test_set_this(self):
        arglist = [
            FAKE_NAME,
            '--enable',
            '--name', 'noob',
            '--share',
        ]
        verifylist = [
            ('identifier', FAKE_NAME),
            ('admin_state', True),
            ('name', 'noob'),
            ('shared', True),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        exp = {'admin_state_up': True, 'name': 'noob', 'shared': True}
        exp_record = {RESOURCE: exp}
        self.network.update_network.assert_called_with(FAKE_ID, exp_record)
        self.assertEqual(None, result)

    def test_set_that(self):
        arglist = [
            FAKE_NAME,
            '--disable',
            '--no-share',
        ]
        verifylist = [
            ('identifier', FAKE_NAME),
            ('admin_state', False),
            ('shared', False),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        exp = {'admin_state_up': False, 'shared': False}
        exp_record = {RESOURCE: exp}
        self.network.update_network.assert_called_with(FAKE_ID, exp_record)
        self.assertEqual(None, result)

    def test_set_nothing(self):
        arglist = [FAKE_NAME, ]
        verifylist = [('identifier', FAKE_NAME), ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(exceptions.CommandError, self.cmd.take_action,
                          parsed_args)


@mock.patch(
    'openstackclient.api.network_v2.APIv2.find_attr'
)
class TestShowNetwork(TestNetwork):

    def setUp(self):
        super(TestShowNetwork, self).setUp()

        # Get the command object to test
        self.cmd = network.ShowNetwork(self.app, self.namespace)

    def test_show_no_options(self, find_attr):
        arglist = [
            FAKE_NAME,
        ]
        verifylist = [
            ('identifier', FAKE_NAME),
        ]
        find_attr.return_value = copy.deepcopy(RECORD)

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = list(self.cmd.take_action(parsed_args))

        find_attr.assert_called_with('networks', FAKE_NAME)
        self.assertEqual(FILTERED, result)

    def test_show_all_options(self, find_attr):
        arglist = [FAKE_NAME]
        verifylist = [('identifier', FAKE_NAME)]
        find_attr.return_value = copy.deepcopy(RECORD)

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = list(self.cmd.take_action(parsed_args))

        find_attr.assert_called_with('networks', FAKE_NAME)
        self.assertEqual(FILTERED, result)
