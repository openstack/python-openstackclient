#   Copyright 2015 Symantec Corporation
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

from openstackclient.compute.v2 import flavor
from openstackclient.tests.compute.v2 import fakes as compute_fakes
from openstackclient.tests import fakes


class FakeFlavorResource(fakes.FakeResource):

    _keys = {'property': 'value'}

    def set_keys(self, args):
        self._keys.update(args)

    def unset_keys(self, keys):
        for key in keys:
            self._keys.pop(key, None)

    def get_keys(self):
        return self._keys


class TestFlavor(compute_fakes.TestComputev2):

    def setUp(self):
        super(TestFlavor, self).setUp()

        # Get a shortcut to the FlavorManager Mock
        self.flavors_mock = self.app.client_manager.compute.flavors
        self.flavors_mock.reset_mock()


class TestFlavorList(TestFlavor):

    def setUp(self):
        super(TestFlavorList, self).setUp()

        self.flavors_mock.list.return_value = [
            FakeFlavorResource(
                None,
                copy.deepcopy(compute_fakes.FLAVOR),
                loaded=True,
            ),
        ]

        # Get the command object to test
        self.cmd = flavor.ListFlavor(self.app, None)

    def test_flavor_list_no_options(self):
        arglist = []
        verifylist = [
            ('public', True),
            ('all', False),
            ('long', False),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'is_public': True
        }

        self.flavors_mock.list.assert_called_with(
            **kwargs
        )

        collist = (
            'ID',
            'Name',
            'RAM',
            'Disk',
            'Ephemeral',
            'VCPUs',
            'Is Public',
        )
        self.assertEqual(collist, columns)
        datalist = ((
            compute_fakes.flavor_id,
            compute_fakes.flavor_name,
            compute_fakes.flavor_ram,
            '',
            '',
            compute_fakes.flavor_vcpus,
            ''
        ), )
        self.assertEqual(datalist, tuple(data))

    def test_flavor_list_all_flavors(self):
        arglist = [
            '--all',
        ]
        verifylist = [
            ('all', True),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'is_public': None
        }

        self.flavors_mock.list.assert_called_with(
            **kwargs
        )

        collist = (
            'ID',
            'Name',
            'RAM',
            'Disk',
            'Ephemeral',
            'VCPUs',
            'Is Public',
        )
        self.assertEqual(collist, columns)
        datalist = ((
            compute_fakes.flavor_id,
            compute_fakes.flavor_name,
            compute_fakes.flavor_ram,
            '',
            '',
            compute_fakes.flavor_vcpus,
            ''
        ), )
        self.assertEqual(datalist, tuple(data))

    def test_flavor_list_private_flavors(self):
        arglist = [
            '--private',
            ]
        verifylist = [
            ('public', False),
            ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'is_public': False
        }

        self.flavors_mock.list.assert_called_with(
            **kwargs
        )

        collist = (
            'ID',
            'Name',
            'RAM',
            'Disk',
            'Ephemeral',
            'VCPUs',
            'Is Public',
        )
        self.assertEqual(collist, columns)
        datalist = ((
            compute_fakes.flavor_id,
            compute_fakes.flavor_name,
            compute_fakes.flavor_ram,
            '',
            '',
            compute_fakes.flavor_vcpus,
            ''
        ), )
        self.assertEqual(datalist, tuple(data))

    def test_flavor_list_public_flavors(self):
        arglist = [
            '--public',
            ]
        verifylist = [
            ('public', True),
            ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'is_public': True
        }

        self.flavors_mock.list.assert_called_with(
            **kwargs
        )

        collist = (
            'ID',
            'Name',
            'RAM',
            'Disk',
            'Ephemeral',
            'VCPUs',
            'Is Public',
        )
        self.assertEqual(collist, columns)
        datalist = ((
            compute_fakes.flavor_id,
            compute_fakes.flavor_name,
            compute_fakes.flavor_ram,
            '',
            '',
            compute_fakes.flavor_vcpus,
            ''
        ), )
        self.assertEqual(datalist, tuple(data))

    def test_flavor_list_long(self):
        arglist = [
            '--long',
        ]
        verifylist = [
            ('long', True),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # DisplayCommandBase.take_action() returns two tuples
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'is_public': True
        }

        self.flavors_mock.list.assert_called_with(
            **kwargs
        )

        collist = (
            'ID',
            'Name',
            'RAM',
            'Disk',
            'Ephemeral',
            'VCPUs',
            'Is Public',
            'Swap',
            'RXTX Factor',
            'Properties'
        )
        self.assertEqual(collist, columns)
        datalist = ((
            compute_fakes.flavor_id,
            compute_fakes.flavor_name,
            compute_fakes.flavor_ram,
            '',
            '',
            compute_fakes.flavor_vcpus,
            '',
            '',
            '',
            'property=\'value\''
        ), )
        self.assertEqual(datalist, tuple(data))


class TestFlavorSet(TestFlavor):

    def setUp(self):
        super(TestFlavorSet, self).setUp()

        self.flavors_mock.find.return_value = FakeFlavorResource(
            None,
            copy.deepcopy(compute_fakes.FLAVOR),
            loaded=True,
        )

        self.cmd = flavor.SetFlavor(self.app, None)

    def test_flavor_set(self):
        arglist = [
            '--property', 'FOO="B A R"',
            'baremetal'
        ]
        verifylist = [
            ('property', {'FOO': '"B A R"'}),
            ('flavor', 'baremetal')
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.flavors_mock.find.assert_called_with(name='baremetal')

        self.assertEqual('properties', columns[2])
        self.assertIn('FOO=\'"B A R"\'', data[2])


class TestFlavorUnset(TestFlavor):

    def setUp(self):
        super(TestFlavorUnset, self).setUp()

        self.flavors_mock.find.return_value = FakeFlavorResource(
            None,
            copy.deepcopy(compute_fakes.FLAVOR),
            loaded=True,
        )

        self.cmd = flavor.UnsetFlavor(self.app, None)

    def test_flavor_unset(self):
        arglist = [
            '--property', 'property',
            'baremetal'
        ]
        verifylist = [
            ('property', ['property']),
            ('flavor', 'baremetal'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.flavors_mock.find.assert_called_with(name='baremetal')

        self.assertEqual('properties', columns[2])
        self.assertNotIn('property', data[2])
