# Copyright (c) 2016, Intel Corporation.
# All Rights Reserved.
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

from osc_lib import exceptions

from openstackclient.network.v2 import network_flavor
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes_v3
from openstackclient.tests.unit.network.v2 import fakes as network_fakes
from openstackclient.tests.unit import utils as tests_utils


class TestNetworkFlavor(network_fakes.TestNetworkV2):

    def setUp(self):
        super(TestNetworkFlavor, self).setUp()

        # Get a shortcut to the network client
        self.network = self.app.client_manager.network
        # Get a shortcut to the ProjectManager Mock
        self.projects_mock = self.app.client_manager.identity.projects
        # Get a shortcut to the DomainManager Mock
        self.domains_mock = self.app.client_manager.identity.domains


class TestAddNetworkFlavorToProfile(TestNetworkFlavor):

    network_flavor = \
        network_fakes.FakeNetworkFlavor.create_one_network_flavor()
    service_profile = \
        network_fakes.FakeNetworkFlavorProfile.create_one_service_profile()

    def setUp(self):
        super(TestAddNetworkFlavorToProfile, self).setUp()
        self.network.find_flavor = mock.Mock(return_value=self.network_flavor)
        self.network.find_service_profile = mock.Mock(
            return_value=self.service_profile)
        self.network.associate_flavor_with_service_profile = mock.Mock()

        self.cmd = network_flavor.AddNetworkFlavorToProfile(
            self.app, self.namespace)

    def test_show_no_options(self):
        arglist = []
        verifylist = []

        # Missing required args should bail here
        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_add_flavor_to_service_profile(self):
        arglist = [
            self.network_flavor.id,
            self.service_profile.id
        ]
        verifylist = [
            ('flavor', self.network_flavor.id),
            ('service_profile', self.service_profile.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        self.network.associate_flavor_with_service_profile.\
            assert_called_once_with(self.network_flavor, self.service_profile)


class TestCreateNetworkFlavor(TestNetworkFlavor):

    project = identity_fakes_v3.FakeProject.create_one_project()
    domain = identity_fakes_v3.FakeDomain.create_one_domain()
    # The new network flavor created.
    new_network_flavor = (
        network_fakes.FakeNetworkFlavor.create_one_network_flavor())
    columns = (
        'description',
        'enabled',
        'id',
        'name',
        'project_id',
        'service_type'
    )
    data = (
        new_network_flavor.description,
        new_network_flavor.enabled,
        new_network_flavor.id,
        new_network_flavor.name,
        new_network_flavor.project_id,
        new_network_flavor.service_type,
    )

    def setUp(self):
        super(TestCreateNetworkFlavor, self).setUp()
        self.network.create_flavor = mock.Mock(
            return_value=self.new_network_flavor)

        # Get the command object to test
        self.cmd = network_flavor.CreateNetworkFlavor(self.app, self.namespace)

        self.projects_mock.get.return_value = self.project
        self.domains_mock.get.return_value = self.domain

    def test_create_no_options(self):
        arglist = []
        verifylist = []

        # Missing required args should bail here
        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_create_default_options(self):
        arglist = [
            '--service-type', self.new_network_flavor.service_type,
            self.new_network_flavor.name,
        ]
        verifylist = [
            ('service_type', self.new_network_flavor.service_type),
            ('name', self.new_network_flavor.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = (self.cmd.take_action(parsed_args))

        self.network.create_flavor.assert_called_once_with(**{
            'service_type': self.new_network_flavor.service_type,
            'name': self.new_network_flavor.name,
        })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_all_options(self):
        arglist = [
            '--description', self.new_network_flavor.description,
            '--enable',
            '--project', self.new_network_flavor.project_id,
            '--project-domain', self.domain.name,
            '--service-type', self.new_network_flavor.service_type,
            self.new_network_flavor.name,
        ]
        verifylist = [
            ('description', self.new_network_flavor.description),
            ('enable', True),
            ('project', self.new_network_flavor.project_id),
            ('project_domain', self.domain.name),
            ('service_type', self.new_network_flavor.service_type),
            ('name', self.new_network_flavor.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = (self.cmd.take_action(parsed_args))

        self.network.create_flavor.assert_called_once_with(**{
            'description': self.new_network_flavor.description,
            'enabled': True,
            'tenant_id': self.project.id,
            'service_type': self.new_network_flavor.service_type,
            'name': self.new_network_flavor.name,
        })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_disable(self):
        arglist = [
            '--disable',
            '--service-type', self.new_network_flavor.service_type,
            self.new_network_flavor.name,
        ]
        verifylist = [
            ('disable', True),
            ('service_type', self.new_network_flavor.service_type),
            ('name', self.new_network_flavor.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network.create_flavor.assert_called_once_with(**{
            'enabled': False,
            'service_type': self.new_network_flavor.service_type,
            'name': self.new_network_flavor.name,
        })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


class TestDeleteNetworkFlavor(TestNetworkFlavor):

    # The network flavor to delete.
    _network_flavors = (
        network_fakes.FakeNetworkFlavor.create_flavor(count=2))

    def setUp(self):
        super(TestDeleteNetworkFlavor, self).setUp()
        self.network.delete_flavor = mock.Mock(return_value=None)
        self.network.find_flavor = (
            network_fakes.FakeNetworkFlavor.get_flavor(
                network_flavors=self._network_flavors)
        )

        # Get the command object to test
        self.cmd = network_flavor.DeleteNetworkFlavor(self.app, self.namespace)

    def test_network_flavor_delete(self):
        arglist = [
            self._network_flavors[0].name,
        ]
        verifylist = [
            ('flavor', [self._network_flavors[0].name]),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.network.find_flavor.assert_called_once_with(
            self._network_flavors[0].name, ignore_missing=False)
        self.network.delete_flavor.assert_called_once_with(
            self._network_flavors[0])
        self.assertIsNone(result)

    def test_multi_network_flavors_delete(self):
        arglist = []
        verifylist = []

        for a in self._network_flavors:
            arglist.append(a.name)
        verifylist = [
            ('flavor', arglist),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        calls = []
        for a in self._network_flavors:
            calls.append(mock.call(a))
        self.network.delete_flavor.assert_has_calls(calls)
        self.assertIsNone(result)

    def test_multi_network_flavors_delete_with_exception(self):
        arglist = [
            self._network_flavors[0].name,
            'unexist_network_flavor',
        ]
        verifylist = [
            ('flavor',
             [self._network_flavors[0].name, 'unexist_network_flavor']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        find_mock_result = [self._network_flavors[0], exceptions.CommandError]
        self.network.find_flavor = (
            mock.Mock(side_effect=find_mock_result)
        )

        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual('1 of 2 flavors failed to delete.', str(e))

        self.network.find_flavor.assert_any_call(
            self._network_flavors[0].name, ignore_missing=False)
        self.network.find_flavor.assert_any_call(
            'unexist_network_flavor', ignore_missing=False)
        self.network.delete_flavor.assert_called_once_with(
            self._network_flavors[0]
        )


class TestListNetworkFlavor(TestNetworkFlavor):

    # The network flavors to list up.
    _network_flavors = (
        network_fakes.FakeNetworkFlavor.create_flavor(count=2))
    columns = (
        'ID',
        'Name',
        'Enabled',
        'Service Type',
        'Description',
    )
    data = []
    for flavor in _network_flavors:
        data.append((
            flavor.id,
            flavor.name,
            flavor.enabled,
            flavor.service_type,
            flavor.description,
        ))

    def setUp(self):
        super(TestListNetworkFlavor, self).setUp()
        self.network.flavors = mock.Mock(
            return_value=self._network_flavors)

        # Get the command object to test
        self.cmd = network_flavor.ListNetworkFlavor(self.app, self.namespace)

    def test_network_flavor_list(self):
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network.flavors.assert_called_once_with(**{})
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))


class TestRemoveNetworkFlavorFromProfile(TestNetworkFlavor):

    network_flavor = \
        network_fakes.FakeNetworkFlavor.create_one_network_flavor()
    service_profile = \
        network_fakes.FakeNetworkFlavorProfile.create_one_service_profile()

    def setUp(self):
        super(TestRemoveNetworkFlavorFromProfile, self).setUp()
        self.network.find_flavor = mock.Mock(return_value=self.network_flavor)
        self.network.find_service_profile = mock.Mock(
            return_value=self.service_profile)
        self.network.disassociate_flavor_from_service_profile = mock.Mock()

        self.cmd = network_flavor.RemoveNetworkFlavorFromProfile(
            self.app, self.namespace)

    def test_show_no_options(self):
        arglist = []
        verifylist = []

        # Missing required args should bail here
        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_remove_flavor_from_service_profile(self):
        arglist = [
            self.network_flavor.id,
            self.service_profile.id
        ]
        verifylist = [
            ('flavor', self.network_flavor.id),
            ('service_profile', self.service_profile.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        self.network.disassociate_flavor_from_service_profile.\
            assert_called_once_with(self.network_flavor, self.service_profile)


class TestShowNetworkFlavor(TestNetworkFlavor):

    # The network flavor to show.
    new_network_flavor = (
        network_fakes.FakeNetworkFlavor.create_one_network_flavor())
    columns = (
        'description',
        'enabled',
        'id',
        'name',
        'project_id',
        'service_type'
    )
    data = (
        new_network_flavor.description,
        new_network_flavor.enabled,
        new_network_flavor.id,
        new_network_flavor.name,
        new_network_flavor.project_id,
        new_network_flavor.service_type,
    )

    def setUp(self):
        super(TestShowNetworkFlavor, self).setUp()
        self.network.find_flavor = mock.Mock(
            return_value=self.new_network_flavor)

        # Get the command object to test
        self.cmd = network_flavor.ShowNetworkFlavor(self.app, self.namespace)

    def test_show_no_options(self):
        arglist = []
        verifylist = []

        # Missing required args should bail here
        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_show_all_options(self):
        arglist = [
            self.new_network_flavor.name,
        ]
        verifylist = [
            ('flavor', self.new_network_flavor.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network.find_flavor.assert_called_once_with(
            self.new_network_flavor.name, ignore_missing=False)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


class TestSetNetworkFlavor(TestNetworkFlavor):

    # The network flavor to set.
    new_network_flavor = (
        network_fakes.FakeNetworkFlavor.create_one_network_flavor())

    def setUp(self):
        super(TestSetNetworkFlavor, self).setUp()
        self.network.update_flavor = mock.Mock(return_value=None)
        self.network.find_flavor = mock.Mock(
            return_value=self.new_network_flavor)

        # Get the command object to test
        self.cmd = network_flavor.SetNetworkFlavor(self.app, self.namespace)

    def test_set_nothing(self):
        arglist = [self.new_network_flavor.name, ]
        verifylist = [
            ('flavor', self.new_network_flavor.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        attrs = {}
        self.network.update_flavor.assert_called_with(
            self.new_network_flavor, **attrs)
        self.assertIsNone(result)

    def test_set_name_and_enable(self):
        arglist = [
            '--name', 'new_network_flavor',
            '--enable',
            self.new_network_flavor.name,
        ]
        verifylist = [
            ('name', 'new_network_flavor'),
            ('enable', True),
            ('flavor', self.new_network_flavor.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        attrs = {
            'name': "new_network_flavor",
            'enabled': True,
        }
        self.network.update_flavor.assert_called_with(
            self.new_network_flavor, **attrs)
        self.assertIsNone(result)

    def test_set_disable(self):
        arglist = [
            '--disable',
            self.new_network_flavor.name,
        ]
        verifylist = [
            ('disable', True),
            ('flavor', self.new_network_flavor.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        attrs = {
            'enabled': False,
        }
        self.network.update_flavor.assert_called_with(
            self.new_network_flavor, **attrs)
        self.assertIsNone(result)
