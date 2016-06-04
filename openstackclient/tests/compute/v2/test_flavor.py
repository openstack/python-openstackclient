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

from openstackclient.common import exceptions
from openstackclient.common import utils
from openstackclient.compute.v2 import flavor
from openstackclient.tests.compute.v2 import fakes as compute_fakes
from openstackclient.tests import fakes
from openstackclient.tests.identity.v3 import fakes as identity_fakes
from openstackclient.tests import utils as tests_utils


class TestFlavor(compute_fakes.TestComputev2):

    def setUp(self):
        super(TestFlavor, self).setUp()

        # Get a shortcut to the FlavorManager Mock
        self.flavors_mock = self.app.client_manager.compute.flavors
        self.flavors_mock.reset_mock()

        # Get a shortcut to the FlavorAccessManager Mock
        self.flavor_access_mock = self.app.client_manager.compute.flavor_access
        self.flavor_access_mock.reset_mock()

        self.projects_mock = self.app.client_manager.identity.projects
        self.projects_mock.reset_mock()


class TestFlavorCreate(TestFlavor):

    flavor = compute_fakes.FakeFlavor.create_one_flavor(
        attrs={'links': 'flavor-links'})

    columns = (
        'OS-FLV-DISABLED:disabled',
        'OS-FLV-EXT-DATA:ephemeral',
        'disk',
        'id',
        'name',
        'os-flavor-access:is_public',
        'ram',
        'rxtx_factor',
        'swap',
        'vcpus',
    )
    data = (
        flavor.disabled,
        flavor.ephemeral,
        flavor.disk,
        flavor.id,
        flavor.name,
        flavor.is_public,
        flavor.ram,
        flavor.rxtx_factor,
        flavor.swap,
        flavor.vcpus,
    )

    def setUp(self):
        super(TestFlavorCreate, self).setUp()

        self.flavors_mock.create.return_value = self.flavor
        self.cmd = flavor.CreateFlavor(self.app, None)

    def test_flavor_create_default_options(self):

        arglist = [
            self.flavor.name
        ]
        verifylist = [
            ('name', self.flavor.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        default_args = (
            self.flavor.name,
            256,
            1,
            0,
            'auto',
            0,
            0,
            1.0,
            True
        )
        columns, data = self.cmd.take_action(parsed_args)
        self.flavors_mock.create.assert_called_once_with(*default_args)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_flavor_create_all_options(self):

        arglist = [
            self.flavor.name,
            '--id', self.flavor.id,
            '--ram', str(self.flavor.ram),
            '--disk', str(self.flavor.disk),
            '--ephemeral', str(self.flavor.ephemeral),
            '--swap', str(self.flavor.swap),
            '--vcpus', str(self.flavor.vcpus),
            '--rxtx-factor', str(self.flavor.rxtx_factor),
            '--public',
        ]
        verifylist = [
            ('name', self.flavor.name),
            ('id', self.flavor.id),
            ('ram', self.flavor.ram),
            ('disk', self.flavor.disk),
            ('ephemeral', self.flavor.ephemeral),
            ('swap', self.flavor.swap),
            ('vcpus', self.flavor.vcpus),
            ('rxtx_factor', self.flavor.rxtx_factor),
            ('public', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        args = (
            self.flavor.name,
            self.flavor.ram,
            self.flavor.vcpus,
            self.flavor.disk,
            self.flavor.id,
            self.flavor.ephemeral,
            self.flavor.swap,
            self.flavor.rxtx_factor,
            self.flavor.is_public,
        )
        columns, data = self.cmd.take_action(parsed_args)
        self.flavors_mock.create.assert_called_once_with(*args)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_flavor_create_other_options(self):

        self.flavor.is_public = False
        arglist = [
            self.flavor.name,
            '--id', self.flavor.id,
            '--ram', str(self.flavor.ram),
            '--disk', str(self.flavor.disk),
            '--ephemeral', str(self.flavor.ephemeral),
            '--swap', str(self.flavor.swap),
            '--vcpus', str(self.flavor.vcpus),
            '--rxtx-factor', str(self.flavor.rxtx_factor),
            '--private',
        ]
        verifylist = [
            ('name', self.flavor.name),
            ('id', self.flavor.id),
            ('ram', self.flavor.ram),
            ('disk', self.flavor.disk),
            ('ephemeral', self.flavor.ephemeral),
            ('swap', self.flavor.swap),
            ('vcpus', self.flavor.vcpus),
            ('rxtx_factor', self.flavor.rxtx_factor),
            ('public', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        args = (
            self.flavor.name,
            self.flavor.ram,
            self.flavor.vcpus,
            self.flavor.disk,
            self.flavor.id,
            self.flavor.ephemeral,
            self.flavor.swap,
            self.flavor.rxtx_factor,
            self.flavor.is_public,
        )
        columns, data = self.cmd.take_action(parsed_args)
        self.flavors_mock.create.assert_called_once_with(*args)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_flavor_create_no_options(self):
        arglist = []
        verifylist = None
        self.assertRaises(tests_utils.ParserException,
                          self.check_parser,
                          self.cmd,
                          arglist,
                          verifylist)


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

        result = self.cmd.take_action(parsed_args)

        self.flavors_mock.delete.assert_called_with(self.flavor.id)
        self.assertIsNone(result)

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
        flavors[0].disk,
        flavors[0].ephemeral,
        flavors[0].vcpus,
        flavors[0].is_public,
    ), )
    data_long = (data[0] + (
        flavors[0].swap,
        flavors[0].rxtx_factor,
        u'property=\'value\''
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

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
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

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
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

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
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

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
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

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
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
    flavor = compute_fakes.FakeFlavor.create_one_flavor(
        attrs={'os-flavor-access:is_public': False})

    def setUp(self):
        super(TestFlavorSet, self).setUp()

        self.flavors_mock.find.return_value = self.flavor
        self.flavors_mock.get.side_effect = exceptions.NotFound(None)
        # Return a project
        self.projects_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.PROJECT),
            loaded=True,
        )
        self.cmd = flavor.SetFlavor(self.app, None)

    def test_flavor_set_property(self):
        arglist = [
            '--property', 'FOO="B A R"',
            'baremetal'
        ]
        verifylist = [
            ('property', {'FOO': '"B A R"'}),
            ('flavor', 'baremetal')
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.flavors_mock.find.assert_called_with(name=parsed_args.flavor,
                                                  is_public=None)
        self.assertIsNone(result)

    def test_flavor_set_project(self):
        arglist = [
            '--project', identity_fakes.project_id,
            self.flavor.id,
        ]
        verifylist = [
            ('project', identity_fakes.project_id),
            ('flavor', self.flavor.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        self.flavor_access_mock.add_tenant_access.assert_called_with(
            self.flavor.id,
            identity_fakes.project_id,
        )

    def test_flavor_set_no_project(self):
        arglist = [
            '--project',
            self.flavor.id,
        ]
        verifylist = [
            ('project', ''),
            ('flavor', self.flavor.id),
        ]
        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_flavor_set_no_flavor(self):
        arglist = [
            '--project', identity_fakes.project_id,
        ]
        verifylist = [
            ('project', identity_fakes.project_id),
        ]

        self.assertRaises(tests_utils.ParserException,
                          self.check_parser,
                          self.cmd,
                          arglist,
                          verifylist)

    def test_flavor_set_with_unexist_flavor(self):
        self.flavors_mock.get.side_effect = exceptions.NotFound(None)
        self.flavors_mock.find.side_effect = exceptions.NotFound(None)

        arglist = [
            '--project', identity_fakes.project_id,
            'unexist_flavor',
        ]
        verifylist = [
            ('project', identity_fakes.project_id),
            ('flavor', 'unexist_flavor'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(exceptions.CommandError,
                          self.cmd.take_action,
                          parsed_args)

    def test_flavor_set_nothing(self):
        arglist = [
            self.flavor.id,
        ]
        verifylist = [
            ('flavor', self.flavor.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(exceptions.CommandError, self.cmd.take_action,
                          parsed_args)


class TestFlavorShow(TestFlavor):

    # Return value of self.flavors_mock.find().
    flavor = compute_fakes.FakeFlavor.create_one_flavor()

    columns = (
        'OS-FLV-DISABLED:disabled',
        'OS-FLV-EXT-DATA:ephemeral',
        'disk',
        'id',
        'name',
        'os-flavor-access:is_public',
        'properties',
        'ram',
        'rxtx_factor',
        'swap',
        'vcpus',
    )

    data = (
        flavor.disabled,
        flavor.ephemeral,
        flavor.disk,
        flavor.id,
        flavor.name,
        flavor.is_public,
        utils.format_dict(flavor.get_keys()),
        flavor.ram,
        flavor.rxtx_factor,
        flavor.swap,
        flavor.vcpus,
    )

    def setUp(self):
        super(TestFlavorShow, self).setUp()

        # Return value of _find_resource()
        self.flavors_mock.find.return_value = self.flavor
        self.flavors_mock.get.side_effect = exceptions.NotFound(None)
        self.cmd = flavor.ShowFlavor(self.app, None)

    def test_show_no_options(self):
        arglist = []
        verifylist = []

        # Missing required args should boil here
        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_flavor_show(self):
        arglist = [
            self.flavor.name,
        ]
        verifylist = [
            ('flavor', self.flavor.name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)


class TestFlavorUnset(TestFlavor):

    # Return value of self.flavors_mock.find().
    flavor = compute_fakes.FakeFlavor.create_one_flavor(
        attrs={'os-flavor-access:is_public': False})

    def setUp(self):
        super(TestFlavorUnset, self).setUp()

        self.flavors_mock.find.return_value = self.flavor
        self.flavors_mock.get.side_effect = exceptions.NotFound(None)
        # Return a project
        self.projects_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.PROJECT),
            loaded=True,
        )
        self.cmd = flavor.UnsetFlavor(self.app, None)

    def test_flavor_unset_property(self):
        arglist = [
            '--property', 'property',
            'baremetal'
        ]
        verifylist = [
            ('property', ['property']),
            ('flavor', 'baremetal'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.flavors_mock.find.assert_called_with(name=parsed_args.flavor,
                                                  is_public=None)
        self.assertIsNone(result)

    def test_flavor_unset_project(self):
        arglist = [
            '--project', identity_fakes.project_id,
            self.flavor.id,
        ]
        verifylist = [
            ('project', identity_fakes.project_id),
            ('flavor', self.flavor.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        self.flavor_access_mock.remove_tenant_access.assert_called_with(
            self.flavor.id,
            identity_fakes.project_id,
        )

    def test_flavor_unset_no_project(self):
        arglist = [
            '--project', '',
            self.flavor.id,
        ]
        verifylist = [
            ('project', ''),
            ('flavor', self.flavor.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(exceptions.CommandError, self.cmd.take_action,
                          parsed_args)

    def test_flavor_unset_no_flavor(self):
        arglist = [
            '--project', identity_fakes.project_id,
        ]
        verifylist = [
            ('project', identity_fakes.project_id),
        ]

        self.assertRaises(tests_utils.ParserException,
                          self.check_parser,
                          self.cmd,
                          arglist,
                          verifylist)

    def test_flavor_unset_with_unexist_flavor(self):
        self.flavors_mock.get.side_effect = exceptions.NotFound(None)
        self.flavors_mock.find.side_effect = exceptions.NotFound(None)

        arglist = [
            '--project', identity_fakes.project_id,
            'unexist_flavor',
        ]
        verifylist = [
            ('project', identity_fakes.project_id),
            ('flavor', 'unexist_flavor'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(exceptions.CommandError,
                          self.cmd.take_action,
                          parsed_args)

    def test_flavor_unset_nothing(self):
        arglist = [
            self.flavor.id,
        ]
        verifylist = [
            ('flavor', self.flavor.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(exceptions.CommandError, self.cmd.take_action,
                          parsed_args)
