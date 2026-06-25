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

from unittest.mock import call

from openstack.block_storage.v3 import type as _type
from openstack import exceptions as sdk_exceptions
from openstack.identity.v3 import project as _project
from openstack.test import fakes as sdk_fakes
from osc_lib.cli import format_columns
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.tests.unit import utils as tests_utils
from openstackclient.tests.unit.volume.v3 import fakes as volume_fakes
from openstackclient.volume.v3 import volume_type


class TestTypeCreate(volume_fakes.TestVolume):
    def setUp(self):
        super().setUp()

        self.new_volume_type = sdk_fakes.generate_fake_resource(_type.Type)
        self.project = sdk_fakes.generate_fake_resource(_project.Project)
        self.columns = (
            'description',
            'id',
            'is_public',
            'name',
            'properties',
        )
        self.data = (
            self.new_volume_type.description,
            self.new_volume_type.id,
            self.new_volume_type.is_public,
            self.new_volume_type.name,
            format_columns.DictColumn(self.new_volume_type.extra_specs),
        )

        self.volume_client.create_type.return_value = self.new_volume_type
        self.identity_sdk_client.find_project.return_value = self.project

        self.cmd = volume_type.CreateVolumeType(self.app, None)

    def test_type_create_public(self):
        arglist = [
            "--description",
            self.new_volume_type.description,
            "--public",
            self.new_volume_type.name,
        ]
        verifylist = [
            ("description", self.new_volume_type.description),
            ("is_public", True),
            ("name", self.new_volume_type.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.volume_client.create_type.assert_called_with(
            name=self.new_volume_type.name,
            description=self.new_volume_type.description,
            is_public=True,
        )

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_type_create_private(self):
        arglist = [
            "--description",
            self.new_volume_type.description,
            "--private",
            "--project",
            self.project.id,
            self.new_volume_type.name,
        ]
        verifylist = [
            ("description", self.new_volume_type.description),
            ("is_public", False),
            ("project", self.project.id),
            ("name", self.new_volume_type.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.volume_client.create_type.assert_called_with(
            name=self.new_volume_type.name,
            description=self.new_volume_type.description,
            is_public=False,
        )

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_type_create_with_properties(self):
        arglist = [
            '--property',
            'myprop=myvalue',
            # this combination isn't viable server-side but is okay for testing
            '--multiattach',
            '--cacheable',
            '--replicated',
            '--availability-zone',
            'az1',
            self.new_volume_type.name,
        ]
        verifylist = [
            ('properties', {'myprop': 'myvalue'}),
            ('multiattach', True),
            ('cacheable', True),
            ('replicated', True),
            ('availability_zones', ['az1']),
            ('name', self.new_volume_type.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result_type = sdk_fakes.generate_fake_resource(
            _type.Type,
            extra_specs={
                'myprop': 'myvalue',
                'multiattach': '<is> True',
                'cacheable': '<is> True',
                'replication_enabled': '<is> True',
                'RESKEY:availability_zones': 'az1',
            },
        )
        self.volume_client.update_type_extra_specs.return_value = result_type

        columns, data = self.cmd.take_action(parsed_args)
        self.volume_client.create_type.assert_called_with(
            name=self.new_volume_type.name, description=None
        )
        self.volume_client.update_type_extra_specs.assert_called_once_with(
            self.new_volume_type.id,
            myprop='myvalue',
            multiattach='<is> True',
            cacheable='<is> True',
            replication_enabled='<is> True',
            **{'RESKEY:availability_zones': 'az1'},
        )

        expected_data = (
            self.new_volume_type.description,
            self.new_volume_type.id,
            self.new_volume_type.is_public,
            self.new_volume_type.name,
            format_columns.DictColumn(result_type.extra_specs),
        )

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(expected_data, data)

    def test_public_type_create_with_project_public(self):
        arglist = [
            '--project',
            self.project.id,
            self.new_volume_type.name,
        ]
        verifylist = [
            ('is_public', None),
            ('project', self.project.id),
            ('name', self.new_volume_type.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args,
        )

    def test_type_create_with_encryption(self):
        encryption_type = sdk_fakes.generate_fake_resource(
            _type.TypeEncryption,
            provider='LuksEncryptor',
            cipher='aes-xts-plain64',
            key_size='128',
            control_location='front-end',
        )
        self.new_volume_type = sdk_fakes.generate_fake_resource(_type.Type)
        self.volume_client.create_type.return_value = self.new_volume_type
        self.volume_client.create_type_encryption.return_value = (
            encryption_type
        )
        expected_encryption_info = {
            'provider': encryption_type.provider,
            'cipher': encryption_type.cipher,
            'key_size': encryption_type.key_size,
            'control_location': encryption_type.control_location,
            'encryption_id': encryption_type.encryption_id,
        }
        encryption_columns = (
            'description',
            'encryption',
            'id',
            'is_public',
            'name',
            'properties',
        )
        encryption_data = (
            self.new_volume_type.description,
            format_columns.DictColumn(expected_encryption_info),
            self.new_volume_type.id,
            self.new_volume_type.is_public,
            self.new_volume_type.name,
            format_columns.DictColumn(self.new_volume_type.extra_specs),
        )
        arglist = [
            '--encryption-provider',
            'LuksEncryptor',
            '--encryption-cipher',
            'aes-xts-plain64',
            '--encryption-key-size',
            '128',
            '--encryption-control-location',
            'front-end',
            self.new_volume_type.name,
        ]
        verifylist = [
            ('encryption_provider', 'LuksEncryptor'),
            ('encryption_cipher', 'aes-xts-plain64'),
            ('encryption_key_size', 128),
            ('encryption_control_location', 'front-end'),
            ('name', self.new_volume_type.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.volume_client.create_type.assert_called_with(
            name=self.new_volume_type.name,
            description=None,
        )
        self.volume_client.create_type_encryption.assert_called_with(
            self.new_volume_type,
            provider='LuksEncryptor',
            cipher='aes-xts-plain64',
            key_size=128,
            control_location='front-end',
        )
        self.assertEqual(encryption_columns, columns)
        self.assertCountEqual(encryption_data, data)


class TestTypeDelete(volume_fakes.TestVolume):
    volume_types = list(sdk_fakes.generate_fake_resources(_type.Type, count=2))

    def setUp(self):
        super().setUp()

        self.volume_client.find_type.side_effect = self.volume_types
        self.volume_client.delete_type.return_value = None

        self.cmd = volume_type.DeleteVolumeType(self.app, None)

    def test_type_delete(self):
        arglist = [self.volume_types[0].id]
        verifylist = [("volume_types", [self.volume_types[0].id])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.volume_client.find_type.assert_called_with(
            self.volume_types[0].id, ignore_missing=False
        )
        self.volume_client.delete_type.assert_called_with(self.volume_types[0])
        self.assertIsNone(result)

    def test_delete_multiple_types(self):
        arglist = []
        for t in self.volume_types:
            arglist.append(t.id)
        verifylist = [
            ('volume_types', arglist),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        calls = []
        for t in self.volume_types:
            calls.append(call(t))
        self.volume_client.delete_type.assert_has_calls(calls)
        self.assertIsNone(result)

    def test_delete_multiple_types_with_exception(self):
        arglist = [
            self.volume_types[0].id,
            'unexist_type',
        ]
        verifylist = [
            ('volume_types', arglist),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.volume_client.find_type.side_effect = [
            self.volume_types[0],
            exceptions.CommandError,
        ]
        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual('1 of 2 volume types failed to delete.', str(e))
        self.volume_client.find_type.assert_any_call(
            self.volume_types[0].id, ignore_missing=False
        )
        self.volume_client.find_type.assert_any_call(
            'unexist_type', ignore_missing=False
        )

        self.assertEqual(2, self.volume_client.find_type.call_count)
        self.volume_client.delete_type.assert_called_once_with(
            self.volume_types[0]
        )


class TestTypeList(volume_fakes.TestVolume):
    volume_types = list(sdk_fakes.generate_fake_resources(_type.Type, count=2))

    columns = [
        "ID",
        "Name",
        "Is Public",
    ]
    columns_long = [*columns, "Description", "Properties"]
    data_with_default_type = [(volume_types[0].id, volume_types[0].name, True)]
    data = []
    for t in volume_types:
        data.append(
            (
                t.id,
                t.name,
                t.is_public,
            )
        )
    data_long = []
    for t in volume_types:
        data_long.append(
            (
                t.id,
                t.name,
                t.is_public,
                t.description,
                format_columns.DictColumn(t.extra_specs),
            )
        )

    def setUp(self):
        super().setUp()

        self.volume_client.types.return_value = self.volume_types

        self.cmd = volume_type.ListVolumeType(self.app, None)

    def test_type_list_without_options(self):
        arglist = []
        verifylist = [
            ("long", False),
            ("is_public", 'none'),
            ("default", False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.volume_client.types.assert_called_once_with(is_public='none')
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))

    def test_type_list_with_options(self):
        arglist = [
            "--long",
            "--public",
        ]
        verifylist = [
            ("long", True),
            ("is_public", True),
            ("default", False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.volume_client.types.assert_called_once_with(is_public=True)
        self.assertEqual(self.columns_long, columns)
        self.assertCountEqual(self.data_long, list(data))

    def test_type_list_with_private_option(self):
        arglist = [
            "--private",
        ]
        verifylist = [
            ("long", False),
            ("is_public", False),
            ("default", False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.volume_client.types.assert_called_once_with(is_public=False)
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))

    def test_type_list_with_default_option(self):
        self.volume_client.get_type.return_value = self.volume_types[0]

        arglist = [
            "--default",
        ]
        verifylist = [
            ("encryption_type", False),
            ("long", False),
            ("is_public", 'none'),
            ("default", True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.volume_client.get_type.assert_called_once_with('default')
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data_with_default_type, list(data))

    def test_type_list_with_properties(self):
        self.set_volume_api_version('3.52')

        arglist = [
            "--property",
            "foo=bar",
            "--multiattach",
            "--cacheable",
            "--replicated",
            "--availability-zone",
            "az1",
        ]
        verifylist = [
            ("encryption_type", False),
            ("long", False),
            ("is_public", 'none'),
            ("default", False),
            ("properties", {"foo": "bar"}),
            ("multiattach", True),
            ("cacheable", True),
            ("replicated", True),
            ("availability_zones", ["az1"]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.volume_client.types.assert_called_once_with(
            is_public='none',
            foo="bar",
            multiattach="<is> True",
            cacheable="<is> True",
            replication_enabled="<is> True",
            **{"RESKEY:availability_zones": "az1"},
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))

    def test_type_list_with_properties_pre_v352(self):
        self.set_volume_api_version('3.51')

        arglist = [
            "--property",
            "foo=bar",
        ]
        verifylist = [
            ("encryption_type", False),
            ("long", False),
            ("is_public", 'none'),
            ("default", False),
            ("properties", {"foo": "bar"}),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args,
        )
        self.assertIn(
            '--os-volume-api-version 3.52 or greater is required',
            str(exc),
        )

    def test_type_list_with_encryption(self):
        encryption_types = [
            sdk_fakes.generate_fake_resource(
                _type.TypeEncryption,
                volume_type_id=vt.id,
            )
            for vt in self.volume_types
        ]
        expected_encryption_info = [
            {
                'provider': encryption_type.provider,
                'cipher': encryption_type.cipher,
                'key_size': encryption_type.key_size,
                'control_location': encryption_type.control_location,
                'encryption_id': encryption_type.encryption_id,
            }
            for encryption_type in encryption_types
        ]
        encryption_columns = [*self.columns, "Encryption"]
        encryption_data = [
            (
                self.volume_types[x].id,
                self.volume_types[x].name,
                self.volume_types[x].is_public,
                volume_type.EncryptionInfoColumn(
                    self.volume_types[x].id,
                    {self.volume_types[x].id: expected_encryption_info[x]},
                ),
            )
            for x in (0, 1)
        ]

        self.volume_client.get_type_encryption.side_effect = encryption_types
        arglist = [
            "--encryption-type",
        ]
        verifylist = [
            ("encryption_type", True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.volume_client.get_type_encryption.assert_has_calls(
            [call(self.volume_types[0].id), call(self.volume_types[1].id)],
        )
        self.volume_client.types.assert_called_once_with(is_public='none')
        self.assertEqual(encryption_columns, columns)
        self.assertCountEqual(encryption_data, list(data))


class TestTypeSet(volume_fakes.TestVolume):
    def setUp(self):
        super().setUp()

        self.project = sdk_fakes.generate_fake_resource(_project.Project)
        self.identity_sdk_client.find_project.return_value = self.project

        self.volume_type = sdk_fakes.generate_fake_resource(_type.Type)
        self.volume_client.find_type.return_value = self.volume_type
        self.volume_client.create_type_encryption.return_value = None
        self.volume_client.update_type_encryption.return_value = None

        self.cmd = volume_type.SetVolumeType(self.app, None)

    def test_type_set(self):
        arglist = [
            '--name',
            'new_name',
            '--description',
            'new_description',
            '--private',
            self.volume_type.id,
        ]
        verifylist = [
            ('name', 'new_name'),
            ('description', 'new_description'),
            ('properties', None),
            ('volume_type', self.volume_type.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        kwargs = {
            'name': 'new_name',
            'description': 'new_description',
            'is_public': False,
        }
        self.volume_client.update_type.assert_called_with(
            self.volume_type.id, **kwargs
        )
        self.assertIsNone(result)

        self.volume_client.add_type_access.assert_not_called()
        self.volume_client.update_type_encryption.assert_not_called()
        self.volume_client.create_type_encryption.assert_not_called()

    def test_type_set_property(self):
        arglist = [
            '--property',
            'myprop=myvalue',
            # this combination isn't viable server-side but is okay for testing
            '--multiattach',
            '--cacheable',
            '--replicated',
            '--availability-zone',
            'az1',
            self.volume_type.id,
        ]
        verifylist = [
            ('name', None),
            ('description', None),
            ('properties', {'myprop': 'myvalue'}),
            ('multiattach', True),
            ('cacheable', True),
            ('replicated', True),
            ('availability_zones', ['az1']),
            ('volume_type', self.volume_type.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        self.volume_client.update_type_extra_specs.assert_called_once_with(
            self.volume_type.id,
            myprop='myvalue',
            multiattach='<is> True',
            cacheable='<is> True',
            replication_enabled='<is> True',
            **{'RESKEY:availability_zones': 'az1'},
        )
        self.volume_client.add_type_access.assert_not_called()
        self.volume_client.update_type_encryption.assert_not_called()
        self.volume_client.create_type_encryption.assert_not_called()

    def test_type_set_with_empty_project(self):
        arglist = [
            '--project',
            '',
            self.volume_type.id,
        ]
        verifylist = [
            ('project', ''),
            ('volume_type', self.volume_type.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        self.volume_client.update_type_extra_specs.assert_not_called()
        self.volume_client.add_type_access.assert_not_called()
        self.volume_client.update_type_encryption.assert_not_called()
        self.volume_client.create_type_encryption.assert_not_called()

    def test_type_set_with_project(self):
        arglist = [
            '--project',
            self.project.id,
            self.volume_type.id,
        ]
        verifylist = [
            ('project', self.project.id),
            ('volume_type', self.volume_type.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        self.volume_client.update_type_extra_specs.assert_not_called()
        self.volume_client.add_type_access.assert_called_with(
            self.volume_type.id,
            self.project.id,
        )
        self.volume_client.update_type_encryption.assert_not_called()
        self.volume_client.create_type_encryption.assert_not_called()

    def test_type_set_with_new_encryption(self):
        self.volume_client.update_type_encryption.side_effect = (
            sdk_exceptions.NotFoundException('NotFound')
        )
        arglist = [
            '--encryption-provider',
            'LuksEncryptor',
            '--encryption-cipher',
            'aes-xts-plain64',
            '--encryption-key-size',
            '128',
            '--encryption-control-location',
            'front-end',
            self.volume_type.id,
        ]
        verifylist = [
            ('encryption_provider', 'LuksEncryptor'),
            ('encryption_cipher', 'aes-xts-plain64'),
            ('encryption_key_size', 128),
            ('encryption_control_location', 'front-end'),
            ('volume_type', self.volume_type.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        self.volume_client.update_type_encryption.assert_called_with(
            encryption=None,
            volume_type=self.volume_type,
            provider='LuksEncryptor',
            cipher='aes-xts-plain64',
            key_size=128,
            control_location='front-end',
        )
        self.volume_client.create_type_encryption.assert_called_with(
            self.volume_type,
            provider='LuksEncryptor',
            cipher='aes-xts-plain64',
            key_size=128,
            control_location='front-end',
        )

    def test_type_set_with_existing_encryption(self):
        arglist = [
            '--encryption-provider',
            'LuksEncryptor',
            '--encryption-cipher',
            'aes-xts-plain64',
            '--encryption-control-location',
            'front-end',
            self.volume_type.id,
        ]
        verifylist = [
            ('encryption_provider', 'LuksEncryptor'),
            ('encryption_cipher', 'aes-xts-plain64'),
            ('encryption_control_location', 'front-end'),
            ('volume_type', self.volume_type.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        self.volume_client.update_type_extra_specs.assert_not_called()
        self.volume_client.add_type_access.assert_not_called()
        self.volume_client.update_type_encryption.assert_called_with(
            encryption=None,
            volume_type=self.volume_type,
            provider='LuksEncryptor',
            cipher='aes-xts-plain64',
            control_location='front-end',
        )
        self.volume_client.create_type_encryption.assert_not_called()

    def test_type_set_new_encryption_without_provider(self):
        self.volume_client.update_type_encryption.side_effect = (
            sdk_exceptions.NotFoundException('NotFound')
        )
        arglist = [
            '--encryption-cipher',
            'aes-xts-plain64',
            '--encryption-key-size',
            '128',
            '--encryption-control-location',
            'front-end',
            self.volume_type.id,
        ]
        verifylist = [
            ('encryption_cipher', 'aes-xts-plain64'),
            ('encryption_key_size', 128),
            ('encryption_control_location', 'front-end'),
            ('volume_type', self.volume_type.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError,
            self.cmd.take_action,
            parsed_args,
        )
        self.assertEqual(
            "Command Failed: One or more of the operations failed",
            str(exc),
        )

        self.volume_client.update_type_extra_specs.assert_not_called()
        self.volume_client.add_type_access.assert_not_called()
        self.volume_client.update_type_encryption.assert_called_with(
            encryption=None,
            volume_type=self.volume_type,
            cipher='aes-xts-plain64',
            key_size=128,
            control_location='front-end',
        )
        self.volume_client.create_type_encryption.assert_not_called()


class TestTypeShow(volume_fakes.TestVolume):
    columns = (
        'access_project_ids',
        'description',
        'id',
        'is_public',
        'name',
        'properties',
    )

    def setUp(self):
        super().setUp()

        self.volume_type = sdk_fakes.generate_fake_resource(_type.Type)
        self.data = (
            None,
            self.volume_type.description,
            self.volume_type.id,
            self.volume_type.is_public,
            self.volume_type.name,
            format_columns.DictColumn(self.volume_type.extra_specs),
        )

        self.volume_client.find_type.return_value = self.volume_type

        self.cmd = volume_type.ShowVolumeType(self.app, None)

    def test_type_show(self):
        arglist = [self.volume_type.id]
        verifylist = [
            ("encryption_type", False),
            ("volume_type", self.volume_type.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.volume_client.find_type.assert_called_with(
            self.volume_type.id, ignore_missing=False
        )

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_type_show_with_access(self):
        arglist = [self.volume_type.id]
        verifylist = [("volume_type", self.volume_type.id)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        private_type = sdk_fakes.generate_fake_resource(
            _type.Type, is_public=False
        )
        type_access_list = {
            'volume_type_id': private_type.id,
            'project_id': 'project-id-test',
        }
        self.volume_client.find_type.return_value = private_type
        self.volume_client.get_type_access.return_value = [type_access_list]

        columns, data = self.cmd.take_action(parsed_args)
        self.volume_client.find_type.assert_called_once_with(
            self.volume_type.id, ignore_missing=False
        )
        self.volume_client.get_type_access.assert_called_once_with(
            private_type.id
        )

        self.assertEqual(self.columns, columns)
        private_type_data = (
            format_columns.ListColumn([type_access_list['project_id']]),
            private_type.description,
            private_type.id,
            private_type.is_public,
            private_type.name,
            format_columns.DictColumn(private_type.extra_specs),
        )
        self.assertCountEqual(private_type_data, data)

    def test_type_show_with_list_access_exec(self):
        arglist = [self.volume_type.id]
        verifylist = [("volume_type", self.volume_type.id)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        private_type = sdk_fakes.generate_fake_resource(
            _type.Type, is_public=False
        )
        self.volume_client.find_type.return_value = private_type
        self.volume_client.get_type_access.side_effect = Exception()

        columns, data = self.cmd.take_action(parsed_args)
        self.volume_client.find_type.assert_called_once_with(
            self.volume_type.id, ignore_missing=False
        )
        self.volume_client.get_type_access.assert_called_once_with(
            private_type.id
        )

        self.assertEqual(self.columns, columns)
        private_type_data = (
            None,
            private_type.description,
            private_type.id,
            private_type.is_public,
            private_type.name,
            format_columns.DictColumn(private_type.extra_specs),
        )
        self.assertCountEqual(private_type_data, data)

    def test_type_show_with_encryption(self):
        encryption_type = sdk_fakes.generate_fake_resource(
            _type.TypeEncryption,
        )
        self.volume_type = sdk_fakes.generate_fake_resource(_type.Type)
        self.volume_client.find_type.return_value = self.volume_type
        self.volume_client.get_type_encryption.return_value = encryption_type
        expected_encryption_info = {
            'cipher': encryption_type.cipher,
            'control_location': encryption_type.control_location,
            'encryption_id': encryption_type.encryption_id,
            'key_size': encryption_type.key_size,
            'provider': encryption_type.provider,
        }
        encryption_columns = (
            'access_project_ids',
            'description',
            'encryption',
            'id',
            'is_public',
            'name',
            'properties',
        )
        encryption_data = (
            None,
            self.volume_type.description,
            format_columns.DictColumn(expected_encryption_info),
            self.volume_type.id,
            self.volume_type.is_public,
            self.volume_type.name,
            format_columns.DictColumn(self.volume_type.extra_specs),
        )
        arglist = ['--encryption-type', self.volume_type.id]
        verifylist = [
            ('encryption_type', True),
            ("volume_type", self.volume_type.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.volume_client.find_type.assert_called_with(
            self.volume_type.id, ignore_missing=False
        )
        self.volume_client.get_type_encryption.assert_called_with(
            self.volume_type.id
        )
        self.assertEqual(encryption_columns, columns)
        self.assertCountEqual(encryption_data, data)


class TestTypeUnset(volume_fakes.TestVolume):
    volume_type = sdk_fakes.generate_fake_resource(_type.Type)

    def setUp(self):
        super().setUp()

        self.volume_client.find_type.return_value = self.volume_type

        self.project = sdk_fakes.generate_fake_resource(_project.Project)
        self.identity_sdk_client.find_project.return_value = self.project

        self.cmd = volume_type.UnsetVolumeType(self.app, None)

    def test_type_unset(self):
        arglist = [
            '--property',
            'property',
            '--property',
            'multi_property',
            self.volume_type.id,
        ]
        verifylist = [
            ('properties', ['property', 'multi_property']),
            ('volume_type', self.volume_type.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.volume_client.delete_type_extra_specs.assert_called_once_with(
            self.volume_type.id, ['property', 'multi_property']
        )
        self.assertIsNone(result)

    def test_type_unset_project_access(self):
        arglist = [
            '--project',
            self.project.id,
            self.volume_type.id,
        ]
        verifylist = [
            ('project', self.project.id),
            ('volume_type', self.volume_type.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        self.volume_client.remove_type_access.assert_called_with(
            self.volume_type.id,
            self.project.id,
        )

    def test_type_unset_not_called_without_project_argument(self):
        arglist = [
            '--project',
            '',
            self.volume_type.id,
        ]
        verifylist = [
            ('encryption_type', False),
            ('project', ''),
            ('volume_type', self.volume_type.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)
        self.volume_client.delete_type_encryption.assert_not_called()
        self.volume_client.remove_type_access.assert_not_called()

    def test_type_unset_failed_with_missing_volume_type_argument(self):
        arglist = [
            '--project',
            'foo',
        ]
        verifylist = [
            ('project', 'foo'),
        ]

        self.assertRaises(
            tests_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_type_unset_encryption_type(self):
        arglist = [
            '--encryption-type',
            self.volume_type.id,
        ]
        verifylist = [
            ('encryption_type', True),
            ('volume_type', self.volume_type.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.volume_client.delete_type_encryption.assert_called_with(
            None, self.volume_type.id
        )
        self.assertIsNone(result)


class TestColumns(volume_fakes.TestVolume):
    def test_encryption_info_column_with_info(self):
        fake_volume_type = sdk_fakes.generate_fake_resource(_type.Type)
        type_id = fake_volume_type.id

        encryption_info = {
            'provider': 'LuksEncryptor',
            'cipher': None,
            'key_size': None,
            'control_location': 'front-end',
        }
        col = volume_type.EncryptionInfoColumn(
            type_id, {type_id: encryption_info}
        )
        self.assertEqual(
            utils.format_dict(encryption_info), col.human_readable()
        )
        self.assertEqual(encryption_info, col.machine_readable())

    def test_encryption_info_column_without_info(self):
        fake_volume_type = sdk_fakes.generate_fake_resource(_type.Type)
        type_id = fake_volume_type.id

        col = volume_type.EncryptionInfoColumn(type_id, {})
        self.assertEqual('-', col.human_readable())
        self.assertIsNone(col.machine_readable())
