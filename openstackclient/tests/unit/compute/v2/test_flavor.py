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

import mock
from mock import call

import novaclient
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.compute.v2 import flavor
from openstackclient.tests.unit.compute.v2 import fakes as compute_fakes
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes
from openstackclient.tests.unit import utils as tests_utils


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
    project = identity_fakes.FakeProject.create_one_project()
    columns = (
        'OS-FLV-DISABLED:disabled',
        'OS-FLV-EXT-DATA:ephemeral',
        'description',
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
        flavor.description,
        flavor.disk,
        flavor.id,
        flavor.name,
        flavor.is_public,
        utils.format_dict(flavor.properties),
        flavor.ram,
        flavor.rxtx_factor,
        flavor.swap,
        flavor.vcpus,
    )

    def setUp(self):
        super(TestFlavorCreate, self).setUp()

        # Return a project
        self.projects_mock.get.return_value = self.project
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
            True,
            None,
        )
        columns, data = self.cmd.take_action(parsed_args)
        self.flavors_mock.create.assert_called_once_with(*default_args)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_flavor_create_all_options(self):

        arglist = [
            '--id', self.flavor.id,
            '--ram', str(self.flavor.ram),
            '--disk', str(self.flavor.disk),
            '--ephemeral', str(self.flavor.ephemeral),
            '--swap', str(self.flavor.swap),
            '--vcpus', str(self.flavor.vcpus),
            '--rxtx-factor', str(self.flavor.rxtx_factor),
            '--public',
            '--description', str(self.flavor.description),
            '--property', 'property=value',
            self.flavor.name,
        ]
        verifylist = [
            ('id', self.flavor.id),
            ('ram', self.flavor.ram),
            ('disk', self.flavor.disk),
            ('ephemeral', self.flavor.ephemeral),
            ('swap', self.flavor.swap),
            ('vcpus', self.flavor.vcpus),
            ('rxtx_factor', self.flavor.rxtx_factor),
            ('public', True),
            ('description', self.flavor.description),
            ('property', {'property': 'value'}),
            ('name', self.flavor.name),
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
            self.flavor.description,
        )
        self.app.client_manager.compute.api_version = 2.55
        with mock.patch.object(novaclient.api_versions,
                               'APIVersion',
                               return_value=2.55):
            columns, data = self.cmd.take_action(parsed_args)
        self.flavors_mock.create.assert_called_once_with(*args)
        self.flavor.set_keys.assert_called_once_with({'property': 'value'})
        self.flavor.get_keys.assert_called_once_with()

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_flavor_create_other_options(self):

        self.flavor.is_public = False
        arglist = [
            '--id', 'auto',
            '--ram', str(self.flavor.ram),
            '--disk', str(self.flavor.disk),
            '--ephemeral', str(self.flavor.ephemeral),
            '--swap', str(self.flavor.swap),
            '--vcpus', str(self.flavor.vcpus),
            '--rxtx-factor', str(self.flavor.rxtx_factor),
            '--private',
            '--description', str(self.flavor.description),
            '--project', self.project.id,
            '--property', 'key1=value1',
            '--property', 'key2=value2',
            self.flavor.name,
        ]
        verifylist = [
            ('ram', self.flavor.ram),
            ('disk', self.flavor.disk),
            ('ephemeral', self.flavor.ephemeral),
            ('swap', self.flavor.swap),
            ('vcpus', self.flavor.vcpus),
            ('rxtx_factor', self.flavor.rxtx_factor),
            ('public', False),
            ('description', 'description'),
            ('project', self.project.id),
            ('property', {'key1': 'value1', 'key2': 'value2'}),
            ('name', self.flavor.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        args = (
            self.flavor.name,
            self.flavor.ram,
            self.flavor.vcpus,
            self.flavor.disk,
            'auto',
            self.flavor.ephemeral,
            self.flavor.swap,
            self.flavor.rxtx_factor,
            self.flavor.is_public,
            self.flavor.description,
        )
        self.app.client_manager.compute.api_version = 2.55
        with mock.patch.object(novaclient.api_versions,
                               'APIVersion',
                               return_value=2.55):
            columns, data = self.cmd.take_action(parsed_args)
        self.flavors_mock.create.assert_called_once_with(*args)
        self.flavor_access_mock.add_tenant_access.assert_called_with(
            self.flavor.id,
            self.project.id,
        )
        self.flavor.set_keys.assert_called_with(
            {'key1': 'value1', 'key2': 'value2'})
        self.flavor.get_keys.assert_called_with()
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_public_flavor_create_with_project(self):
        arglist = [
            '--project', self.project.id,
            self.flavor.name,
        ]
        verifylist = [
            ('project', self.project.id),
            ('name', self.flavor.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(exceptions.CommandError,
                          self.cmd.take_action,
                          parsed_args)

    def test_flavor_create_no_options(self):
        arglist = []
        verifylist = None
        self.assertRaises(tests_utils.ParserException,
                          self.check_parser,
                          self.cmd,
                          arglist,
                          verifylist)

    def test_flavor_create_with_description_api_newer(self):
        arglist = [
            '--id', self.flavor.id,
            '--ram', str(self.flavor.ram),
            '--disk', str(self.flavor.disk),
            '--ephemeral', str(self.flavor.ephemeral),
            '--swap', str(self.flavor.swap),
            '--vcpus', str(self.flavor.vcpus),
            '--rxtx-factor', str(self.flavor.rxtx_factor),
            '--private',
            '--description', 'fake description',
            self.flavor.name,
        ]
        verifylist = [
            ('id', self.flavor.id),
            ('ram', self.flavor.ram),
            ('disk', self.flavor.disk),
            ('ephemeral', self.flavor.ephemeral),
            ('swap', self.flavor.swap),
            ('vcpus', self.flavor.vcpus),
            ('rxtx_factor', self.flavor.rxtx_factor),
            ('public', False),
            ('description', 'fake description'),
            ('name', self.flavor.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.app.client_manager.compute.api_version = 2.55
        with mock.patch.object(novaclient.api_versions,
                               'APIVersion',
                               return_value=2.55):
            columns, data = self.cmd.take_action(parsed_args)

        args = (
            self.flavor.name,
            self.flavor.ram,
            self.flavor.vcpus,
            self.flavor.disk,
            self.flavor.id,
            self.flavor.ephemeral,
            self.flavor.swap,
            self.flavor.rxtx_factor,
            False,
            'fake description',
        )

        self.flavors_mock.create.assert_called_once_with(*args)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_flavor_create_with_description_api_older(self):
        arglist = [
            '--id', self.flavor.id,
            '--ram', str(self.flavor.ram),
            '--vcpus', str(self.flavor.vcpus),
            '--description', 'description',
            self.flavor.name,
        ]
        verifylist = [
            ('ram', self.flavor.ram),
            ('vcpus', self.flavor.vcpus),
            ('description', 'description'),
            ('name', self.flavor.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.app.client_manager.compute.api_version = 2.54
        with mock.patch.object(novaclient.api_versions,
                               'APIVersion',
                               return_value=2.55):
            self.assertRaises(exceptions.CommandError, self.cmd.take_action,
                              parsed_args)


class TestFlavorDelete(TestFlavor):

    flavors = compute_fakes.FakeFlavor.create_flavors(count=2)

    def setUp(self):
        super(TestFlavorDelete, self).setUp()

        self.flavors_mock.get = (
            compute_fakes.FakeFlavor.get_flavors(self.flavors))
        self.flavors_mock.delete.return_value = None

        self.cmd = flavor.DeleteFlavor(self.app, None)

    def test_flavor_delete(self):
        arglist = [
            self.flavors[0].id
        ]
        verifylist = [
            ('flavor', [self.flavors[0].id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.flavors_mock.delete.assert_called_with(self.flavors[0].id)
        self.assertIsNone(result)

    def test_delete_multiple_flavors(self):
        arglist = []
        for f in self.flavors:
            arglist.append(f.id)
        verifylist = [
            ('flavor', arglist),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        calls = []
        for f in self.flavors:
            calls.append(call(f.id))
        self.flavors_mock.delete.assert_has_calls(calls)
        self.assertIsNone(result)

    def test_multi_flavors_delete_with_exception(self):
        arglist = [
            self.flavors[0].id,
            'unexist_flavor',
        ]
        verifylist = [
            ('flavor', [self.flavors[0].id, 'unexist_flavor'])
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        find_mock_result = [self.flavors[0], exceptions.CommandError]
        self.flavors_mock.get = (
            mock.Mock(side_effect=find_mock_result)
        )
        self.flavors_mock.find.side_effect = exceptions.NotFound(None)

        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual('1 of 2 flavors failed to delete.', str(e))

        self.flavors_mock.get.assert_any_call(self.flavors[0].id)
        self.flavors_mock.get.assert_any_call('unexist_flavor')
        self.flavors_mock.delete.assert_called_once_with(self.flavors[0].id)


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
    project = identity_fakes.FakeProject.create_one_project()

    def setUp(self):
        super(TestFlavorSet, self).setUp()

        self.flavors_mock.find.return_value = self.flavor
        self.flavors_mock.get.side_effect = exceptions.NotFound(None)
        # Return a project
        self.projects_mock.get.return_value = self.project
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
        self.flavor.set_keys.assert_called_with({'FOO': '"B A R"'})
        self.assertIsNone(result)

    def test_flavor_set_no_property(self):
        arglist = [
            '--no-property',
            'baremetal'
        ]
        verifylist = [
            ('no_property', True),
            ('flavor', 'baremetal')
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.flavors_mock.find.assert_called_with(name=parsed_args.flavor,
                                                  is_public=None)
        self.flavor.unset_keys.assert_called_with(['property'])
        self.assertIsNone(result)

    def test_flavor_set_project(self):
        arglist = [
            '--project', self.project.id,
            self.flavor.id,
        ]
        verifylist = [
            ('project', self.project.id),
            ('flavor', self.flavor.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.flavors_mock.find.assert_called_with(name=parsed_args.flavor,
                                                  is_public=None)
        self.flavor_access_mock.add_tenant_access.assert_called_with(
            self.flavor.id,
            self.project.id,
        )
        self.flavor.set_keys.assert_not_called()
        self.assertIsNone(result)

    def test_flavor_set_no_project(self):
        arglist = [
            '--project',
            self.flavor.id,
        ]
        verifylist = [
            ('project', None),
            ('flavor', self.flavor.id),
        ]
        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_flavor_set_no_flavor(self):
        arglist = [
            '--project', self.project.id,
        ]
        verifylist = [
            ('project', self.project.id),
        ]
        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_flavor_set_with_unexist_flavor(self):
        self.flavors_mock.get.side_effect = exceptions.NotFound(None)
        self.flavors_mock.find.side_effect = exceptions.NotFound(None)

        arglist = [
            '--project', self.project.id,
            'unexist_flavor',
        ]
        verifylist = [
            ('project', self.project.id),
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
        result = self.cmd.take_action(parsed_args)

        self.flavors_mock.find.assert_called_with(name=parsed_args.flavor,
                                                  is_public=None)
        self.flavor_access_mock.add_tenant_access.assert_not_called()
        self.assertIsNone(result)

    def test_flavor_set_description_api_newer(self):
        arglist = [
            '--description', 'description',
            self.flavor.id,
        ]
        verifylist = [
            ('description', 'description'),
            ('flavor', self.flavor.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.app.client_manager.compute.api_version = 2.55
        with mock.patch.object(novaclient.api_versions,
                               'APIVersion',
                               return_value=2.55):
            result = self.cmd.take_action(parsed_args)
            self.flavors_mock.update.assert_called_with(
                flavor=self.flavor.id, description='description')
            self.assertIsNone(result)

    def test_flavor_set_description_api_older(self):
        arglist = [
            '--description', 'description',
            self.flavor.id,
        ]
        verifylist = [
            ('description', 'description'),
            ('flavor', self.flavor.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.app.client_manager.compute.api_version = 2.54
        with mock.patch.object(novaclient.api_versions,
                               'APIVersion',
                               return_value=2.55):
            self.assertRaises(exceptions.CommandError, self.cmd.take_action,
                              parsed_args)


class TestFlavorShow(TestFlavor):

    # Return value of self.flavors_mock.find().
    flavor_access = compute_fakes.FakeFlavorAccess.create_one_flavor_access()
    flavor = compute_fakes.FakeFlavor.create_one_flavor()

    columns = (
        'OS-FLV-DISABLED:disabled',
        'OS-FLV-EXT-DATA:ephemeral',
        'access_project_ids',
        'description',
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
        None,
        flavor.description,
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
        self.flavor_access_mock.list.return_value = [self.flavor_access]
        self.cmd = flavor.ShowFlavor(self.app, None)

    def test_show_no_options(self):
        arglist = []
        verifylist = []

        # Missing required args should boil here
        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_public_flavor_show(self):
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

    def test_private_flavor_show(self):
        private_flavor = compute_fakes.FakeFlavor.create_one_flavor(
            attrs={
                'os-flavor-access:is_public': False,
            }
        )
        self.flavors_mock.find.return_value = private_flavor

        arglist = [
            private_flavor.name,
        ]
        verifylist = [
            ('flavor', private_flavor.name),
        ]

        data_with_project = (
            private_flavor.disabled,
            private_flavor.ephemeral,
            self.flavor_access.tenant_id,
            private_flavor.description,
            private_flavor.disk,
            private_flavor.id,
            private_flavor.name,
            private_flavor.is_public,
            utils.format_dict(private_flavor.get_keys()),
            private_flavor.ram,
            private_flavor.rxtx_factor,
            private_flavor.swap,
            private_flavor.vcpus,
        )

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.flavor_access_mock.list.assert_called_with(
            flavor=private_flavor.id)
        self.assertEqual(self.columns, columns)
        self.assertEqual(data_with_project, data)


class TestFlavorUnset(TestFlavor):

    # Return value of self.flavors_mock.find().
    flavor = compute_fakes.FakeFlavor.create_one_flavor(
        attrs={'os-flavor-access:is_public': False})
    project = identity_fakes.FakeProject.create_one_project()

    def setUp(self):
        super(TestFlavorUnset, self).setUp()

        self.flavors_mock.find.return_value = self.flavor
        self.flavors_mock.get.side_effect = exceptions.NotFound(None)
        # Return a project
        self.projects_mock.get.return_value = self.project
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
        self.flavor.unset_keys.assert_called_with(['property'])
        self.flavor_access_mock.remove_tenant_access.assert_not_called()
        self.assertIsNone(result)

    def test_flavor_unset_project(self):
        arglist = [
            '--project', self.project.id,
            self.flavor.id,
        ]
        verifylist = [
            ('project', self.project.id),
            ('flavor', self.flavor.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        self.flavors_mock.find.assert_called_with(name=parsed_args.flavor,
                                                  is_public=None)
        self.flavor_access_mock.remove_tenant_access.assert_called_with(
            self.flavor.id,
            self.project.id,
        )
        self.flavor.unset_keys.assert_not_called()
        self.assertIsNone(result)

    def test_flavor_unset_no_project(self):
        arglist = [
            '--project',
            self.flavor.id,
        ]
        verifylist = [
            ('project', None),
            ('flavor', self.flavor.id),
        ]
        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_flavor_unset_no_flavor(self):
        arglist = [
            '--project', self.project.id,
        ]
        verifylist = [
            ('project', self.project.id),
        ]
        self.assertRaises(tests_utils.ParserException, self.check_parser,
                          self.cmd, arglist, verifylist)

    def test_flavor_unset_with_unexist_flavor(self):
        self.flavors_mock.get.side_effect = exceptions.NotFound(None)
        self.flavors_mock.find.side_effect = exceptions.NotFound(None)

        arglist = [
            '--project', self.project.id,
            'unexist_flavor',
        ]
        verifylist = [
            ('project', self.project.id),
            ('flavor', 'unexist_flavor'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(exceptions.CommandError, self.cmd.take_action,
                          parsed_args)

    def test_flavor_unset_nothing(self):
        arglist = [
            self.flavor.id,
        ]
        verifylist = [
            ('flavor', self.flavor.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        self.flavor_access_mock.remove_tenant_access.assert_not_called()
