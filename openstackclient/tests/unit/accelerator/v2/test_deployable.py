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

from openstack.accelerator.v2 import deployable as _deployable
from openstack.test import fakes as sdk_fakes

from openstackclient.accelerator.v2 import deployable
from openstackclient.tests.unit.accelerator.v2 import (
    fakes as accelerator_fakes,
)

SHOW_COLUMNS = (
    "created_at",
    "updated_at",
    "uuid",
    "name",
)

LIST_COLUMNS_SHORT = (
    "uuid",
    "name",
    "device_id",
)

LIST_COLUMNS_LONG = (
    "created_at",
    "updated_at",
    *LIST_COLUMNS_SHORT,
    "parent_id",
    "root_id",
    "num_accelerators",
)


class TestDeployable(accelerator_fakes.TestAccelerator):
    def setUp(self):
        super().setUp()

        self.fake_dep = sdk_fakes.generate_fake_resource(
            _deployable.Deployable
        )
        self.data = tuple(
            self.fake_dep[("id" if c == "uuid" else c)] for c in SHOW_COLUMNS
        )


class TestListDeployable(TestDeployable):
    def setUp(self):
        super().setUp()

        self.accelerator_client.deployables.return_value = [self.fake_dep]
        self.cmd = deployable.ListDeployable(self.app, None)

    def test_list(self):
        parsed_args = self.check_parser(self.cmd, [], [])
        columns, data = self.cmd.take_action(parsed_args)

        self.accelerator_client.deployables.assert_called_once_with()
        self.assertEqual(LIST_COLUMNS_SHORT, columns)

        expected_data = (
            tuple(
                self.fake_dep[("id" if c == "uuid" else c)]
                for c in LIST_COLUMNS_SHORT
            ),
        )
        self.assertCountEqual(expected_data, tuple(data))

    def test_list_long(self):
        arglist = ['--long']
        verifylist = [('detail', True)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(LIST_COLUMNS_LONG, columns)

        expected_data = (
            tuple(
                self.fake_dep[("id" if c == "uuid" else c)]
                for c in LIST_COLUMNS_LONG
            ),
        )
        self.assertCountEqual(expected_data, tuple(data))


class TestProgramDeployable(TestDeployable):
    def setUp(self):
        super().setUp()

        self.accelerator_client.get_deployable.return_value = self.fake_dep
        self.cmd = deployable.ProgramDeployable(self.app, None)

    def test_program(self):
        arglist = [self.fake_dep.id, 'image-uuid-1']
        verifylist = [
            ('deployable_uuid', self.fake_dep.id),
            ('image_uuid', 'image-uuid-1'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.accelerator_client.get_deployable.assert_any_call(
            self.fake_dep.id
        )
        self.app.client_manager.image.get_image.assert_called_once_with(
            'image-uuid-1'
        )

        expected_patch = [
            {
                'op': 'replace',
                'path': '/program',
                'value': [{'image_uuid': 'image-uuid-1'}],
            }
        ]
        self.accelerator_client.patch_deployable.assert_called_once_with(
            self.fake_dep.id, expected_patch
        )
        self.assertEqual(SHOW_COLUMNS, columns)
        self.assertCountEqual(self.data, data)


class TestShowDeployable(TestDeployable):
    def setUp(self):
        super().setUp()

        self.accelerator_client.get_deployable.return_value = self.fake_dep
        self.cmd = deployable.ShowDeployable(self.app, None)

    def test_show(self):
        arglist = [self.fake_dep.id]
        verifylist = [
            ('deployable', self.fake_dep.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.accelerator_client.get_deployable.assert_called_once_with(
            self.fake_dep.id
        )
        self.assertEqual(SHOW_COLUMNS, columns)
        self.assertCountEqual(self.data, data)
