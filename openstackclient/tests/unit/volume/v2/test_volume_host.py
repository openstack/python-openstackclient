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

from openstackclient.tests.unit.volume.v2 import fakes as host_fakes
from openstackclient.volume.v2 import volume_host


class TestVolumeHost(host_fakes.TestVolume):

    def setUp(self):
        super(TestVolumeHost, self).setUp()

        self.host_mock = self.app.client_manager.volume.services
        self.host_mock.reset_mock()


class TestVolumeHostSet(TestVolumeHost):

    service = host_fakes.FakeService.create_one_service()

    def setUp(self):
        super(TestVolumeHostSet, self).setUp()

        self.host_mock.freeze_host.return_value = None
        self.host_mock.thaw_host.return_value = None

        # Get the command object to mock
        self.cmd = volume_host.SetVolumeHost(self.app, None)

    def test_volume_host_set_nothing(self):
        arglist = [
            self.service.host,
        ]
        verifylist = [
            ('host', self.service.host),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.host_mock.freeze_host.assert_not_called()
        self.host_mock.thaw_host.assert_not_called()
        self.assertIsNone(result)

    def test_volume_host_set_enable(self):
        arglist = [
            '--enable',
            self.service.host,
        ]
        verifylist = [
            ('enable', True),
            ('host', self.service.host),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.host_mock.thaw_host.assert_called_with(self.service.host)
        self.host_mock.freeze_host.assert_not_called()
        self.assertIsNone(result)

    def test_volume_host_set_disable(self):
        arglist = [
            '--disable',
            self.service.host,
        ]
        verifylist = [
            ('disable', True),
            ('host', self.service.host),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.host_mock.freeze_host.assert_called_with(self.service.host)
        self.host_mock.thaw_host.assert_not_called()
        self.assertIsNone(result)


class TestVolumeHostFailover(TestVolumeHost):

    service = host_fakes.FakeService.create_one_service()

    def setUp(self):
        super(TestVolumeHostFailover, self).setUp()

        self.host_mock.failover_host.return_value = None

        # Get the command object to mock
        self.cmd = volume_host.FailoverVolumeHost(self.app, None)

    def test_volume_host_failover(self):
        arglist = [
            '--volume-backend', 'backend_test',
            self.service.host,
        ]
        verifylist = [
            ('volume_backend', 'backend_test'),
            ('host', self.service.host),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.host_mock.failover_host.assert_called_with(
            self.service.host, 'backend_test')
        self.assertIsNone(result)
