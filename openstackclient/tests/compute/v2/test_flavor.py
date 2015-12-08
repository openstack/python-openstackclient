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

from openstackclient.common import exceptions
from openstackclient.compute.v2 import flavor
from openstackclient.tests.compute.v2 import fakes as compute_fakes


class TestFlavor(compute_fakes.TestComputev2):

    def setUp(self):
        super(TestFlavor, self).setUp()

        # Get a shortcut to the FlavorManager Mock
        self.flavors_mock = self.app.client_manager.compute.flavors
        self.flavors_mock.reset_mock()


class TestFlavorDelete(TestFlavor):

    flavor = compute_fakes.FakeFlavor.create_one_flavor()

    def setUp(self):
        super(TestFlavorDelete, self).setUp()

        self.flavors_mock.get.return_value = self.flavor
        self.flavors_mock.delete.return_value = None

        self.cmd = flavor.DeleteFlavor(self.app, None)

    def test_flavor_delete(self):
        arglist = [
            self.flavor.id
        ]
        verifylist = [
            ('flavor', self.flavor.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.flavors_mock.delete.assert_called_with(self.flavor.id)

    def test_flavor_delete_with_unexist_flavor(self):
        self.flavors_mock.get.side_effect = exceptions.NotFound(None)
        self.flavors_mock.find.side_effect = exceptions.NotFound(None)

        arglist = [
            'unexist_flavor'
        ]
        verifylist = [
            ('flavor', 'unexist_flavor'),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args)


class TestFlavorList(TestFlavor):

    # Return value of self.flavors_mock.list().
    flavors = compute_fakes.FakeFlavor.create_flavors(count=1)

    columns = (
        'ID',
        'Name',
        'RAM',
        'Disk',
        'Ephemeral',
        'VCPUs',
        'Is Public',
    )
    columns_long = columns + (
        'Swap',
        'RXTX Factor',
        'Properties'
    )

    data = ((
        flavors[0].id,
        flavors[0].name,
        flavors[0].ram,
        '',
        '',
        flavors[0].vcpus,
        ''
    ), )
    data_long = (data[0] + (
        '',
        '',
        'property=\'value\''
    ), )

    def setUp(self):
        super(TestFlavorList, self).setUp()

        self.flavors_mock.list.return_value = self.flavors

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
            'is_public': True,
            'limit': None,
            'marker': None
        }

        self.flavors_mock.list.assert_called_with(
            **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(tuple(self.data), tuple(data))

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
            'is_public': None,
            'limit': None,
            'marker': None
        }

        self.flavors_mock.list.assert_called_with(
            **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(tuple(self.data), tuple(data))

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
            'is_public': False,
            'limit': None,
            'marker': None
        }

        self.flavors_mock.list.assert_called_with(
            **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(tuple(self.data), tuple(data))

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
            'is_public': True,
            'limit': None,
            'marker': None
        }

        self.flavors_mock.list.assert_called_with(
            **kwargs
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(tuple(self.data), tuple(data))

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
            'is_public': True,
            'limit': None,
            'marker': None
        }

        self.flavors_mock.list.assert_called_with(
            **kwargs
        )

        self.assertEqual(self.columns_long, columns)
        self.assertEqual(tuple(self.data_long), tuple(data))


class TestFlavorSet(TestFlavor):

    # Return value of self.flavors_mock.find().
    flavor = compute_fakes.FakeFlavor.create_one_flavor()

    def setUp(self):
        super(TestFlavorSet, self).setUp()

        self.flavors_mock.find.return_value = self.flavor

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

    # Return value of self.flavors_mock.find().
    flavor = compute_fakes.FakeFlavor.create_one_flavor()

    def setUp(self):
        super(TestFlavorUnset, self).setUp()

        self.flavors_mock.find.return_value = self.flavor

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
