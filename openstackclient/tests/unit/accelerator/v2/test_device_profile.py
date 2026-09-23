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

from openstack.accelerator.v2 import (
    device_profile as _device_profile,
)
from openstack.test import fakes as sdk_fakes
from osc_lib import exceptions

from openstackclient.accelerator.v2 import device_profile
from openstackclient.tests.unit.accelerator.v2 import fakes


class TestDeviceProfile(fakes.TestAccelerator):
    show_columns = (
        "created_at",
        "updated_at",
        "uuid",
        "name",
        "groups",
        "description",
    )

    def setUp(self):
        super().setUp()

        self.fake_dp = sdk_fakes.generate_fake_resource(
            _device_profile.DeviceProfile,
        )
        self.show_data = (
            self.fake_dp.created_at,
            self.fake_dp.updated_at,
            self.fake_dp.uuid,
            self.fake_dp.name,
            self.fake_dp.groups,
            self.fake_dp.description,
        )


class TestCreateDeviceProfile(TestDeviceProfile):
    def setUp(self):
        super().setUp()

        self.accelerator_client.create_device_profile.return_value = (
            self.fake_dp
        )
        self.cmd = device_profile.CreateDeviceProfile(self.app, None)

    def test_create(self):
        groups_json = '[{"resources:FPGA": 1}]'
        arglist = [
            self.fake_dp.name,
            groups_json,
        ]
        verifylist = [
            ('name', self.fake_dp.name),
            ('groups', groups_json),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.accelerator_client.create_device_profile.assert_called_once_with(
            name=self.fake_dp.name,
            groups=[{"resources:FPGA": 1}],
            description=None,
        )
        self.assertEqual(self.show_columns, columns)
        self.assertCountEqual(self.show_data, data)

    def test_create_with_description(self):
        groups_json = '[{"resources:FPGA": 1}]'
        arglist = [
            self.fake_dp.name,
            groups_json,
            '--description',
            'test desc',
        ]
        verifylist = [
            ('name', self.fake_dp.name),
            ('groups', groups_json),
            ('description', 'test desc'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.accelerator_client.create_device_profile.assert_called_once_with(
            name=self.fake_dp.name,
            groups=[{"resources:FPGA": 1}],
            description='test desc',
        )
        self.assertEqual(self.show_columns, columns)
        self.assertCountEqual(self.show_data, data)


class TestDeleteDeviceProfile(TestDeviceProfile):
    def setUp(self):
        super().setUp()

        self.fake_dps = list(
            sdk_fakes.generate_fake_resources(_device_profile.DeviceProfile, 2)
        )
        self.cmd = device_profile.DeleteDeviceProfile(self.app, None)

    def test_delete(self):
        arglist = [self.fake_dps[0].uuid]
        verifylist = [
            ('device_profiles', [self.fake_dps[0].uuid]),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        self.accelerator_client.delete_device_profile.assert_called_once_with(
            self.fake_dps[0].uuid,
            ignore_missing=False,
        )

    def test_delete_multiple(self):
        arglist = [dp.uuid for dp in self.fake_dps]
        verifylist = [
            ('device_profiles', arglist),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.cmd.take_action(parsed_args)

        self.assertEqual(
            self.accelerator_client.delete_device_profile.call_count,
            len(self.fake_dps),
        )

    def test_delete_with_error(self):
        arglist = [
            self.fake_dps[0].uuid,
            'nonexistent',
        ]
        verifylist = [
            ('device_profiles', arglist),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.accelerator_client.delete_device_profile.side_effect = [
            None,
            Exception('not found'),
        ]
        try:
            self.cmd.take_action(parsed_args)
            self.fail('CommandError should be raised.')
        except exceptions.CommandError as e:
            self.assertEqual(
                '1 of 2 device profiles failed to delete.',
                str(e),
            )


class TestListDeviceProfile(TestDeviceProfile):
    def setUp(self):
        super().setUp()

        self.accelerator_client.device_profiles.return_value = [
            self.fake_dp,
        ]
        self.cmd = device_profile.ListDeviceProfile(self.app, None)

    def test_list(self):
        parsed_args = self.check_parser(self.cmd, [], [])
        columns, data = self.cmd.take_action(parsed_args)

        expected_columns = (
            "uuid",
            "name",
            "groups",
            "description",
        )
        expected_data = (
            (
                self.fake_dp.uuid,
                self.fake_dp.name,
                self.fake_dp.groups,
                self.fake_dp.description,
            ),
        )

        self.accelerator_client.device_profiles.assert_called_once_with()
        self.assertEqual(expected_columns, columns)
        self.assertCountEqual(expected_data, tuple(data))

    def test_list_long(self):
        arglist = ['--long']
        verifylist = [('detail', True)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        expected_columns = (
            "uuid",
            "name",
            "groups",
            "description",
            "created_at",
            "updated_at",
        )
        expected_data = (
            (
                self.fake_dp.uuid,
                self.fake_dp.name,
                self.fake_dp.groups,
                self.fake_dp.description,
                self.fake_dp.created_at,
                self.fake_dp.updated_at,
            ),
        )

        self.accelerator_client.device_profiles.assert_called_once_with()
        self.assertEqual(expected_columns, columns)
        self.assertCountEqual(expected_data, tuple(data))


class TestShowDeviceProfile(TestDeviceProfile):
    def setUp(self):
        super().setUp()

        self.accelerator_client.get_device_profile.return_value = self.fake_dp
        self.cmd = device_profile.ShowDeviceProfile(self.app, None)

    def test_show(self):
        arglist = [self.fake_dp.uuid]
        verifylist = [
            ('device_profile', self.fake_dp.uuid),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.accelerator_client.get_device_profile.assert_called_once_with(
            self.fake_dp.uuid
        )
        self.assertEqual(self.show_columns, columns)
        self.assertCountEqual(self.show_data, data)
