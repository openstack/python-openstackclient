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

from openstack.block_storage.v3 import default_type as _default_type
from openstack.block_storage.v3 import type as _type
from openstack.identity.v3 import project as _project
from openstack.test import fakes as sdk_fakes
from osc_lib import exceptions

from openstackclient.tests.unit.volume.v3 import fakes
from openstackclient.volume.v3 import default_type


class TestDefaultTypeBase(fakes.TestVolume):
    def setUp(self):
        super().setUp()

        self.volume_type = sdk_fakes.generate_fake_resource(_type.Type)
        self.project = sdk_fakes.generate_fake_resource(_project.Project)
        self.default_type = sdk_fakes.generate_fake_resource(
            _default_type.DefaultType,
            project_id=self.project.id,
            volume_type_id=self.volume_type.id,
        )
        self.volume_client.find_type.return_value = self.volume_type
        self.set_volume_api_version('3.67')


class TestDefaultTypeSet(TestDefaultTypeBase):
    def setUp(self):
        super().setUp()
        self.volume_client.set_default_type.return_value = self.default_type
        self.columns = (
            'Project ID',
            'Volume Type ID',
        )
        self.data = (
            self.project.id,
            self.volume_type.id,
        )
        # Get the command object to test
        self.cmd = default_type.SetDefaultType(self.app, None)

    def test_default_type_set(self):
        self.set_volume_api_version('3.67')
        arglist = [
            self.volume_type.id,
            self.project.id,
        ]
        verifylist = [
            ("volume_type", self.volume_type.id),
            ("project", self.project.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.volume_client.find_type.assert_called_once_with(
            self.volume_type.id, ignore_missing=False
        )
        self.volume_client.set_default_type.assert_called_with(
            self.project.id,
            self.volume_type.id,
        )

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_default_type_set_by_name(self) -> None:
        parsed_args = self.check_parser(
            self.cmd,
            [self.volume_type.name, self.project.id],
            [('volume_type', self.volume_type.name)],
        )

        self.cmd.take_action(parsed_args)

        self.volume_client.find_type.assert_called_once_with(
            self.volume_type.name, ignore_missing=False
        )
        self.volume_client.set_default_type.assert_called_once_with(
            self.project.id, self.volume_type.id
        )

    def test_default_type_set_pre_3_67(self):
        self.set_volume_api_version('3.66')
        arglist = [
            self.volume_type.id,
            self.project.id,
        ]
        verifylist = [
            ("volume_type", self.volume_type.id),
            ("project", self.project.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-volume-api-version 3.67 or greater is required', str(exc)
        )


class TestDefaultTypeList(TestDefaultTypeBase):
    def setUp(self):
        super().setUp()

        self.project_new = sdk_fakes.generate_fake_resource(_project.Project)
        self.volume_type_new = sdk_fakes.generate_fake_resource(_type.Type)
        self.default_type_new = sdk_fakes.generate_fake_resource(
            _default_type.DefaultType,
            project_id=self.project_new.id,
            volume_type_id=self.volume_type_new.id,
        )
        self.volume_client.default_types.return_value = [
            self.default_type,
            self.default_type_new,
        ]
        self.columns = [
            'Project ID',
            'Volume Type ID',
        ]
        self.data = []
        for t in [self.default_type, self.default_type_new]:
            self.data.append(
                (
                    t.project_id,
                    t.volume_type_id,
                )
            )
        # Get the command object to test
        self.cmd = default_type.ListDefaultType(self.app, None)

    def test_default_type_list(self):
        self.set_volume_api_version('3.67')
        parsed_args = self.check_parser(self.cmd, [], [])

        columns, data = self.cmd.take_action(parsed_args)
        self.volume_client.default_types.assert_called_with()

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_default_type_list_pre_3_67(self):
        self.set_volume_api_version('3.66')
        parsed_args = self.check_parser(self.cmd, [], [])

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-volume-api-version 3.67 or greater is required', str(exc)
        )


class TestDefaultTypeShow(TestDefaultTypeBase):
    def setUp(self):
        super().setUp()
        self.volume_client.show_default_type.return_value = self.default_type
        self.columns = [
            'Project ID',
            'Volume Type ID',
        ]
        self.data = (
            self.project.id,
            self.volume_type.id,
        )
        # Get the command object to test
        self.cmd = default_type.ShowDefaultType(self.app, None)

    def test_default_type_show(self):
        self.set_volume_api_version('3.67')
        arglist = [
            self.project.id,
        ]
        verifylist = [
            ("project", self.project.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.volume_client.show_default_type.assert_called_with(
            self.project.id,
        )

        self.assertEqual(self.columns, columns)
        self.assertCountEqual(self.data, data)

    def test_default_type_show_pre_3_67(self):
        self.set_volume_api_version('3.66')
        arglist = [
            self.project.id,
        ]
        verifylist = [
            ("project", self.project.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-volume-api-version 3.67 or greater is required', str(exc)
        )


class TestDefaultTypeUnset(TestDefaultTypeBase):
    def setUp(self):
        super().setUp()
        # Get the command object to test
        self.cmd = default_type.UnsetDefaultType(self.app, None)

    def test_default_type_unset(self):
        self.set_volume_api_version('3.67')
        arglist = [
            self.project.id,
        ]
        verifylist = [
            ("project", self.project.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.volume_client.unset_default_type.assert_called_with(
            self.project.id,
        )

    def test_default_type_show_pre_3_67(self):
        self.set_volume_api_version('3.66')
        arglist = [
            self.project.id,
        ]
        verifylist = [
            ("project", self.project.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-volume-api-version 3.67 or greater is required', str(exc)
        )
