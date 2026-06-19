# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from openstack.block_storage.v3 import group_type as _group_type
from openstack.test import fakes as sdk_fakes
from osc_lib.cli import format_columns
from osc_lib import exceptions

from openstackclient.tests.unit.volume.v3 import fakes as volume_fakes
from openstackclient.volume.v3 import volume_group_type


class TestVolumeGroupType(volume_fakes.TestVolume):
    def setUp(self):
        super().setUp()
        self.set_volume_api_version('3.11')


class TestVolumeGroupTypeCreate(TestVolumeGroupType):
    fake_volume_group_type = sdk_fakes.generate_fake_resource(
        _group_type.GroupType
    )

    columns = (
        'ID',
        'Name',
        'Description',
        'Is Public',
        'Properties',
    )
    data = (
        fake_volume_group_type.id,
        fake_volume_group_type.name,
        fake_volume_group_type.description,
        fake_volume_group_type.is_public,
        format_columns.DictColumn(fake_volume_group_type.group_specs),
    )

    def setUp(self):
        super().setUp()

        self.volume_sdk_client.create_group_type.return_value = (
            self.fake_volume_group_type
        )

        self.cmd = volume_group_type.CreateVolumeGroupType(self.app, None)

    def test_volume_group_type_create(self):
        arglist = [
            self.fake_volume_group_type.name,
        ]
        verifylist = [
            ('name', self.fake_volume_group_type.name),
            ('description', None),
            ('is_public', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.create_group_type.assert_called_once_with(
            name=self.fake_volume_group_type.name,
            description=None,
            is_public=True,
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_volume_group_type_create_with_options(self):
        arglist = [
            self.fake_volume_group_type.name,
            '--description',
            'foo',
            '--private',
        ]
        verifylist = [
            ('name', self.fake_volume_group_type.name),
            ('description', 'foo'),
            ('is_public', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.create_group_type.assert_called_once_with(
            name=self.fake_volume_group_type.name,
            description='foo',
            is_public=False,
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_volume_group_type_create_pre_v311(self):
        self.set_volume_api_version('3.10')

        arglist = [
            self.fake_volume_group_type.name,
        ]
        verifylist = [
            ('name', self.fake_volume_group_type.name),
            ('description', None),
            ('is_public', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-volume-api-version 3.11 or greater is required', str(exc)
        )


class TestVolumeGroupTypeDelete(TestVolumeGroupType):
    fake_volume_group_type = sdk_fakes.generate_fake_resource(
        _group_type.GroupType
    )

    def setUp(self):
        super().setUp()

        self.volume_sdk_client.find_group_type.return_value = (
            self.fake_volume_group_type
        )
        self.volume_sdk_client.delete_group_type.return_value = None

        self.cmd = volume_group_type.DeleteVolumeGroupType(self.app, None)

    def test_volume_group_type_delete(self):
        arglist = [
            self.fake_volume_group_type.id,
        ]
        verifylist = [
            ('group_type', self.fake_volume_group_type.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.find_group_type.assert_called_once_with(
            self.fake_volume_group_type.id,
            ignore_missing=False,
        )
        self.volume_sdk_client.delete_group_type.assert_called_once_with(
            self.fake_volume_group_type,
        )
        self.assertIsNone(result)

    def test_volume_group_type_delete_pre_v311(self):
        self.set_volume_api_version('3.10')

        arglist = [
            self.fake_volume_group_type.id,
        ]
        verifylist = [
            ('group_type', self.fake_volume_group_type.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-volume-api-version 3.11 or greater is required', str(exc)
        )


class TestVolumeGroupTypeSet(TestVolumeGroupType):
    fake_volume_group_type = sdk_fakes.generate_fake_resource(
        _group_type.GroupType, group_specs={'foo': 'bar'}
    )

    columns = (
        'ID',
        'Name',
        'Description',
        'Is Public',
        'Properties',
    )
    data = (
        fake_volume_group_type.id,
        fake_volume_group_type.name,
        fake_volume_group_type.description,
        fake_volume_group_type.is_public,
        format_columns.DictColumn(fake_volume_group_type.group_specs),
    )

    def setUp(self):
        super().setUp()

        self.volume_sdk_client.find_group_type.return_value = (
            self.fake_volume_group_type
        )
        self.volume_sdk_client.update_group_type.return_value = (
            self.fake_volume_group_type
        )

        self.cmd = volume_group_type.SetVolumeGroupType(self.app, None)

    def test_volume_group_type_set(self):
        arglist = [
            self.fake_volume_group_type.id,
            '--name',
            'foo',
            '--description',
            'hello, world',
            '--public',
            '--property',
            'fizz=buzz',
        ]
        verifylist = [
            ('group_type', self.fake_volume_group_type.id),
            ('name', 'foo'),
            ('description', 'hello, world'),
            ('is_public', True),
            ('no_property', False),
            ('properties', {'fizz': 'buzz'}),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.update_group_type.assert_called_once_with(
            self.fake_volume_group_type.id,
            name='foo',
            description='hello, world',
            is_public=True,
        )
        self.volume_sdk_client.create_group_type_group_specs.assert_called_once_with(
            self.fake_volume_group_type.id,
            {'fizz': 'buzz'},
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_volume_group_type_with_no_property_option(self):
        arglist = [
            self.fake_volume_group_type.id,
            '--no-property',
            '--property',
            'fizz=buzz',
        ]
        verifylist = [
            ('group_type', self.fake_volume_group_type.id),
            ('name', None),
            ('description', None),
            ('is_public', None),
            ('no_property', True),
            ('properties', {'fizz': 'buzz'}),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.delete_group_type_group_specs_property.assert_called_once_with(
            self.fake_volume_group_type.id,
            'foo',
        )
        self.volume_sdk_client.create_group_type_group_specs.assert_called_once_with(
            self.fake_volume_group_type.id,
            {'fizz': 'buzz'},
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_volume_group_type_set_pre_v311(self):
        self.set_volume_api_version('3.10')

        arglist = [
            self.fake_volume_group_type.id,
            '--name',
            'foo',
            '--description',
            'hello, world',
        ]
        verifylist = [
            ('group_type', self.fake_volume_group_type.id),
            ('name', 'foo'),
            ('description', 'hello, world'),
            ('is_public', None),
            ('no_property', False),
            ('properties', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-volume-api-version 3.11 or greater is required', str(exc)
        )


class TestVolumeGroupTypeUnset(TestVolumeGroupType):
    fake_volume_group_type = sdk_fakes.generate_fake_resource(
        _group_type.GroupType
    )

    columns = (
        'ID',
        'Name',
        'Description',
        'Is Public',
        'Properties',
    )
    data = (
        fake_volume_group_type.id,
        fake_volume_group_type.name,
        fake_volume_group_type.description,
        fake_volume_group_type.is_public,
        format_columns.DictColumn(fake_volume_group_type.group_specs),
    )

    def setUp(self):
        super().setUp()

        self.volume_sdk_client.find_group_type.return_value = (
            self.fake_volume_group_type
        )

        self.cmd = volume_group_type.UnsetVolumeGroupType(self.app, None)

    def test_volume_group_type_unset(self):
        arglist = [
            self.fake_volume_group_type.id,
            '--property',
            'fizz',
        ]
        verifylist = [
            ('group_type', self.fake_volume_group_type.id),
            ('properties', ['fizz']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.delete_group_type_group_specs_property.assert_called_once_with(
            self.fake_volume_group_type.id,
            'fizz',
        )
        self.volume_sdk_client.find_group_type.assert_called_once_with(
            self.fake_volume_group_type.id,
            ignore_missing=False,
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_volume_group_type_unset_pre_v311(self):
        self.set_volume_api_version('3.10')

        arglist = [
            self.fake_volume_group_type.id,
            '--property',
            'fizz',
        ]
        verifylist = [
            ('group_type', self.fake_volume_group_type.id),
            ('properties', ['fizz']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-volume-api-version 3.11 or greater is required', str(exc)
        )


class TestVolumeGroupTypeList(TestVolumeGroupType):
    fake_volume_group_types = list(
        sdk_fakes.generate_fake_resources(_group_type.GroupType, count=2)
    )

    columns = (
        'ID',
        'Name',
        'Is Public',
        'Group Specs',
    )
    data = [
        (
            fake_volume_group_type.id,
            fake_volume_group_type.name,
            fake_volume_group_type.is_public,
            format_columns.DictColumn(fake_volume_group_type.group_specs),
        )
        for fake_volume_group_type in fake_volume_group_types
    ]

    def setUp(self):
        super().setUp()

        self.volume_sdk_client.group_types.return_value = (
            self.fake_volume_group_types
        )
        self.volume_sdk_client.get_group_type.return_value = (
            self.fake_volume_group_types[0]
        )

        self.cmd = volume_group_type.ListVolumeGroupType(self.app, None)

    def test_volume_group_type_list(self):
        arglist = []
        verifylist = [
            ('show_default', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.group_types.assert_called_once_with()
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(tuple(self.data), data)

    def test_volume_group_type_list_with_default_option(self):
        arglist = [
            '--default',
        ]
        verifylist = [
            ('show_default', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.get_group_type.assert_called_once_with(
            'default'
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(
            tuple([self.data[0]]),
            data,
        )

    def test_volume_group_type_list_pre_v311(self):
        self.set_volume_api_version('3.10')

        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-volume-api-version 3.11 or greater is required', str(exc)
        )


class TestVolumeGroupTypeShow(TestVolumeGroupType):
    fake_volume_group_type = sdk_fakes.generate_fake_resource(
        _group_type.GroupType
    )

    columns = (
        'ID',
        'Name',
        'Description',
        'Is Public',
        'Properties',
    )
    data = (
        fake_volume_group_type.id,
        fake_volume_group_type.name,
        fake_volume_group_type.description,
        fake_volume_group_type.is_public,
        format_columns.DictColumn(fake_volume_group_type.group_specs),
    )

    def setUp(self):
        super().setUp()

        self.volume_sdk_client.find_group_type.return_value = (
            self.fake_volume_group_type
        )

        self.cmd = volume_group_type.ShowVolumeGroupType(self.app, None)

    def test_volume_group_type_show(self):
        arglist = [
            self.fake_volume_group_type.id,
        ]
        verifylist = [
            ('group_type', self.fake_volume_group_type.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.find_group_type.assert_called_once_with(
            self.fake_volume_group_type.id,
            ignore_missing=False,
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_volume_group_type_show_pre_v311(self):
        self.set_volume_api_version('3.10')

        arglist = [
            self.fake_volume_group_type.id,
        ]
        verifylist = [
            ('group_type', self.fake_volume_group_type.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-volume-api-version 3.11 or greater is required', str(exc)
        )
