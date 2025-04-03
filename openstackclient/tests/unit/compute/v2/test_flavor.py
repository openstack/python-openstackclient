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
from unittest import mock

from openstack.compute.v2 import flavor as _flavor
from openstack import exceptions as sdk_exceptions
from osc_lib.cli import format_columns
from osc_lib import exceptions

from openstackclient.compute.v2 import flavor
from openstackclient.tests.unit.compute.v2 import fakes as compute_fakes
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes
from openstackclient.tests.unit import utils as tests_utils


class TestFlavor(compute_fakes.TestComputev2):
    def setUp(self):
        super().setUp()

        self.projects_mock = self.identity_client.projects
        self.projects_mock.reset_mock()


class TestFlavorCreate(TestFlavor):
    flavor = compute_fakes.create_one_flavor(attrs={'links': 'flavor-links'})
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
        flavor.is_disabled,
        flavor.ephemeral,
        flavor.description,
        flavor.disk,
        flavor.id,
        flavor.name,
        flavor.is_public,
        format_columns.DictColumn(flavor.extra_specs),
        flavor.ram,
        flavor.rxtx_factor,
        flavor.swap,
        flavor.vcpus,
    )
    data_private = (
        flavor.is_disabled,
        flavor.ephemeral,
        flavor.description,
        flavor.disk,
        flavor.id,
        flavor.name,
        False,
        format_columns.DictColumn(flavor.extra_specs),
        flavor.ram,
        flavor.rxtx_factor,
        flavor.swap,
        flavor.vcpus,
    )

    def setUp(self):
        super().setUp()

        # Return a project
        self.projects_mock.get.return_value = self.project
        self.compute_client.create_flavor.return_value = self.flavor
        self.cmd = flavor.CreateFlavor(self.app, None)

    def test_flavor_create_default_options(self):
        arglist = [self.flavor.name]
        verifylist = [
            ('name', self.flavor.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        default_args = {
            'name': self.flavor.name,
            'ram': 256,
            'vcpus': 1,
            'disk': 0,
            'id': None,
            'ephemeral': 0,
            'swap': 0,
            'rxtx_factor': 1.0,
            'is_public': True,
        }

        columns, data = self.cmd.take_action(parsed_args)
        self.compute_client.create_flavor.assert_called_once_with(
            **default_args
        )

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_flavor_create_all_options(self):
        self.set_compute_api_version('2.55')

        arglist = [
            '--id',
            self.flavor.id,
            '--ram',
            str(self.flavor.ram),
            '--disk',
            str(self.flavor.disk),
            '--ephemeral',
            str(self.flavor.ephemeral),
            '--swap',
            str(self.flavor.swap),
            '--vcpus',
            str(self.flavor.vcpus),
            '--rxtx-factor',
            str(self.flavor.rxtx_factor),
            '--public',
            '--description',
            str(self.flavor.description),
            '--property',
            'property=value',
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
            ('properties', {'property': 'value'}),
            ('name', self.flavor.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        args = {
            'name': self.flavor.name,
            'ram': self.flavor.ram,
            'vcpus': self.flavor.vcpus,
            'disk': self.flavor.disk,
            'id': self.flavor.id,
            'ephemeral': self.flavor.ephemeral,
            'swap': self.flavor.swap,
            'rxtx_factor': self.flavor.rxtx_factor,
            'is_public': self.flavor.is_public,
            'description': self.flavor.description,
        }

        props = {'property': 'value'}

        # SDK updates the flavor object instance. In order to make the
        # verification clear and preciese let's create new flavor and change
        # expected props this way
        create_flavor = _flavor.Flavor(**self.flavor)
        expected_flavor = _flavor.Flavor(**self.flavor)
        expected_flavor.extra_specs = props
        # convert expected data tuple to list to be able to modify it
        cmp_data = list(self.data)
        cmp_data[7] = format_columns.DictColumn(props)
        self.compute_client.create_flavor.return_value = create_flavor
        self.compute_client.create_flavor_extra_specs.return_value = (
            expected_flavor
        )

        columns, data = self.cmd.take_action(parsed_args)
        self.compute_client.create_flavor.assert_called_once_with(**args)
        self.compute_client.create_flavor_extra_specs.assert_called_once_with(
            create_flavor, props
        )
        self.compute_client.get_flavor_access.assert_not_called()

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(tuple(cmp_data), data)

    def test_flavor_create_other_options(self):
        self.set_compute_api_version('2.55')

        self.flavor.is_public = False
        arglist = [
            '--id',
            'auto',
            '--ram',
            str(self.flavor.ram),
            '--disk',
            str(self.flavor.disk),
            '--ephemeral',
            str(self.flavor.ephemeral),
            '--swap',
            str(self.flavor.swap),
            '--vcpus',
            str(self.flavor.vcpus),
            '--rxtx-factor',
            str(self.flavor.rxtx_factor),
            '--private',
            '--description',
            str(self.flavor.description),
            '--project',
            self.project.id,
            '--property',
            'key1=value1',
            '--property',
            'key2=value2',
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
            ('properties', {'key1': 'value1', 'key2': 'value2'}),
            ('name', self.flavor.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        args = {
            'name': self.flavor.name,
            'ram': self.flavor.ram,
            'vcpus': self.flavor.vcpus,
            'disk': self.flavor.disk,
            'id': 'auto',
            'ephemeral': self.flavor.ephemeral,
            'swap': self.flavor.swap,
            'rxtx_factor': self.flavor.rxtx_factor,
            'is_public': False,
            'description': self.flavor.description,
        }

        props = {'key1': 'value1', 'key2': 'value2'}

        # SDK updates the flavor object instance. In order to make the
        # verification clear and preciese let's create new flavor and change
        # expected props this way
        create_flavor = _flavor.Flavor(**self.flavor)
        expected_flavor = _flavor.Flavor(**self.flavor)
        expected_flavor.extra_specs = props
        expected_flavor.is_public = False
        # convert expected data tuple to list to be able to modify it
        cmp_data = list(self.data_private)
        cmp_data[7] = format_columns.DictColumn(props)
        self.compute_client.create_flavor.return_value = create_flavor
        self.compute_client.create_flavor_extra_specs.return_value = (
            expected_flavor
        )

        columns, data = self.cmd.take_action(parsed_args)

        self.compute_client.create_flavor.assert_called_once_with(**args)
        self.compute_client.flavor_add_tenant_access.assert_called_with(
            self.flavor.id,
            self.project.id,
        )
        self.compute_client.create_flavor_extra_specs.assert_called_with(
            create_flavor, props
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(cmp_data, data)

    def test_public_flavor_create_with_project(self):
        arglist = [
            '--project',
            self.project.id,
            self.flavor.name,
        ]
        verifylist = [
            ('project', self.project.id),
            ('name', self.flavor.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

    def test_flavor_create_no_options(self):
        arglist = []
        verifylist = None
        self.assertRaises(
            tests_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_flavor_create_with_description(self):
        self.set_compute_api_version('2.55')

        arglist = [
            '--id',
            self.flavor.id,
            '--ram',
            str(self.flavor.ram),
            '--disk',
            str(self.flavor.disk),
            '--ephemeral',
            str(self.flavor.ephemeral),
            '--swap',
            str(self.flavor.swap),
            '--vcpus',
            str(self.flavor.vcpus),
            '--rxtx-factor',
            str(self.flavor.rxtx_factor),
            '--private',
            '--description',
            'fake description',
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

        columns, data = self.cmd.take_action(parsed_args)

        args = {
            'name': self.flavor.name,
            'ram': self.flavor.ram,
            'vcpus': self.flavor.vcpus,
            'disk': self.flavor.disk,
            'id': self.flavor.id,
            'ephemeral': self.flavor.ephemeral,
            'swap': self.flavor.swap,
            'rxtx_factor': self.flavor.rxtx_factor,
            'is_public': self.flavor.is_public,
            'description': 'fake description',
        }

        self.compute_client.create_flavor.assert_called_once_with(**args)

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data_private, data)

    def test_flavor_create_with_description_pre_v255(self):
        self.set_compute_api_version('2.54')

        arglist = [
            '--id',
            self.flavor.id,
            '--ram',
            str(self.flavor.ram),
            '--vcpus',
            str(self.flavor.vcpus),
            '--description',
            'description',
            self.flavor.name,
        ]
        verifylist = [
            ('ram', self.flavor.ram),
            ('vcpus', self.flavor.vcpus),
            ('description', 'description'),
            ('name', self.flavor.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )


class TestFlavorDelete(TestFlavor):
    flavors = compute_fakes.create_flavors(count=2)

    def setUp(self):
        super().setUp()

        self.compute_client.delete_flavor.return_value = None

        self.cmd = flavor.DeleteFlavor(self.app, None)

    def test_flavor_delete(self):
        arglist = [self.flavors[0].id]
        verifylist = [
            ('flavor', [self.flavors[0].id]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.compute_client.find_flavor.return_value = self.flavors[0]

        result = self.cmd.take_action(parsed_args)

        self.compute_client.find_flavor.assert_called_with(
            self.flavors[0].id, ignore_missing=False
        )
        self.compute_client.delete_flavor.assert_called_with(
            self.flavors[0].id
        )
        self.assertIsNone(result)

    def test_delete_multiple_flavors(self):
        arglist = []
        for f in self.flavors:
            arglist.append(f.id)
        verifylist = [
            ('flavor', arglist),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.compute_client.find_flavor.side_effect = self.flavors

        result = self.cmd.take_action(parsed_args)

        find_calls = [
            mock.call(i.id, ignore_missing=False) for i in self.flavors
        ]
        delete_calls = [mock.call(i.id) for i in self.flavors]
        self.compute_client.find_flavor.assert_has_calls(find_calls)
        self.compute_client.delete_flavor.assert_has_calls(delete_calls)
        self.assertIsNone(result)

    def test_multi_flavors_delete_with_exception(self):
        arglist = [
            self.flavors[0].id,
            'unexist_flavor',
        ]
        verifylist = [('flavor', [self.flavors[0].id, 'unexist_flavor'])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.compute_client.find_flavor.side_effect = [
            self.flavors[0],
            sdk_exceptions.ResourceNotFound,
        ]

        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual('1 of 2 flavors failed to delete.', str(e))

        find_calls = [
            mock.call(self.flavors[0].id, ignore_missing=False),
            mock.call('unexist_flavor', ignore_missing=False),
        ]
        delete_calls = [mock.call(self.flavors[0].id)]
        self.compute_client.find_flavor.assert_has_calls(find_calls)
        self.compute_client.delete_flavor.assert_has_calls(delete_calls)


class TestFlavorList(TestFlavor):
    _flavor = compute_fakes.create_one_flavor()

    columns = (
        'ID',
        'Name',
        'RAM',
        'Disk',
        'Ephemeral',
        'VCPUs',
        'Is Public',
    )
    columns_long = columns + ('Swap', 'RXTX Factor', 'Properties')

    data = (
        (
            _flavor.id,
            _flavor.name,
            _flavor.ram,
            _flavor.disk,
            _flavor.ephemeral,
            _flavor.vcpus,
            _flavor.is_public,
        ),
    )
    data_long = (
        data[0]
        + (
            _flavor.swap,
            _flavor.rxtx_factor,
            format_columns.DictColumn(_flavor.extra_specs),
        ),
    )

    def setUp(self):
        super().setUp()

        self.api_mock = mock.Mock()
        self.api_mock.side_effect = [
            [self._flavor],
            [],
        ]

        self.compute_client.flavors = self.api_mock

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
        }

        self.compute_client.flavors.assert_called_with(**kwargs)
        self.compute_client.fetch_flavor_extra_specs.assert_not_called()

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, tuple(data))

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
        }

        self.compute_client.flavors.assert_called_with(**kwargs)
        self.compute_client.fetch_flavor_extra_specs.assert_not_called()

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, tuple(data))

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
        }

        self.compute_client.flavors.assert_called_with(**kwargs)
        self.compute_client.fetch_flavor_extra_specs.assert_not_called()

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, tuple(data))

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
        }

        self.compute_client.flavors.assert_called_with(**kwargs)
        self.compute_client.fetch_flavor_extra_specs.assert_not_called()

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, tuple(data))

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
        }

        self.compute_client.flavors.assert_called_with(**kwargs)
        self.compute_client.fetch_flavor_extra_specs.assert_not_called()

        self.assertEqual(self.columns_long, columns)
        self.assertCountEqual(self.data_long, tuple(data))

    def test_flavor_list_long_no_extra_specs(self):
        # use flavor with no extra specs for this test
        flavor = compute_fakes.create_one_flavor(attrs={"extra_specs": {}})
        self.data = (
            (
                flavor.id,
                flavor.name,
                flavor.ram,
                flavor.disk,
                flavor.ephemeral,
                flavor.vcpus,
                flavor.is_public,
            ),
        )
        self.data_long = (
            self.data[0]
            + (
                flavor.swap,
                flavor.rxtx_factor,
                format_columns.DictColumn(flavor.extra_specs),
            ),
        )
        self.api_mock.side_effect = [
            [flavor],
            [],
        ]

        self.compute_client.flavors = self.api_mock
        self.compute_client.fetch_flavor_extra_specs = mock.Mock(
            return_value=None
        )

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
        }

        self.compute_client.flavors.assert_called_with(**kwargs)
        self.compute_client.fetch_flavor_extra_specs.assert_called_once_with(
            flavor
        )

        self.assertEqual(self.columns_long, columns)
        self.assertCountEqual(self.data_long, tuple(data))

    def test_flavor_list_min_disk_min_ram(self):
        arglist = [
            '--min-disk',
            '10',
            '--min-ram',
            '2048',
        ]
        verifylist = [
            ('min_disk', 10),
            ('min_ram', 2048),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # In base command class Lister in cliff, abstract method take_action()
        # returns a tuple containing the column names and an iterable
        # containing the data to be listed.
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'is_public': True,
            'min_disk': 10,
            'min_ram': 2048,
        }

        self.compute_client.flavors.assert_called_with(**kwargs)
        self.compute_client.fetch_flavor_extra_specs.assert_not_called()

        self.assertEqual(self.columns, columns)
        self.assertEqual(tuple(self.data), tuple(data))


class TestFlavorSet(TestFlavor):
    # Return value of self.compute_client.find_flavor().
    flavor = compute_fakes.create_one_flavor(
        attrs={'os-flavor-access:is_public': False}
    )
    project = identity_fakes.FakeProject.create_one_project()

    def setUp(self):
        super().setUp()

        self.compute_client.find_flavor.return_value = self.flavor
        # Return a project
        self.projects_mock.get.return_value = self.project
        self.cmd = flavor.SetFlavor(self.app, None)

    def test_flavor_set_property(self):
        arglist = ['--property', 'FOO="B A R"', 'baremetal']
        verifylist = [
            ('properties', {'FOO': '"B A R"'}),
            ('flavor', 'baremetal'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.compute_client.find_flavor.assert_called_with(
            parsed_args.flavor, get_extra_specs=True, ignore_missing=False
        )
        self.compute_client.create_flavor_extra_specs.assert_called_with(
            self.flavor.id, {'FOO': '"B A R"'}
        )
        self.assertIsNone(result)

    def test_flavor_set_no_property(self):
        arglist = ['--no-property', 'baremetal']
        verifylist = [('no_property', True), ('flavor', 'baremetal')]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.compute_client.find_flavor.assert_called_with(
            parsed_args.flavor, get_extra_specs=True, ignore_missing=False
        )
        self.compute_client.delete_flavor_extra_specs_property.assert_called_with(
            self.flavor.id, 'property'
        )
        self.assertIsNone(result)

    def test_flavor_set_project(self):
        arglist = [
            '--project',
            self.project.id,
            self.flavor.id,
        ]
        verifylist = [
            ('project', self.project.id),
            ('flavor', self.flavor.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.compute_client.find_flavor.assert_called_with(
            parsed_args.flavor, get_extra_specs=True, ignore_missing=False
        )
        self.compute_client.flavor_add_tenant_access.assert_called_with(
            self.flavor.id,
            self.project.id,
        )
        self.compute_client.create_flavor_extra_specs.assert_not_called()
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
        self.assertRaises(
            tests_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_flavor_set_no_flavor(self):
        arglist = [
            '--project',
            self.project.id,
        ]
        verifylist = [
            ('project', self.project.id),
        ]
        self.assertRaises(
            tests_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_flavor_set_with_unexist_flavor(self):
        self.compute_client.find_flavor.side_effect = [
            sdk_exceptions.ResourceNotFound()
        ]

        arglist = [
            '--project',
            self.project.id,
            'unexist_flavor',
        ]
        verifylist = [
            ('project', self.project.id),
            ('flavor', 'unexist_flavor'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

    def test_flavor_set_nothing(self):
        arglist = [
            self.flavor.id,
        ]
        verifylist = [
            ('flavor', self.flavor.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.compute_client.find_flavor.assert_called_with(
            parsed_args.flavor, get_extra_specs=True, ignore_missing=False
        )
        self.compute_client.flavor_add_tenant_access.assert_not_called()
        self.assertIsNone(result)

    def test_flavor_set_description(self):
        self.set_compute_api_version('2.55')

        arglist = [
            '--description',
            'description',
            self.flavor.id,
        ]
        verifylist = [
            ('description', 'description'),
            ('flavor', self.flavor.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.compute_client.update_flavor.assert_called_with(
            flavor=self.flavor.id, description='description'
        )
        self.assertIsNone(result)

    def test_flavor_set_description_pre_v254(self):
        self.set_compute_api_version('2.54')

        arglist = [
            '--description',
            'description',
            self.flavor.id,
        ]
        verifylist = [
            ('description', 'description'),
            ('flavor', self.flavor.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

    def test_flavor_set_description_using_name(self):
        self.set_compute_api_version('2.55')

        arglist = [
            '--description',
            'description',
            self.flavor.name,
        ]
        verifylist = [
            ('description', 'description'),
            ('flavor', self.flavor.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.compute_client.update_flavor.assert_called_with(
            flavor=self.flavor.id, description='description'
        )
        self.assertIsNone(result)

    def test_flavor_set_description_using_name_pre_v255(self):
        self.set_compute_api_version('2.54')

        arglist = [
            '--description',
            'description',
            self.flavor.name,
        ]
        verifylist = [
            ('description', 'description'),
            ('flavor', self.flavor.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )


class TestFlavorShow(TestFlavor):
    # Return value of self.compute_client.find_flavor().
    flavor_access = compute_fakes.create_one_flavor_access()
    flavor = compute_fakes.create_one_flavor()

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
        flavor.is_disabled,
        flavor.ephemeral,
        None,
        flavor.description,
        flavor.disk,
        flavor.id,
        flavor.name,
        flavor.is_public,
        format_columns.DictColumn(flavor.extra_specs),
        flavor.ram,
        flavor.rxtx_factor,
        flavor.swap,
        flavor.vcpus,
    )

    def setUp(self):
        super().setUp()

        # Return value of _find_resource()
        self.compute_client.find_flavor.return_value = self.flavor
        self.compute_client.get_flavor_access.return_value = [
            self.flavor_access
        ]
        self.cmd = flavor.ShowFlavor(self.app, None)

    def test_show_no_options(self):
        arglist = []
        verifylist = []

        # Missing required args should boil here
        self.assertRaises(
            tests_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

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
        self.assertCountEqual(self.data, data)

    def test_private_flavor_show(self):
        private_flavor = compute_fakes.create_one_flavor(
            attrs={
                'os-flavor-access:is_public': False,
            }
        )
        self.compute_client.find_flavor.return_value = private_flavor

        arglist = [
            private_flavor.name,
        ]
        verifylist = [
            ('flavor', private_flavor.name),
        ]

        data_with_project = (
            private_flavor.is_disabled,
            private_flavor.ephemeral,
            [self.flavor_access.tenant_id],
            private_flavor.description,
            private_flavor.disk,
            private_flavor.id,
            private_flavor.name,
            private_flavor.is_public,
            format_columns.DictColumn(private_flavor.extra_specs),
            private_flavor.ram,
            private_flavor.rxtx_factor,
            private_flavor.swap,
            private_flavor.vcpus,
        )

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.compute_client.get_flavor_access.assert_called_with(
            flavor=private_flavor.id
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(data_with_project, data)


class TestFlavorUnset(TestFlavor):
    # Return value of self.compute_client.find_flavor().
    flavor = compute_fakes.create_one_flavor(
        attrs={'os-flavor-access:is_public': False}
    )
    project = identity_fakes.FakeProject.create_one_project()

    def setUp(self):
        super().setUp()

        self.compute_client.find_flavor.return_value = self.flavor
        # Return a project
        self.projects_mock.get.return_value = self.project
        self.cmd = flavor.UnsetFlavor(self.app, None)

        self.mock_shortcut = (
            self.compute_client.delete_flavor_extra_specs_property
        )

    def test_flavor_unset_property(self):
        arglist = ['--property', 'property', 'baremetal']
        verifylist = [
            ('properties', ['property']),
            ('flavor', 'baremetal'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.compute_client.find_flavor.assert_called_with(
            parsed_args.flavor, get_extra_specs=True, ignore_missing=False
        )
        self.mock_shortcut.assert_called_with(self.flavor.id, 'property')
        self.compute_client.flavor_remove_tenant_access.assert_not_called()
        self.assertIsNone(result)

    def test_flavor_unset_properties(self):
        arglist = [
            '--property',
            'property1',
            '--property',
            'property2',
            'baremetal',
        ]
        verifylist = [
            ('properties', ['property1', 'property2']),
            ('flavor', 'baremetal'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.compute_client.find_flavor.assert_called_with(
            parsed_args.flavor, get_extra_specs=True, ignore_missing=False
        )
        calls = [
            mock.call(self.flavor.id, 'property1'),
            mock.call(self.flavor.id, 'property2'),
        ]
        self.mock_shortcut.assert_has_calls(calls)

        # A bit tricky way to ensure we do not unset other properties
        calls.append(mock.call(self.flavor.id, 'property'))
        self.assertRaises(
            AssertionError, self.mock_shortcut.assert_has_calls, calls
        )

        self.compute_client.flavor_remove_tenant_access.assert_not_called()

    def test_flavor_unset_project(self):
        arglist = [
            '--project',
            self.project.id,
            self.flavor.id,
        ]
        verifylist = [
            ('project', self.project.id),
            ('flavor', self.flavor.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        self.compute_client.find_flavor.assert_called_with(
            parsed_args.flavor, get_extra_specs=True, ignore_missing=False
        )
        self.compute_client.flavor_remove_tenant_access.assert_called_with(
            self.flavor.id,
            self.project.id,
        )
        self.compute_client.delete_flavor_extra_specs_property.assert_not_called()
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
        self.assertRaises(
            tests_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_flavor_unset_no_flavor(self):
        arglist = [
            '--project',
            self.project.id,
        ]
        verifylist = [
            ('project', self.project.id),
        ]
        self.assertRaises(
            tests_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_flavor_unset_with_unexist_flavor(self):
        self.compute_client.find_flavor.side_effect = [
            sdk_exceptions.ResourceNotFound
        ]

        arglist = [
            '--project',
            self.project.id,
            'unexist_flavor',
        ]
        verifylist = [
            ('project', self.project.id),
            ('flavor', 'unexist_flavor'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

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

        self.compute_client.flavor_remove_tenant_access.assert_not_called()
