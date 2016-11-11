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

import mock

from osc_lib import exceptions

from openstackclient.network.v2 import network_flavor_profile
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes_v3
from openstackclient.tests.unit.network.v2 import fakes as network_fakes


class TestFlavorProfile(network_fakes.TestNetworkV2):

    def setUp(self):
        super(TestFlavorProfile, self).setUp()
        # Get the network client
        self.network = self.app.client_manager.network
        # Get the ProjectManager Mock
        self.projects_mock = self.app.client_manager.identity.projects
        # Get the DomainManager Mock
        self.domains_mock = self.app.client_manager.identity.domains


class TestCreateFlavorProfile(TestFlavorProfile):
    project = identity_fakes_v3.FakeProject.create_one_project()
    domain = identity_fakes_v3.FakeDomain.create_one_domain()
    new_flavor_profile = (
        network_fakes.FakeNetworkFlavorProfile.
        create_one_service_profile()
    )
    columns = (
        'description',
        'driver',
        'enabled',
        'id',
        'metainfo',
        'project_id',
    )

    data = (
        new_flavor_profile.description,
        new_flavor_profile.driver,
        new_flavor_profile.enabled,
        new_flavor_profile.id,
        new_flavor_profile.metainfo,
        new_flavor_profile.project_id,
    )

    def setUp(self):
        super(TestCreateFlavorProfile, self).setUp()
        self.network.create_service_profile = mock.Mock(
            return_value=self.new_flavor_profile)
        self.projects_mock.get.return_value = self.project
        # Get the command object to test
        self.cmd = (network_flavor_profile.CreateNetworkFlavorProfile(
            self.app, self.namespace))

    def test_create_all_options(self):
        arglist = [
            "--description", self.new_flavor_profile.description,
            "--project", self.new_flavor_profile.project_id,
            '--project-domain', self.domain.name,
            "--enable",
            "--driver", self.new_flavor_profile.driver,
            "--metainfo", self.new_flavor_profile.metainfo,
        ]

        verifylist = [
            ('description', self.new_flavor_profile.description),
            ('project', self.new_flavor_profile.project_id),
            ('project_domain', self.domain.name),
            ('enable', True),
            ('driver', self.new_flavor_profile.driver),
            ('metainfo', self.new_flavor_profile.metainfo)
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = (self.cmd.take_action(parsed_args))

        self.network.create_service_profile.assert_called_once_with(
            **{'description': self.new_flavor_profile.description,
               'tenant_id': self.project.id,
               'enabled': self.new_flavor_profile.enabled,
               'driver': self.new_flavor_profile.driver,
               'metainfo': self.new_flavor_profile.metainfo}
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_with_metainfo(self):
        arglist = [
            "--description", self.new_flavor_profile.description,
            "--project", self.new_flavor_profile.project_id,
            '--project-domain', self.domain.name,
            "--enable",
            "--metainfo", self.new_flavor_profile.metainfo,
        ]

        verifylist = [
            ('description', self.new_flavor_profile.description),
            ('project', self.new_flavor_profile.project_id),
            ('project_domain', self.domain.name),
            ('enable', True),
            ('metainfo', self.new_flavor_profile.metainfo)
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = (self.cmd.take_action(parsed_args))

        self.network.create_service_profile.assert_called_once_with(
            **{'description': self.new_flavor_profile.description,
               'tenant_id': self.project.id,
               'enabled': self.new_flavor_profile.enabled,
               'metainfo': self.new_flavor_profile.metainfo}
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_with_driver(self):
        arglist = [
            "--description", self.new_flavor_profile.description,
            "--project", self.new_flavor_profile.project_id,
            '--project-domain', self.domain.name,
            "--enable",
            "--driver", self.new_flavor_profile.driver,
        ]

        verifylist = [
            ('description', self.new_flavor_profile.description),
            ('project', self.new_flavor_profile.project_id),
            ('project_domain', self.domain.name),
            ('enable', True),
            ('driver', self.new_flavor_profile.driver),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = (self.cmd.take_action(parsed_args))

        self.network.create_service_profile.assert_called_once_with(
            **{'description': self.new_flavor_profile.description,
               'tenant_id': self.project.id,
               'enabled': self.new_flavor_profile.enabled,
               'driver': self.new_flavor_profile.driver,
               }
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_without_driver_and_metainfo(self):
        arglist = [
            "--description", self.new_flavor_profile.description,
            "--project", self.new_flavor_profile.project_id,
            '--project-domain', self.domain.name,
            "--enable",
        ]

        verifylist = [
            ('description', self.new_flavor_profile.description),
            ('project', self.new_flavor_profile.project_id),
            ('project_domain', self.domain.name),
            ('enable', True),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args,
        )

    def test_create_disable(self):
        arglist = [
            '--disable',
            '--driver', self.new_flavor_profile.driver,
        ]
        verifylist = [
            ('disable', True),
            ('driver', self.new_flavor_profile.driver)
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network.create_service_profile.assert_called_once_with(**{
            'enabled': False,
            'driver': self.new_flavor_profile.driver,
        })
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


class TestDeleteFlavorProfile(TestFlavorProfile):

    # The network flavor_profiles to delete.
    _network_flavor_profiles = (
        network_fakes.FakeNetworkFlavorProfile.create_service_profile(count=2))

    def setUp(self):
        super(TestDeleteFlavorProfile, self).setUp()
        self.network.delete_service_profile = mock.Mock(return_value=None)
        self.network.find_service_profile = (
            network_fakes.FakeNetworkFlavorProfile.get_service_profile(
                flavor_profile=self._network_flavor_profiles)
        )

        # Get the command object to test
        self.cmd = network_flavor_profile.DeleteNetworkFlavorProfile(
            self.app, self.namespace)

    def test_network_flavor_profile_delete(self):
        arglist = [
            self._network_flavor_profiles[0].id,
        ]
        verifylist = [
            ('flavor_profile', [self._network_flavor_profiles[0].id]),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.network.find_service_profile.assert_called_once_with(
            self._network_flavor_profiles[0].id, ignore_missing=False)
        self.network.delete_service_profile.assert_called_once_with(
            self._network_flavor_profiles[0])
        self.assertIsNone(result)

    def test_multi_network_flavor_profiles_delete(self):
        arglist = []

        for a in self._network_flavor_profiles:
            arglist.append(a.id)
        verifylist = [
            ('flavor_profile', arglist),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        calls = []
        for a in self._network_flavor_profiles:
            calls.append(mock.call(a))
        self.network.delete_service_profile.assert_has_calls(calls)
        self.assertIsNone(result)

    def test_multi_network_flavor_profiles_delete_with_exception(self):
        arglist = [
            self._network_flavor_profiles[0].id,
            'unexist_network_flavor_profile',
        ]
        verifylist = [
            ('flavor_profile',
             [self._network_flavor_profiles[0].id,
              'unexist_network_flavor_profile']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        find_mock_result = [self._network_flavor_profiles[0],
                            exceptions.CommandError]
        self.network.find_service_profile = (
            mock.Mock(side_effect=find_mock_result)
        )

        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual('1 of 2 flavor_profiles failed to delete.',
                             str(e))

        self.network.find_service_profile.assert_any_call(
            self._network_flavor_profiles[0].id, ignore_missing=False)
        self.network.find_service_profile.assert_any_call(
            'unexist_network_flavor_profile', ignore_missing=False)
        self.network.delete_service_profile.assert_called_once_with(
            self._network_flavor_profiles[0]
        )


class TestListFlavorProfile(TestFlavorProfile):

    # The network flavor profiles list
    _network_flavor_profiles = (
        network_fakes.FakeNetworkFlavorProfile.create_service_profile(count=2))

    columns = (
        'ID',
        'Driver',
        'Enabled',
        'Metainfo',
        'Description',
    )
    data = []
    for flavor_profile in _network_flavor_profiles:
        data.append((
            flavor_profile.id,
            flavor_profile.driver,
            flavor_profile.enabled,
            flavor_profile.metainfo,
            flavor_profile.description,
        ))

    def setUp(self):
        super(TestListFlavorProfile, self).setUp()
        self.network.service_profiles = mock.Mock(
            return_value=self._network_flavor_profiles)

        # Get the command object to test
        self.cmd = network_flavor_profile.ListNetworkFlavorProfile(
            self.app, self.namespace)

    def test_network_flavor_profile_list(self):
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network.service_profiles.assert_called_once_with(**{})
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))


class TestShowFlavorProfile(TestFlavorProfile):

    # The network flavor profile to show.
    network_flavor_profile = (
        network_fakes.FakeNetworkFlavorProfile.create_one_service_profile())
    columns = (
        'description',
        'driver',
        'enabled',
        'id',
        'metainfo',
        'project_id',
    )
    data = (
        network_flavor_profile.description,
        network_flavor_profile.driver,
        network_flavor_profile.enabled,
        network_flavor_profile.id,
        network_flavor_profile.metainfo,
        network_flavor_profile.project_id,
    )

    def setUp(self):
        super(TestShowFlavorProfile, self).setUp()
        self.network.find_service_profile = mock.Mock(
            return_value=self.network_flavor_profile)

        # Get the command object to test
        self.cmd = network_flavor_profile.ShowNetworkFlavorProfile(
            self.app, self.namespace)

    def test_show_all_options(self):
        arglist = [
            self.network_flavor_profile.id,
        ]
        verifylist = [
            ('flavor_profile', self.network_flavor_profile.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network.find_service_profile.assert_called_once_with(
            self.network_flavor_profile.id, ignore_missing=False)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


class TestSetFlavorProfile(TestFlavorProfile):

    # The network flavor profile to set.
    network_flavor_profile = (
        network_fakes.FakeNetworkFlavorProfile.create_one_service_profile())

    def setUp(self):
        super(TestSetFlavorProfile, self).setUp()
        self.network.update_service_profile = mock.Mock(return_value=None)
        self.network.find_service_profile = mock.Mock(
            return_value=self.network_flavor_profile)

        # Get the command object to test
        self.cmd = network_flavor_profile.SetNetworkFlavorProfile(
            self.app, self.namespace)

    def test_set_nothing(self):
        arglist = [self.network_flavor_profile.id]
        verifylist = [
            ('flavor_profile', self.network_flavor_profile.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        attrs = {}
        self.network.update_service_profile.assert_called_with(
            self.network_flavor_profile, **attrs)
        self.assertIsNone(result)

    def test_set_enable(self):
        arglist = [
            '--enable',
            self.network_flavor_profile.id,
        ]
        verifylist = [
            ('enable', True),
            ('flavor_profile', self.network_flavor_profile.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        attrs = {
            'enabled': True,
        }
        self.network.update_service_profile.assert_called_with(
            self.network_flavor_profile, **attrs)
        self.assertIsNone(result)

    def test_set_disable(self):
        arglist = [
            '--disable',
            self.network_flavor_profile.id,
        ]
        verifylist = [
            ('disable', True),
            ('flavor_profile', self.network_flavor_profile.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        attrs = {
            'enabled': False,
        }
        self.network.update_service_profile.assert_called_with(
            self.network_flavor_profile, **attrs)
        self.assertIsNone(result)
