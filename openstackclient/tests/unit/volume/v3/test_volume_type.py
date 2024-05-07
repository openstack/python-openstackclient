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

from unittest import mock
from unittest.mock import call

from osc_lib.cli import format_columns
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes
from openstackclient.tests.unit import utils as tests_utils
from openstackclient.tests.unit.volume.v3 import fakes as volume_fakes
from openstackclient.volume.v3 import volume_type


class TestType(volume_fakes.TestVolume):
    def setUp(self):
        super().setUp()

        self.volume_types_mock = self.volume_client.volume_types
        self.volume_types_mock.reset_mock()

        self.volume_type_access_mock = self.volume_client.volume_type_access
        self.volume_type_access_mock.reset_mock()

        self.volume_encryption_types_mock = (
            self.volume_client.volume_encryption_types
        )
        self.volume_encryption_types_mock.reset_mock()

        self.projects_mock = self.identity_client.projects
        self.projects_mock.reset_mock()


class TestTypeCreate(TestType):
    def setUp(self):
        super().setUp()

        self.new_volume_type = volume_fakes.create_one_volume_type(
            methods={'set_keys': None},
        )
        self.project = identity_fakes.FakeProject.create_one_project()
        self.columns = (
            'description',
            'id',
            'is_public',
            'name',
        )
        self.data = (
            self.new_volume_type.description,
            self.new_volume_type.id,
            True,
            self.new_volume_type.name,
        )

        self.volume_types_mock.create.return_value = self.new_volume_type
        self.projects_mock.get.return_value = self.project
        # Get the command object to test
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
        self.volume_types_mock.create.assert_called_with(
            self.new_volume_type.name,
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
        self.volume_types_mock.create.assert_called_with(
            self.new_volume_type.name,
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

        columns, data = self.cmd.take_action(parsed_args)
        self.volume_types_mock.create.assert_called_with(
            self.new_volume_type.name, description=None
        )
        self.new_volume_type.set_keys.assert_called_once_with(
            {
                'myprop': 'myvalue',
                'multiattach': '<is> True',
                'cacheable': '<is> True',
                'replication_enabled': '<is> True',
                'RESKEY:availability_zones': 'az1',
            }
        )

        self.columns += ('properties',)
        self.data += (format_columns.DictColumn(None),)

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

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
        encryption_info = {
            'provider': 'LuksEncryptor',
            'cipher': 'aes-xts-plain64',
            'key_size': '128',
            'control_location': 'front-end',
        }
        encryption_type = volume_fakes.create_one_encryption_volume_type(
            attrs=encryption_info,
        )
        self.new_volume_type = volume_fakes.create_one_volume_type(
            attrs={'encryption': encryption_info},
        )
        self.volume_types_mock.create.return_value = self.new_volume_type
        self.volume_encryption_types_mock.create.return_value = encryption_type
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
        self.volume_types_mock.create.assert_called_with(
            self.new_volume_type.name,
            description=None,
        )
        body = {
            'provider': 'LuksEncryptor',
            'cipher': 'aes-xts-plain64',
            'key_size': 128,
            'control_location': 'front-end',
        }
        self.volume_encryption_types_mock.create.assert_called_with(
            self.new_volume_type,
            body,
        )
        self.assertEqual(encryption_columns, columns)
        self.assertCountEqual(encryption_data, data)


class TestTypeDelete(TestType):
    volume_types = volume_fakes.create_volume_types(count=2)

    def setUp(self):
        super().setUp()

        self.volume_types_mock.get = volume_fakes.get_volume_types(
            self.volume_types,
        )
        self.volume_types_mock.delete.return_value = None

        # Get the command object to mock
        self.cmd = volume_type.DeleteVolumeType(self.app, None)

    def test_type_delete(self):
        arglist = [self.volume_types[0].id]
        verifylist = [("volume_types", [self.volume_types[0].id])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.volume_types_mock.delete.assert_called_with(self.volume_types[0])
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
        self.volume_types_mock.delete.assert_has_calls(calls)
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
        with mock.patch.object(
            utils, 'find_resource', side_effect=find_mock_result
        ) as find_mock:
            try:
                self.cmd.take_action(parsed_args)
                self.fail('CommandError should be raised.')
            except exceptions.CommandError as e:
                self.assertEqual(
                    '1 of 2 volume types failed to delete.', str(e)
                )
            find_mock.assert_any_call(
                self.volume_types_mock, self.volume_types[0].id
            )
            find_mock.assert_any_call(self.volume_types_mock, 'unexist_type')

            self.assertEqual(2, find_mock.call_count)
            self.volume_types_mock.delete.assert_called_once_with(
                self.volume_types[0]
            )


class TestTypeList(TestType):
    volume_types = volume_fakes.create_volume_types()

    columns = [
        "ID",
        "Name",
        "Is Public",
    ]
    columns_long = columns + ["Description", "Properties"]
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

        self.volume_types_mock.list.return_value = self.volume_types
        self.volume_types_mock.default.return_value = self.volume_types[0]
        # get the command to test
        self.cmd = volume_type.ListVolumeType(self.app, None)

    def test_type_list_without_options(self):
        arglist = []
        verifylist = [
            ("long", False),
            ("is_public", None),
            ("default", False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.volume_types_mock.list.assert_called_once_with(
            search_opts={}, is_public=None
        )
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
        self.volume_types_mock.list.assert_called_once_with(
            search_opts={}, is_public=True
        )
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
        self.volume_types_mock.list.assert_called_once_with(
            search_opts={}, is_public=False
        )
        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, list(data))

    def test_type_list_with_default_option(self):
        arglist = [
            "--default",
        ]
        verifylist = [
            ("encryption_type", False),
            ("long", False),
            ("is_public", None),
            ("default", True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.volume_types_mock.default.assert_called_once_with()
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
            ("is_public", None),
            ("default", False),
            ("properties", {"foo": "bar"}),
            ("multiattach", True),
            ("cacheable", True),
            ("replicated", True),
            ("availability_zones", ["az1"]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.volume_types_mock.list.assert_called_once_with(
            search_opts={
                "extra_specs": {
                    "foo": "bar",
                    "multiattach": "<is> True",
                    "cacheable": "<is> True",
                    "replication_enabled": "<is> True",
                    "RESKEY:availability_zones": "az1",
                }
            },
            is_public=None,
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
            ("is_public", None),
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
        encryption_type = volume_fakes.create_one_encryption_volume_type(
            attrs={'volume_type_id': self.volume_types[0].id},
        )
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
        encryption_data.append(
            (
                self.volume_types[0].id,
                self.volume_types[0].name,
                self.volume_types[0].is_public,
                volume_type.EncryptionInfoColumn(
                    self.volume_types[0].id,
                    {self.volume_types[0].id: encryption_info},
                ),
            )
        )
        encryption_data.append(
            (
                self.volume_types[1].id,
                self.volume_types[1].name,
                self.volume_types[1].is_public,
                volume_type.EncryptionInfoColumn(self.volume_types[1].id, {}),
            )
        )

        self.volume_encryption_types_mock.list.return_value = [encryption_type]
        arglist = [
            "--encryption-type",
        ]
        verifylist = [
            ("encryption_type", True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.volume_encryption_types_mock.list.assert_called_once_with()
        self.volume_types_mock.list.assert_called_once_with(
            search_opts={}, is_public=None
        )
        self.assertEqual(encryption_columns, columns)
        self.assertCountEqual(encryption_data, list(data))


class TestTypeSet(TestType):
    def setUp(self):
        super().setUp()

        self.project = identity_fakes.FakeProject.create_one_project()
        self.projects_mock.get.return_value = self.project

        self.volume_type = volume_fakes.create_one_volume_type(
            methods={'set_keys': None},
        )
        self.volume_types_mock.get.return_value = self.volume_type
        self.volume_encryption_types_mock.create.return_value = None
        self.volume_encryption_types_mock.update.return_value = None

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
        self.volume_types_mock.update.assert_called_with(
            self.volume_type.id, **kwargs
        )
        self.assertIsNone(result)

        self.volume_type_access_mock.add_project_access.assert_not_called()
        self.volume_encryption_types_mock.update.assert_not_called()
        self.volume_encryption_types_mock.create.assert_not_called()

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

        self.volume_type.set_keys.assert_called_once_with(
            {
                'myprop': 'myvalue',
                'multiattach': '<is> True',
                'cacheable': '<is> True',
                'replication_enabled': '<is> True',
                'RESKEY:availability_zones': 'az1',
            }
        )
        self.volume_type_access_mock.add_project_access.assert_not_called()
        self.volume_encryption_types_mock.update.assert_not_called()
        self.volume_encryption_types_mock.create.assert_not_called()

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

        self.volume_type.set_keys.assert_not_called()
        self.volume_type_access_mock.add_project_access.assert_not_called()
        self.volume_encryption_types_mock.update.assert_not_called()
        self.volume_encryption_types_mock.create.assert_not_called()

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

        self.volume_type.set_keys.assert_not_called()
        self.volume_type_access_mock.add_project_access.assert_called_with(
            self.volume_type.id,
            self.project.id,
        )
        self.volume_encryption_types_mock.update.assert_not_called()
        self.volume_encryption_types_mock.create.assert_not_called()

    def test_type_set_with_new_encryption(self):
        self.volume_encryption_types_mock.update.side_effect = (
            exceptions.NotFound('NotFound')
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

        body = {
            'provider': 'LuksEncryptor',
            'cipher': 'aes-xts-plain64',
            'key_size': 128,
            'control_location': 'front-end',
        }
        self.volume_encryption_types_mock.update.assert_called_with(
            self.volume_type,
            body,
        )
        self.volume_encryption_types_mock.create.assert_called_with(
            self.volume_type,
            body,
        )

    @mock.patch.object(utils, 'find_resource')
    def test_type_set_with_existing_encryption(self, mock_find):
        mock_find.side_effect = [self.volume_type, "existing_encryption_type"]
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

        self.volume_type.set_keys.assert_not_called()
        self.volume_type_access_mock.add_project_access.assert_not_called()
        body = {
            'provider': 'LuksEncryptor',
            'cipher': 'aes-xts-plain64',
            'control_location': 'front-end',
        }
        self.volume_encryption_types_mock.update.assert_called_with(
            self.volume_type,
            body,
        )
        self.volume_encryption_types_mock.create.assert_not_called()

    def test_type_set_new_encryption_without_provider(self):
        self.volume_encryption_types_mock.update.side_effect = (
            exceptions.NotFound('NotFound')
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

        self.volume_type.set_keys.assert_not_called()
        self.volume_type_access_mock.add_project_access.assert_not_called()
        body = {
            'cipher': 'aes-xts-plain64',
            'key_size': 128,
            'control_location': 'front-end',
        }
        self.volume_encryption_types_mock.update.assert_called_with(
            self.volume_type,
            body,
        )
        self.volume_encryption_types_mock.create.assert_not_called()


class TestTypeShow(TestType):
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

        self.volume_type = volume_fakes.create_one_volume_type()
        self.data = (
            None,
            self.volume_type.description,
            self.volume_type.id,
            True,
            self.volume_type.name,
            format_columns.DictColumn(self.volume_type.extra_specs),
        )

        self.volume_types_mock.get.return_value = self.volume_type

        # Get the command object to test
        self.cmd = volume_type.ShowVolumeType(self.app, None)

    def test_type_show(self):
        arglist = [self.volume_type.id]
        verifylist = [
            ("encryption_type", False),
            ("volume_type", self.volume_type.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.volume_types_mock.get.assert_called_with(self.volume_type.id)

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_type_show_with_access(self):
        arglist = [self.volume_type.id]
        verifylist = [("volume_type", self.volume_type.id)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        private_type = volume_fakes.create_one_volume_type(
            attrs={'is_public': False},
        )
        type_access_list = volume_fakes.create_one_type_access()
        with mock.patch.object(
            self.volume_types_mock,
            'get',
            return_value=private_type,
        ):
            with mock.patch.object(
                self.volume_type_access_mock,
                'list',
                return_value=[type_access_list],
            ):
                columns, data = self.cmd.take_action(parsed_args)
                self.volume_types_mock.get.assert_called_once_with(
                    self.volume_type.id
                )
                self.volume_type_access_mock.list.assert_called_once_with(
                    private_type.id
                )

        self.assertEqual(self.columns, columns)
        private_type_data = (
            format_columns.ListColumn([type_access_list.project_id]),
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

        private_type = volume_fakes.create_one_volume_type(
            attrs={'is_public': False},
        )
        with mock.patch.object(
            self.volume_types_mock, 'get', return_value=private_type
        ):
            with mock.patch.object(
                self.volume_type_access_mock, 'list', side_effect=Exception()
            ):
                columns, data = self.cmd.take_action(parsed_args)
                self.volume_types_mock.get.assert_called_once_with(
                    self.volume_type.id
                )
                self.volume_type_access_mock.list.assert_called_once_with(
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
        encryption_type = volume_fakes.create_one_encryption_volume_type()
        encryption_info = {
            'provider': 'LuksEncryptor',
            'cipher': None,
            'key_size': None,
            'control_location': 'front-end',
        }
        self.volume_type = volume_fakes.create_one_volume_type(
            attrs={'encryption': encryption_info},
        )
        self.volume_types_mock.get.return_value = self.volume_type
        self.volume_encryption_types_mock.get.return_value = encryption_type
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
            format_columns.DictColumn(encryption_info),
            self.volume_type.id,
            True,
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
        self.volume_types_mock.get.assert_called_with(self.volume_type.id)
        self.volume_encryption_types_mock.get.assert_called_with(
            self.volume_type.id
        )
        self.assertEqual(encryption_columns, columns)
        self.assertCountEqual(encryption_data, data)


class TestTypeUnset(TestType):
    project = identity_fakes.FakeProject.create_one_project()
    volume_type = volume_fakes.create_one_volume_type(
        methods={'unset_keys': None},
    )

    def setUp(self):
        super().setUp()

        self.volume_types_mock.get.return_value = self.volume_type

        # Return a project
        self.projects_mock.get.return_value = self.project

        # Get the command object to test
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
        self.volume_type.unset_keys.assert_called_once_with(
            ['property', 'multi_property']
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

        self.volume_type_access_mock.remove_project_access.assert_called_with(
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
        self.volume_encryption_types_mock.delete.assert_not_called()
        self.assertFalse(
            self.volume_type_access_mock.remove_project_access.called
        )

    def test_type_unset_failed_with_missing_volume_type_argument(self):
        arglist = [
            '--project',
            'identity_fakes.project_id',
        ]
        verifylist = [
            ('project', 'identity_fakes.project_id'),
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
        self.volume_encryption_types_mock.delete.assert_called_with(
            self.volume_type
        )
        self.assertIsNone(result)


class TestColumns(TestType):
    def test_encryption_info_column_with_info(self):
        fake_volume_type = volume_fakes.create_one_volume_type()
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
        fake_volume_type = volume_fakes.create_one_volume_type()
        type_id = fake_volume_type.id

        col = volume_type.EncryptionInfoColumn(type_id, {})
        self.assertEqual('-', col.human_readable())
        self.assertIsNone(col.machine_readable())
