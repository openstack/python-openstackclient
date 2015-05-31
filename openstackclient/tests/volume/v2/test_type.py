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

from openstackclient.tests import fakes
from openstackclient.tests.volume.v2 import fakes as volume_fakes
from openstackclient.volume.v2 import volume_type


class TestType(volume_fakes.TestVolume):

    def setUp(self):
        super(TestType, self).setUp()

        self.types_mock = self.app.client_manager.volume.volume_types
        self.types_mock.reset_mock()


class TestTypeShow(TestType):
    def setUp(self):
        super(TestTypeShow, self).setUp()

        self.types_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(volume_fakes.TYPE),
            loaded=True)
        # Get the command object to test
        self.cmd = volume_type.ShowVolumeType(self.app, None)

    def test_type_show(self):
        arglist = [
            volume_fakes.type_id
        ]
        verifylist = [
            ("volume_type", volume_fakes.type_id)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        self.types_mock.get.assert_called_with(volume_fakes.type_id)

        self.assertEqual(volume_fakes.TYPE_columns, columns)
        self.assertEqual(volume_fakes.TYPE_data, data)


class TestTypeDelete(TestType):
    def setUp(self):
        super(TestTypeDelete, self).setUp()

        self.types_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(volume_fakes.TYPE),
            loaded=True)
        self.types_mock.delete.return_value = None

        # Get the command object to mock
        self.cmd = volume_type.DeleteVolumeType(self.app, None)

    def test_type_delete(self):
        arglist = [
            volume_fakes.type_id
        ]
        verifylist = [
            ("volume_type", volume_fakes.type_id)
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        self.types_mock.delete.assert_called_with(volume_fakes.type_id)
