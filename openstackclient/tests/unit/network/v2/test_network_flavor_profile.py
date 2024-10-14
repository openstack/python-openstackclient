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

from unittest import mock

from osc_lib import exceptions

from openstackclient.network.v2 import network_flavor_profile
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes_v3
from openstackclient.tests.unit.network.v2 import fakes as network_fakes


class TestFlavorProfile(network_fakes.TestNetworkV2):
    def setUp(self):
        super().setUp()

        # Get the DomainManager Mock
        self.domains_mock = self.identity_client.domains


class TestCreateFlavorProfile(TestFlavorProfile):
    domain = identity_fakes_v3.FakeDomain.create_one_domain()
    new_flavor_profile = network_fakes.create_one_service_profile()

    columns = (
        'description',
        'driver',
        'enabled',
        'id',
        'meta_info',
    )

    data = (
        new_flavor_profile.description,
        new_flavor_profile.driver,
        new_flavor_profile.is_enabled,
        new_flavor_profile.id,
        new_flavor_profile.meta_info,
    )

    def setUp(self):
        super().setUp()
        self.network_client.create_service_profile = mock.Mock(
            return_value=self.new_flavor_profile
        )
        # Get the command object to test
        self.cmd = network_flavor_profile.CreateNetworkFlavorProfile(
            self.app, None
        )

    def test_create_all_options(self):
        arglist = [
            "--description",
            self.new_flavor_profile.description,
            "--enable",
            "--driver",
            self.new_flavor_profile.driver,
            "--metainfo",
            self.new_flavor_profile.meta_info,
        ]

        verifylist = [
            ('description', self.new_flavor_profile.description),
            ('enable', True),
            ('driver', self.new_flavor_profile.driver),
            ('metainfo', self.new_flavor_profile.meta_info),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.create_service_profile.assert_called_once_with(
            **{
                'description': self.new_flavor_profile.description,
                'enabled': self.new_flavor_profile.is_enabled,
                'driver': self.new_flavor_profile.driver,
                'metainfo': self.new_flavor_profile.meta_info,
            }
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_with_metainfo(self):
        arglist = [
            "--description",
            self.new_flavor_profile.description,
            "--enable",
            "--metainfo",
            self.new_flavor_profile.meta_info,
        ]

        verifylist = [
            ('description', self.new_flavor_profile.description),
            ('enable', True),
            ('metainfo', self.new_flavor_profile.meta_info),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.create_service_profile.assert_called_once_with(
            **{
                'description': self.new_flavor_profile.description,
                'enabled': self.new_flavor_profile.is_enabled,
                'metainfo': self.new_flavor_profile.meta_info,
            }
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_with_driver(self):
        arglist = [
            "--description",
            self.new_flavor_profile.description,
            "--enable",
            "--driver",
            self.new_flavor_profile.driver,
        ]

        verifylist = [
            ('description', self.new_flavor_profile.description),
            ('enable', True),
            ('driver', self.new_flavor_profile.driver),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.create_service_profile.assert_called_once_with(
            **{
                'description': self.new_flavor_profile.description,
                'enabled': self.new_flavor_profile.is_enabled,
                'driver': self.new_flavor_profile.driver,
            }
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_create_without_driver_and_metainfo(self):
        arglist = [
            "--description",
            self.new_flavor_profile.description,
            "--enable",
        ]

        verifylist = [
            ('description', self.new_flavor_profile.description),
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
            '--driver',
            self.new_flavor_profile.driver,
        ]
        verifylist = [
            ('disable', True),
            ('driver', self.new_flavor_profile.driver),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.create_service_profile.assert_called_once_with(
            **{
                'enabled': False,
                'driver': self.new_flavor_profile.driver,
            }
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


class TestDeleteFlavorProfile(TestFlavorProfile):
    # The network flavor_profiles to delete.
    _network_flavor_profiles = network_fakes.create_service_profile(count=2)

    def setUp(self):
        super().setUp()
        self.network_client.delete_service_profile = mock.Mock(
            return_value=None
        )
        self.network_client.find_service_profile = (
            network_fakes.get_service_profile(
                flavor_profile=self._network_flavor_profiles
            )
        )

        # Get the command object to test
        self.cmd = network_flavor_profile.DeleteNetworkFlavorProfile(
            self.app, None
        )

    def test_network_flavor_profile_delete(self):
        arglist = [
            self._network_flavor_profiles[0].id,
        ]
        verifylist = [
            ('flavor_profile', [self._network_flavor_profiles[0].id]),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.network_client.find_service_profile.assert_called_once_with(
            self._network_flavor_profiles[0].id, ignore_missing=False
        )
        self.network_client.delete_service_profile.assert_called_once_with(
            self._network_flavor_profiles[0]
        )
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
        self.network_client.delete_service_profile.assert_has_calls(calls)
        self.assertIsNone(result)

    def test_multi_network_flavor_profiles_delete_with_exception(self):
        arglist = [
            self._network_flavor_profiles[0].id,
            'unexist_network_flavor_profile',
        ]
        verifylist = [
            (
                'flavor_profile',
                [
                    self._network_flavor_profiles[0].id,
                    'unexist_network_flavor_profile',
                ],
            ),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        find_mock_result = [
            self._network_flavor_profiles[0],
            exceptions.CommandError,
        ]
        self.network_client.find_service_profile = mock.Mock(
            side_effect=find_mock_result
        )

        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual(
                '1 of 2 flavor_profiles failed to delete.', str(e)
            )

        self.network_client.find_service_profile.assert_any_call(
            self._network_flavor_profiles[0].id, ignore_missing=False
        )
        self.network_client.find_service_profile.assert_any_call(
            'unexist_network_flavor_profile', ignore_missing=False
        )
        self.network_client.delete_service_profile.assert_called_once_with(
            self._network_flavor_profiles[0]
        )


class TestListFlavorProfile(TestFlavorProfile):
    # The network flavor profiles list
    _network_flavor_profiles = network_fakes.create_service_profile(count=2)

    columns = (
        'ID',
        'Driver',
        'Enabled',
        'Metainfo',
        'Description',
    )
    data = []
    for flavor_profile in _network_flavor_profiles:
        data.append(
            (
                flavor_profile.id,
                flavor_profile.driver,
                flavor_profile.is_enabled,
                flavor_profile.meta_info,
                flavor_profile.description,
            )
        )

    def setUp(self):
        super().setUp()
        self.network_client.service_profiles = mock.Mock(
            return_value=self._network_flavor_profiles
        )

        # Get the command object to test
        self.cmd = network_flavor_profile.ListNetworkFlavorProfile(
            self.app, None
        )

    def test_network_flavor_profile_list(self):
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.service_profiles.assert_called_once_with(**{})
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))


class TestShowFlavorProfile(TestFlavorProfile):
    # The network flavor profile to show.
    network_flavor_profile = network_fakes.create_one_service_profile()
    columns = (
        'description',
        'driver',
        'enabled',
        'id',
        'meta_info',
    )
    data = (
        network_flavor_profile.description,
        network_flavor_profile.driver,
        network_flavor_profile.is_enabled,
        network_flavor_profile.id,
        network_flavor_profile.meta_info,
    )

    def setUp(self):
        super().setUp()
        self.network_client.find_service_profile = mock.Mock(
            return_value=self.network_flavor_profile
        )

        # Get the command object to test
        self.cmd = network_flavor_profile.ShowNetworkFlavorProfile(
            self.app, None
        )

    def test_show_all_options(self):
        arglist = [
            self.network_flavor_profile.id,
        ]
        verifylist = [
            ('flavor_profile', self.network_flavor_profile.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.find_service_profile.assert_called_once_with(
            self.network_flavor_profile.id, ignore_missing=False
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


class TestSetFlavorProfile(TestFlavorProfile):
    # The network flavor profile to set.
    network_flavor_profile = network_fakes.create_one_service_profile()

    def setUp(self):
        super().setUp()
        self.network_client.update_service_profile = mock.Mock(
            return_value=None
        )
        self.network_client.find_service_profile = mock.Mock(
            return_value=self.network_flavor_profile
        )

        # Get the command object to test
        self.cmd = network_flavor_profile.SetNetworkFlavorProfile(
            self.app, None
        )

    def test_set_nothing(self):
        arglist = [self.network_flavor_profile.id]
        verifylist = [
            ('flavor_profile', self.network_flavor_profile.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        attrs = {}
        self.network_client.update_service_profile.assert_called_with(
            self.network_flavor_profile, **attrs
        )
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
        self.network_client.update_service_profile.assert_called_with(
            self.network_flavor_profile, **attrs
        )
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
        self.network_client.update_service_profile.assert_called_with(
            self.network_flavor_profile, **attrs
        )
        self.assertIsNone(result)
