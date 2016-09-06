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

from osc_lib import exceptions
from osc_lib import utils

from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes
from openstackclient.tests.unit import utils as tests_utils
from openstackclient.tests.unit.volume.v2 import fakes as volume_fakes
from openstackclient.volume.v2 import volume_type


class TestType(volume_fakes.TestVolume):

    def setUp(self):
        super(TestType, self).setUp()

        self.types_mock = self.app.client_manager.volume.volume_types
        self.types_mock.reset_mock()

        self.types_access_mock = (
            self.app.client_manager.volume.volume_type_access)
        self.types_access_mock.reset_mock()

        self.projects_mock = self.app.client_manager.identity.projects
        self.projects_mock.reset_mock()


class TestTypeCreate(TestType):

    project = identity_fakes.FakeProject.create_one_project()
    columns = (
        'description',
        'id',
        'is_public',
        'name',
    )

    def setUp(self):
        super(TestTypeCreate, self).setUp()

        self.new_volume_type = volume_fakes.FakeType.create_one_type()
        self.data = (
            self.new_volume_type.description,
            self.new_volume_type.id,
            True,
            self.new_volume_type.name,
        )

        self.types_mock.create.return_value = self.new_volume_type
        self.projects_mock.get.return_value = self.project
        # Get the command object to test
        self.cmd = volume_type.CreateVolumeType(self.app, None)

    def test_type_create_public(self):
        arglist = [
            "--description", self.new_volume_type.description,
            "--public",
            self.new_volume_type.name,
        ]
        verifylist = [
            ("description", self.new_volume_type.description),
            ("public", True),
            ("private", False),
            ("name", self.new_volume_type.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.types_mock.create.assert_called_with(
            self.new_volume_type.name,
            description=self.new_volume_type.description,
            is_public=True,
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_type_create_private(self):
        arglist = [
            "--description", self.new_volume_type.description,
            "--private",
            "--project", self.project.id,
            self.new_volume_type.name,
        ]
        verifylist = [
            ("description", self.new_volume_type.description),
            ("public", False),
            ("private", True),
            ("project", self.project.id),
            ("name", self.new_volume_type.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.types_mock.create.assert_called_with(
            self.new_volume_type.name,
            description=self.new_volume_type.description,
            is_public=False,
        )

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_public_type_create_with_project(self):
        arglist = [
            '--project', self.project.id,
            self.new_volume_type.name,
        ]
        verifylist = [
            ('project', self.project.id),
            ('name', self.new_volume_type.name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(exceptions.CommandError,
                          self.cmd.take_action,
                          parsed_args)


class TestTypeDelete(TestType):

    volume_type = volume_fakes.FakeType.create_one_type()

    def setUp(self):
        super(TestTypeDelete, self).setUp()

        self.types_mock.get.return_value = self.volume_type
        self.types_mock.delete.return_value = None

        # Get the command object to mock
        self.cmd = volume_type.DeleteVolumeType(self.app, None)

    def test_type_delete(self):
        arglist = [
            self.volume_type.id
        ]
        verifylist = [
            ("volume_types", [self.volume_type.id])
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.types_mock.delete.assert_called_with(self.volume_type)
        self.assertIsNone(result)


class TestTypeList(TestType):

    volume_types = volume_fakes.FakeType.create_types()

    columns = [
        "ID",
        "Name"
    ]
    columns_long = columns + [
        "Description",
        "Properties"
    ]

    data = []
    for t in volume_types:
        data.append((
            t.id,
            t.name,
        ))
    data_long = []
    for t in volume_types:
        data_long.append((
            t.id,
            t.name,
            t.description,
            utils.format_dict(t.extra_specs),
        ))

    def setUp(self):
        super(TestTypeList, self).setUp()

        self.types_mock.list.return_value = self.volume_types
        # get the command to test
        self.cmd = volume_type.ListVolumeType(self.app, None)

    def test_type_list_without_options(self):
        arglist = []
        verifylist = [
            ("long", False),
            ("private", False),
            ("public", False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.types_mock.list.assert_called_once_with(is_public=None)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))

    def test_type_list_with_options(self):
        arglist = [
            "--long",
            "--public",
        ]
        verifylist = [
            ("long", True),
            ("private", False),
            ("public", True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.types_mock.list.assert_called_once_with(is_public=True)
        self.assertEqual(self.columns_long, columns)
        self.assertEqual(self.data_long, list(data))

    def test_type_list_with_private_option(self):
        arglist = [
            "--private",
        ]
        verifylist = [
            ("long", False),
            ("private", True),
            ("public", False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.types_mock.list.assert_called_once_with(is_public=False)
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, list(data))


class TestTypeSet(TestType):

    project = identity_fakes.FakeProject.create_one_project()
    volume_type = volume_fakes.FakeType.create_one_type(
        methods={'set_keys': None})

    def setUp(self):
        super(TestTypeSet, self).setUp()

        self.types_mock.get.return_value = self.volume_type

        # Return a project
        self.projects_mock.get.return_value = self.project
        # Get the command object to test
        self.cmd = volume_type.SetVolumeType(self.app, None)

    def test_type_set_name(self):
        new_name = 'new_name'
        arglist = [
            '--name', new_name,
            self.volume_type.id,
        ]
        verifylist = [
            ('name', new_name),
            ('description', None),
            ('property', None),
            ('volume_type', self.volume_type.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'name': new_name,
        }
        self.types_mock.update.assert_called_with(
            self.volume_type.id,
            **kwargs
        )
        self.assertIsNone(result)

    def test_type_set_description(self):
        new_desc = 'new_desc'
        arglist = [
            '--description', new_desc,
            self.volume_type.id,
        ]
        verifylist = [
            ('name', None),
            ('description', new_desc),
            ('property', None),
            ('volume_type', self.volume_type.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'description': new_desc,
        }
        self.types_mock.update.assert_called_with(
            self.volume_type.id,
            **kwargs
        )
        self.assertIsNone(result)

    def test_type_set_property(self):
        arglist = [
            '--property', 'myprop=myvalue',
            self.volume_type.id,
        ]
        verifylist = [
            ('name', None),
            ('description', None),
            ('property', {'myprop': 'myvalue'}),
            ('volume_type', self.volume_type.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.volume_type.set_keys.assert_called_once_with(
            {'myprop': 'myvalue'})
        self.assertIsNone(result)

    def test_type_set_not_called_without_project_argument(self):
        arglist = [
            '--project', '',
            self.volume_type.id,
        ]
        verifylist = [
            ('project', ''),
            ('volume_type', self.volume_type.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        self.assertFalse(self.types_access_mock.add_project_access.called)

    def test_type_set_failed_with_missing_volume_type_argument(self):
        arglist = [
            '--project', 'identity_fakes.project_id',
        ]
        verifylist = [
            ('project', 'identity_fakes.project_id'),
        ]

        self.assertRaises(tests_utils.ParserException,
                          self.check_parser,
                          self.cmd,
                          arglist,
                          verifylist)

    def test_type_set_project_access(self):
        arglist = [
            '--project', self.project.id,
            self.volume_type.id,
        ]
        verifylist = [
            ('project', self.project.id),
            ('volume_type', self.volume_type.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        self.types_access_mock.add_project_access.assert_called_with(
            self.volume_type.id,
            self.project.id,
        )


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
        super(TestTypeShow, self).setUp()

        self.volume_type = volume_fakes.FakeType.create_one_type()
        self.data = (
            None,
            self.volume_type.description,
            self.volume_type.id,
            True,
            self.volume_type.name,
            utils.format_dict(self.volume_type.extra_specs)
        )

        self.types_mock.get.return_value = self.volume_type

        # Get the command object to test
        self.cmd = volume_type.ShowVolumeType(self.app, None)

    def test_type_show(self):
        arglist = [
            self.volume_type.id
        ]
        verifylist = [
            ("volume_type", self.volume_type.id)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.types_mock.get.assert_called_with(self.volume_type.id)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

    def test_type_show_with_access(self):
        arglist = [
            self.volume_type.id
        ]
        verifylist = [
            ("volume_type", self.volume_type.id)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        private_type = volume_fakes.FakeType.create_one_type(
            attrs={'is_public': False})
        type_access_list = volume_fakes.FakeTypeAccess.create_one_type_access()
        with mock.patch.object(self.types_mock, 'get',
                               return_value=private_type):
            with mock.patch.object(self.types_access_mock, 'list',
                                   return_value=[type_access_list]):
                columns, data = self.cmd.take_action(parsed_args)
                self.types_mock.get.assert_called_once_with(
                    self.volume_type.id)
                self.types_access_mock.list.assert_called_once_with(
                    private_type.id)

        self.assertEqual(self.columns, columns)
        private_type_data = (
            utils.format_list([type_access_list.project_id]),
            private_type.description,
            private_type.id,
            private_type.is_public,
            private_type.name,
            utils.format_dict(private_type.extra_specs)
        )
        self.assertEqual(private_type_data, data)

    def test_type_show_with_list_access_exec(self):
        arglist = [
            self.volume_type.id
        ]
        verifylist = [
            ("volume_type", self.volume_type.id)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        private_type = volume_fakes.FakeType.create_one_type(
            attrs={'is_public': False})
        with mock.patch.object(self.types_mock, 'get',
                               return_value=private_type):
            with mock.patch.object(self.types_access_mock, 'list',
                                   side_effect=Exception()):
                columns, data = self.cmd.take_action(parsed_args)
                self.types_mock.get.assert_called_once_with(
                    self.volume_type.id)
                self.types_access_mock.list.assert_called_once_with(
                    private_type.id)

        self.assertEqual(self.columns, columns)
        private_type_data = (
            None,
            private_type.description,
            private_type.id,
            private_type.is_public,
            private_type.name,
            utils.format_dict(private_type.extra_specs)
        )
        self.assertEqual(private_type_data, data)


class TestTypeUnset(TestType):

    project = identity_fakes.FakeProject.create_one_project()
    volume_type = volume_fakes.FakeType.create_one_type(
        methods={'unset_keys': None})

    def setUp(self):
        super(TestTypeUnset, self).setUp()

        self.types_mock.get.return_value = self.volume_type

        # Return a project
        self.projects_mock.get.return_value = self.project

        # Get the command object to test
        self.cmd = volume_type.UnsetVolumeType(self.app, None)

    def test_type_unset(self):
        arglist = [
            '--property', 'property',
            '--property', 'multi_property',
            self.volume_type.id,
        ]
        verifylist = [
            ('property', ['property', 'multi_property']),
            ('volume_type', self.volume_type.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.volume_type.unset_keys.assert_called_once_with(
            ['property', 'multi_property'])
        self.assertIsNone(result)

    def test_type_unset_project_access(self):
        arglist = [
            '--project', self.project.id,
            self.volume_type.id,
        ]
        verifylist = [
            ('project', self.project.id),
            ('volume_type', self.volume_type.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        self.types_access_mock.remove_project_access.assert_called_with(
            self.volume_type.id,
            self.project.id,
        )

    def test_type_unset_not_called_without_project_argument(self):
        arglist = [
            '--project', '',
            self.volume_type.id,
        ]
        verifylist = [
            ('project', ''),
            ('volume_type', self.volume_type.id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        self.assertFalse(self.types_access_mock.remove_project_access.called)

    def test_type_unset_failed_with_missing_volume_type_argument(self):
        arglist = [
            '--project', 'identity_fakes.project_id',
        ]
        verifylist = [
            ('project', 'identity_fakes.project_id'),
        ]

        self.assertRaises(tests_utils.ParserException,
                          self.check_parser,
                          self.cmd,
                          arglist,
                          verifylist)
