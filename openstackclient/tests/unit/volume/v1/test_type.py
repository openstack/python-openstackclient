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

from osc_lib.cli import format_columns
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.tests.unit import utils as tests_utils
from openstackclient.tests.unit.volume.v1 import fakes as volume_fakes
from openstackclient.volume.v1 import volume_type


class TestType(volume_fakes.TestVolumev1):

    def setUp(self):
        super(TestType, self).setUp()

        self.types_mock = self.app.client_manager.volume.volume_types
        self.types_mock.reset_mock()

        self.encryption_types_mock = (
            self.app.client_manager.volume.volume_encryption_types)
        self.encryption_types_mock.reset_mock()


class TestTypeCreate(TestType):

    columns = (
        'description',
        'id',
        'is_public',
        'name',
    )

    def setUp(self):
        super(TestTypeCreate, self).setUp()

        self.new_volume_type = volume_fakes.FakeType.create_one_type(
            methods={'set_keys': {'myprop': 'myvalue'}}
        )
        self.data = (
            self.new_volume_type.description,
            self.new_volume_type.id,
            True,
            self.new_volume_type.name,
        )

        self.types_mock.create.return_value = self.new_volume_type
        # Get the command object to test
        self.cmd = volume_type.CreateVolumeType(self.app, None)

    def test_type_create(self):
        arglist = [
            self.new_volume_type.name,
        ]
        verifylist = [
            ("name", self.new_volume_type.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.types_mock.create.assert_called_with(
            self.new_volume_type.name,
        )

        self.assertEqual(self.columns, columns)
        self.assertItemEqual(self.data, data)

    def test_type_create_with_encryption(self):
        encryption_info = {
            'provider': 'LuksEncryptor',
            'cipher': 'aes-xts-plain64',
            'key_size': '128',
            'control_location': 'front-end',
        }
        encryption_type = volume_fakes.FakeType.create_one_encryption_type(
            attrs=encryption_info
        )
        self.new_volume_type = volume_fakes.FakeType.create_one_type(
            attrs={'encryption': encryption_info})
        self.types_mock.create.return_value = self.new_volume_type
        self.encryption_types_mock.create.return_value = encryption_type
        encryption_columns = (
            'description',
            'encryption',
            'id',
            'is_public',
            'name',
        )
        encryption_data = (
            self.new_volume_type.description,
            format_columns.DictColumn(encryption_info),
            self.new_volume_type.id,
            True,
            self.new_volume_type.name,
        )
        arglist = [
            '--encryption-provider', 'LuksEncryptor',
            '--encryption-cipher', 'aes-xts-plain64',
            '--encryption-key-size', '128',
            '--encryption-control-location', 'front-end',
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
        self.types_mock.create.assert_called_with(
            self.new_volume_type.name,
        )
        body = {
            'provider': 'LuksEncryptor',
            'cipher': 'aes-xts-plain64',
            'key_size': 128,
            'control_location': 'front-end',
        }
        self.encryption_types_mock.create.assert_called_with(
            self.new_volume_type,
            body,
        )
        self.assertEqual(encryption_columns, columns)
        self.assertItemEqual(encryption_data, data)


class TestTypeDelete(TestType):

    volume_types = volume_fakes.FakeType.create_types(count=2)

    def setUp(self):
        super(TestTypeDelete, self).setUp()

        self.types_mock.get = volume_fakes.FakeType.get_types(
            self.volume_types)
        self.types_mock.delete.return_value = None

        # Get the command object to mock
        self.cmd = volume_type.DeleteVolumeType(self.app, None)

    def test_type_delete(self):
        arglist = [
            self.volume_types[0].id
        ]
        verifylist = [
            ("volume_types", [self.volume_types[0].id])
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.types_mock.delete.assert_called_with(self.volume_types[0])
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
        self.types_mock.delete.assert_has_calls(calls)
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

        find_mock_result = [self.volume_types[0], exceptions.CommandError]
        with mock.patch.object(utils, 'find_resource',
                               side_effect=find_mock_result) as find_mock:
            try:
                self.cmd.take_action(parsed_args)
                self.fail('CommandError should be raised.')
            except exceptions.CommandError as e:
                self.assertEqual('1 of 2 volume types failed to delete.',
                                 str(e))

            find_mock.assert_any_call(
                self.types_mock, self.volume_types[0].id)
            find_mock.assert_any_call(self.types_mock, 'unexist_type')

            self.assertEqual(2, find_mock.call_count)
            self.types_mock.delete.assert_called_once_with(
                self.volume_types[0]
            )


class TestTypeList(TestType):

    volume_types = volume_fakes.FakeType.create_types()

    columns = [
        "ID",
        "Name",
        "Is Public",
    ]
    columns_long = [
        "ID",
        "Name",
        "Is Public",
        "Properties"
    ]

    data = []
    for t in volume_types:
        data.append((
            t.id,
            t.name,
            t.is_public,
        ))
    data_long = []
    for t in volume_types:
        data_long.append((
            t.id,
            t.name,
            t.is_public,
            format_columns.DictColumn(t.extra_specs),
        ))

    def setUp(self):
        super(TestTypeList, self).setUp()

        self.types_mock.list.return_value = self.volume_types
        self.encryption_types_mock.create.return_value = None
        self.encryption_types_mock.update.return_value = None
        # get the command to test
        self.cmd = volume_type.ListVolumeType(self.app, None)

    def test_type_list_without_options(self):
        arglist = []
        verifylist = [
            ("long", False),
            ("encryption_type", False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.types_mock.list.assert_called_once_with()
        self.assertEqual(self.columns, columns)
        self.assertListItemEqual(self.data, list(data))

    def test_type_list_with_options(self):
        arglist = [
            "--long",
        ]
        verifylist = [
            ("long", True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.types_mock.list.assert_called_once_with()
        self.assertEqual(self.columns_long, columns)
        self.assertListItemEqual(self.data_long, list(data))

    def test_type_list_with_encryption(self):
        encryption_type = volume_fakes.FakeType.create_one_encryption_type(
            attrs={'volume_type_id': self.volume_types[0].id})
        encryption_info = {
            'provider': 'LuksEncryptor',
            'cipher': None,
            'key_size': None,
            'control_location': 'front-end',
        }
        encryption_columns = self.columns + [
            "Encryption",
        ]
        encryption_data = []
        encryption_data.append((
            self.volume_types[0].id,
            self.volume_types[0].name,
            self.volume_types[0].is_public,
            volume_type.EncryptionInfoColumn(
                self.volume_types[0].id,
                {self.volume_types[0].id: encryption_info}),
        ))
        encryption_data.append((
            self.volume_types[1].id,
            self.volume_types[1].name,
            self.volume_types[1].is_public,
            volume_type.EncryptionInfoColumn(
                self.volume_types[1].id, {}),
        ))

        self.encryption_types_mock.list.return_value = [encryption_type]
        arglist = [
            "--encryption-type",
        ]
        verifylist = [
            ("encryption_type", True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.encryption_types_mock.list.assert_called_once_with()
        self.types_mock.list.assert_called_once_with()
        self.assertEqual(encryption_columns, columns)
        self.assertListItemEqual(encryption_data, list(data))


class TestTypeSet(TestType):

    volume_type = volume_fakes.FakeType.create_one_type(
        methods={'set_keys': None})

    def setUp(self):
        super(TestTypeSet, self).setUp()

        self.types_mock.get.return_value = self.volume_type

        # Get the command object to test
        self.cmd = volume_type.SetVolumeType(self.app, None)

    def test_type_set_nothing(self):
        arglist = [
            self.volume_type.id,
        ]
        verifylist = [
            ('volume_type', self.volume_type.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)

    def test_type_set_property(self):
        arglist = [
            '--property', 'myprop=myvalue',
            self.volume_type.id,
        ]
        verifylist = [
            ('property', {'myprop': 'myvalue'}),
            ('volume_type', self.volume_type.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.volume_type.set_keys.assert_called_once_with(
            {'myprop': 'myvalue'})
        self.assertIsNone(result)

    def test_type_set_new_encryption(self):
        arglist = [
            '--encryption-provider', 'LuksEncryptor',
            '--encryption-cipher', 'aes-xts-plain64',
            '--encryption-key-size', '128',
            '--encryption-control-location', 'front-end',
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
        body = {
            'provider': 'LuksEncryptor',
            'cipher': 'aes-xts-plain64',
            'key_size': 128,
            'control_location': 'front-end',
        }
        self.encryption_types_mock.create.assert_called_with(
            self.volume_type,
            body,
        )
        self.assertIsNone(result)

    def test_type_set_new_encryption_without_provider(self):
        arglist = [
            '--encryption-cipher', 'aes-xts-plain64',
            '--encryption-key-size', '128',
            '--encryption-control-location', 'front-end',
            self.volume_type.id,
        ]
        verifylist = [
            ('encryption_cipher', 'aes-xts-plain64'),
            ('encryption_key_size', 128),
            ('encryption_control_location', 'front-end'),
            ('volume_type', self.volume_type.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual("Command Failed: One or more of"
                             " the operations failed",
                             str(e))
        self.encryption_types_mock.create.assert_not_called()
        self.encryption_types_mock.update.assert_not_called()


class TestTypeShow(TestType):

    columns = (
        'description',
        'id',
        'is_public',
        'name',
        'properties',
    )

    def setUp(self):
        super(TestTypeShow, self).setUp()

        self.volume_type = volume_fakes.FakeType.create_one_type()
        self.data = (
            self.volume_type.description,
            self.volume_type.id,
            True,
            self.volume_type.name,
            format_columns.DictColumn(self.volume_type.extra_specs)
        )

        self.types_mock.get.return_value = self.volume_type

        # Get the command object to test
        self.cmd = volume_type.ShowVolumeType(self.app, None)

    def test_type_show(self):
        arglist = [
            self.volume_type.id
        ]
        verifylist = [
            ("volume_type", self.volume_type.id),
            ("encryption_type", False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.types_mock.get.assert_called_with(self.volume_type.id)

        self.assertEqual(self.columns, columns)
        self.assertItemEqual(self.data, data)

    def test_type_show_with_encryption(self):
        encryption_type = volume_fakes.FakeType.create_one_encryption_type()
        encryption_info = {
            'provider': 'LuksEncryptor',
            'cipher': None,
            'key_size': None,
            'control_location': 'front-end',
        }
        self.volume_type = volume_fakes.FakeType.create_one_type(
            attrs={'encryption': encryption_info})
        self.types_mock.get.return_value = self.volume_type
        self.encryption_types_mock.get.return_value = encryption_type
        encryption_columns = (
            'description',
            'encryption',
            'id',
            'is_public',
            'name',
            'properties',
        )
        encryption_data = (
            self.volume_type.description,
            format_columns.DictColumn(encryption_info),
            self.volume_type.id,
            True,
            self.volume_type.name,
            format_columns.DictColumn(self.volume_type.extra_specs)
        )
        arglist = [
            '--encryption-type',
            self.volume_type.id
        ]
        verifylist = [
            ('encryption_type', True),
            ("volume_type", self.volume_type.id)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.types_mock.get.assert_called_with(self.volume_type.id)
        self.encryption_types_mock.get.assert_called_with(self.volume_type.id)
        self.assertEqual(encryption_columns, columns)
        self.assertItemEqual(encryption_data, data)


class TestTypeUnset(TestType):

    volume_type = volume_fakes.FakeType.create_one_type(
        methods={'unset_keys': None})

    def setUp(self):
        super(TestTypeUnset, self).setUp()

        self.types_mock.get.return_value = self.volume_type

        # Get the command object to test
        self.cmd = volume_type.UnsetVolumeType(self.app, None)

    def test_type_unset_property(self):
        arglist = [
            '--property', 'property',
            '--property', 'multi_property',
            self.volume_type.id,
        ]
        verifylist = [
            ('encryption_type', False),
            ('property', ['property', 'multi_property']),
            ('volume_type', self.volume_type.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.volume_type.unset_keys.assert_called_once_with(
            ['property', 'multi_property'])
        self.encryption_types_mock.delete.assert_not_called()
        self.assertIsNone(result)

    def test_type_unset_failed_with_missing_volume_type_argument(self):
        arglist = [
            '--property', 'property',
            '--property', 'multi_property',
        ]
        verifylist = [
            ('property', ['property', 'multi_property']),
        ]

        self.assertRaises(tests_utils.ParserException,
                          self.check_parser,
                          self.cmd,
                          arglist,
                          verifylist)

    def test_type_unset_nothing(self):
        arglist = [
            self.volume_type.id,
        ]
        verifylist = [
            ('volume_type', self.volume_type.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

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
        self.encryption_types_mock.delete.assert_called_with(self.volume_type)
        self.assertIsNone(result)


class TestColumns(TestType):

    def test_encryption_info_column_with_info(self):
        fake_volume_type = volume_fakes.FakeType.create_one_type()
        type_id = fake_volume_type.id

        encryption_info = {
            'provider': 'LuksEncryptor',
            'cipher': None,
            'key_size': None,
            'control_location': 'front-end',
        }
        col = volume_type.EncryptionInfoColumn(type_id,
                                               {type_id: encryption_info})
        self.assertEqual(utils.format_dict(encryption_info),
                         col.human_readable())
        self.assertEqual(encryption_info, col.machine_readable())

    def test_encryption_info_column_without_info(self):
        fake_volume_type = volume_fakes.FakeType.create_one_type()
        type_id = fake_volume_type.id

        col = volume_type.EncryptionInfoColumn(type_id, {})
        self.assertEqual('-', col.human_readable())
        self.assertIsNone(col.machine_readable())
