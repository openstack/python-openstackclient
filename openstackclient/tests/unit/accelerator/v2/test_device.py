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

from openstack.accelerator.v2 import device as _device
from openstack.test import fakes as sdk_fakes

from openstackclient.accelerator.v2 import device
from openstackclient.tests.unit.accelerator.v2 import fakes


class TestDevice(fakes.TestAccelerator):
    show_columns = (
        "created_at",
        "updated_at",
        "uuid",
        "type",
        "vendor",
        "model",
        "hostname",
        "std_board_info",
        "vendor_board_info",
    )

    def setUp(self):
        super().setUp()

        self.fake_device = sdk_fakes.generate_fake_resource(
            _device.Device,
        )
        self.show_data = (
            self.fake_device.created_at,
            self.fake_device.updated_at,
            self.fake_device.uuid,
            self.fake_device.type,
            self.fake_device.vendor,
            self.fake_device.model,
            self.fake_device.hostname,
            self.fake_device.std_board_info,
            self.fake_device.vendor_board_info,
        )


class TestListDevice(TestDevice):
    def setUp(self):
        super().setUp()

        self.accelerator_client.devices.return_value = [
            self.fake_device,
        ]
        self.cmd = device.ListDevice(self.app, None)

    def test_list(self):
        parsed_args = self.check_parser(self.cmd, [], [])
        columns, data = self.cmd.take_action(parsed_args)

        expected_columns = (
            "uuid",
            "type",
            "vendor",
            "hostname",
            "std_board_info",
        )
        expected_data = (
            (
                self.fake_device.uuid,
                self.fake_device.type,
                self.fake_device.vendor,
                self.fake_device.hostname,
                self.fake_device.std_board_info,
            ),
        )

        self.accelerator_client.devices.assert_called_once_with()
        self.assertEqual(expected_columns, columns)
        self.assertCountEqual(expected_data, tuple(data))

    def test_list_long(self):
        arglist = ['--long']
        verifylist = [('detail', True)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        expected_columns = (
            "uuid",
            "type",
            "vendor",
            "hostname",
            "std_board_info",
            "created_at",
            "updated_at",
            "model",
            "vendor_board_info",
        )
        expected_data = (
            (
                self.fake_device.uuid,
                self.fake_device.type,
                self.fake_device.vendor,
                self.fake_device.hostname,
                self.fake_device.std_board_info,
                self.fake_device.created_at,
                self.fake_device.updated_at,
                self.fake_device.model,
                self.fake_device.vendor_board_info,
            ),
        )

        self.accelerator_client.devices.assert_called_once_with()
        self.assertEqual(expected_columns, columns)
        self.assertCountEqual(expected_data, tuple(data))


class TestShowDevice(TestDevice):
    def setUp(self):
        super().setUp()

        self.accelerator_client.get_device.return_value = self.fake_device
        self.cmd = device.ShowDevice(self.app, None)

    def test_show(self):
        arglist = [self.fake_device.uuid]
        verifylist = [('device', self.fake_device.uuid)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        self.accelerator_client.get_device.assert_called_once_with(
            self.fake_device.uuid
        )
        self.assertEqual(self.show_columns, columns)
        self.assertCountEqual(self.show_data, data)
