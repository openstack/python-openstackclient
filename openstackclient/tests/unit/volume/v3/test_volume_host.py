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

from openstack.block_storage.v3 import service as _service
from openstack.test import fakes as sdk_fakes

from openstackclient.tests.unit.volume.v3 import fakes as volume_fakes
from openstackclient.volume.v3 import volume_host


class TestVolumeHostSet(volume_fakes.TestVolume):
    def setUp(self):
        super().setUp()
        self.service = sdk_fakes.generate_fake_resource(_service.Service)
        self.cmd = volume_host.SetVolumeHost(self.app, None)

    def test_volume_host_set_nothing(self):
        arglist = [self.service.host]
        verifylist = [('host', self.service.host)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.freeze_service.assert_not_called()
        self.volume_sdk_client.thaw_service.assert_not_called()
        self.assertIsNone(result)

    def test_volume_host_set_enable(self):
        arglist = ['--enable', self.service.host]
        verifylist = [('enable', True), ('host', self.service.host)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.thaw_service.assert_called_once_with(
            _service.Service(host=self.service.host)
        )
        self.volume_sdk_client.freeze_service.assert_not_called()
        self.assertIsNone(result)

    def test_volume_host_set_disable(self):
        arglist = ['--disable', self.service.host]
        verifylist = [('disable', True), ('host', self.service.host)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.freeze_service.assert_called_once_with(
            _service.Service(host=self.service.host)
        )
        self.volume_sdk_client.thaw_service.assert_not_called()
        self.assertIsNone(result)


class TestVolumeHostFailover(volume_fakes.TestVolume):
    def setUp(self):
        super().setUp()
        self.service = sdk_fakes.generate_fake_resource(_service.Service)
        self.cmd = volume_host.FailoverVolumeHost(self.app, None)

    def test_volume_host_failover(self):
        arglist = ['--volume-backend', 'backend_test', self.service.host]
        verifylist = [
            ('volume_backend', 'backend_test'),
            ('host', self.service.host),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.volume_sdk_client.failover_service.assert_called_once_with(
            _service.Service(host=self.service.host),
            backend_id='backend_test',
        )
        self.assertIsNone(result)
