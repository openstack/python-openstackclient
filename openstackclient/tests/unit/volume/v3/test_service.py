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

from unittest import mock

from openstack.block_storage.v3 import service as _service
from openstack.test import fakes as sdk_fakes
from osc_lib import exceptions

from openstackclient.tests.unit.volume.v3 import fakes as volume_fakes
from openstackclient.volume.v3 import service


class TestServiceList(volume_fakes.TestVolume):
    def setUp(self):
        super().setUp()

        self.service = sdk_fakes.generate_fake_resource(_service.Service)
        self.volume_sdk_client.services.return_value = [self.service]

        self.cmd = service.ListService(self.app, None)

    def test_service_list(self):
        arglist = [
            '--host',
            self.service.host,
            '--service',
            self.service.binary,
        ]
        verifylist = [
            ('host', self.service.host),
            ('service', self.service.binary),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        expected_columns = (
            'Binary',
            'Host',
            'Zone',
            'Status',
            'State',
            'Updated At',
        )
        datalist = (
            (
                self.service.binary,
                self.service.host,
                self.service.availability_zone,
                self.service.status,
                self.service.state,
                self.service.updated_at,
            ),
        )
        self.assertEqual(expected_columns, columns)
        self.assertEqual(datalist, tuple(data))
        self.volume_sdk_client.services.assert_called_with(
            host=self.service.host,
            binary=self.service.binary,
        )

    def test_service_list_with_long_option(self):
        arglist = [
            '--host',
            self.service.host,
            '--service',
            self.service.binary,
            '--long',
        ]
        verifylist = [
            ('host', self.service.host),
            ('service', self.service.binary),
            ('long', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        expected_columns = (
            'Binary',
            'Host',
            'Zone',
            'Status',
            'State',
            'Updated At',
            'Disabled Reason',
        )
        datalist = (
            (
                self.service.binary,
                self.service.host,
                self.service.availability_zone,
                self.service.status,
                self.service.state,
                self.service.updated_at,
                self.service.disabled_reason,
            ),
        )
        self.assertEqual(expected_columns, columns)
        self.assertEqual(datalist, tuple(data))
        self.volume_sdk_client.services.assert_called_with(
            host=self.service.host,
            binary=self.service.binary,
        )

    def test_service_list_with_cluster(self):
        self.set_volume_api_version('3.7')

        arglist = [
            '--host',
            self.service.host,
            '--service',
            self.service.binary,
        ]
        verifylist = [
            ('host', self.service.host),
            ('service', self.service.binary),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        expected_columns = (
            'Binary',
            'Host',
            'Zone',
            'Status',
            'State',
            'Updated At',
            'Cluster',
        )
        datalist = (
            (
                self.service.binary,
                self.service.host,
                self.service.availability_zone,
                self.service.status,
                self.service.state,
                self.service.updated_at,
                self.service.cluster,
            ),
        )
        self.assertEqual(expected_columns, columns)
        self.assertEqual(datalist, tuple(data))
        self.volume_sdk_client.services.assert_called_with(
            host=self.service.host,
            binary=self.service.binary,
        )

    def test_service_list_with_backend_state(self):
        self.set_volume_api_version('3.49')

        arglist = [
            '--host',
            self.service.host,
            '--service',
            self.service.binary,
        ]
        verifylist = [
            ('host', self.service.host),
            ('service', self.service.binary),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        expected_columns = (
            'Binary',
            'Host',
            'Zone',
            'Status',
            'State',
            'Updated At',
            'Cluster',
            'Backend State',
        )
        datalist = (
            (
                self.service.binary,
                self.service.host,
                self.service.availability_zone,
                self.service.status,
                self.service.state,
                self.service.updated_at,
                self.service.cluster,
                self.service.backend_state,
            ),
        )
        self.assertEqual(expected_columns, columns)
        self.assertEqual(datalist, tuple(data))
        self.volume_sdk_client.services.assert_called_with(
            host=self.service.host,
            binary=self.service.binary,
        )


class TestServiceSet(volume_fakes.TestVolume):
    def setUp(self):
        super().setUp()

        self.service = sdk_fakes.generate_fake_resource(_service.Service)
        self.service.enable = mock.Mock(autospec=True)
        self.service.disable = mock.Mock(autospec=True)
        self.volume_sdk_client.find_service.return_value = self.service

        self.cmd = service.SetService(self.app, None)

    def test_service_set_nothing(self):
        arglist = [
            self.service.host,
            self.service.binary,
        ]
        verifylist = [
            ('host', self.service.host),
            ('service', self.service.binary),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.service.enable.assert_not_called()
        self.service.disable.assert_not_called()
        self.assertIsNone(result)

    def test_service_set_enable(self):
        arglist = [
            '--enable',
            self.service.host,
            self.service.binary,
        ]
        verifylist = [
            ('enable', True),
            ('host', self.service.host),
            ('service', self.service.binary),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.service.enable.assert_called_with(self.volume_sdk_client)
        self.service.disable.assert_not_called()
        self.assertIsNone(result)

    def test_service_set_disable(self):
        arglist = [
            '--disable',
            self.service.host,
            self.service.binary,
        ]
        verifylist = [
            ('disable', True),
            ('host', self.service.host),
            ('service', self.service.binary),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.service.enable.assert_not_called()
        self.service.disable.assert_called_with(
            self.volume_sdk_client, reason=None
        )
        self.assertIsNone(result)

    def test_service_set_disable_with_reason(self):
        reason = 'earthquake'
        arglist = [
            '--disable',
            '--disable-reason',
            reason,
            self.service.host,
            self.service.binary,
        ]
        verifylist = [
            ('disable', True),
            ('disable_reason', reason),
            ('host', self.service.host),
            ('service', self.service.binary),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.service.enable.assert_not_called()
        self.service.disable.assert_called_with(
            self.volume_sdk_client, reason=reason
        )
        self.assertIsNone(result)

    def test_service_set_only_with_disable_reason(self):
        reason = 'earthquake'
        arglist = [
            '--disable-reason',
            reason,
            self.service.host,
            self.service.binary,
        ]
        verifylist = [
            ('disable_reason', reason),
            ('host', self.service.host),
            ('service', self.service.binary),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        try:
            self.cmd.take_action(parsed_args)
            self.fail("CommandError should be raised.")
        except exceptions.CommandError as e:
            self.assertEqual(
                "Cannot specify option --disable-reason without "
                "--disable specified.",
                str(e),
            )

    def test_service_set_enable_with_disable_reason(self):
        reason = 'earthquake'
        arglist = [
            '--enable',
            '--disable-reason',
            reason,
            self.service.host,
            self.service.binary,
        ]
        verifylist = [
            ('enable', True),
            ('disable_reason', reason),
            ('host', self.service.host),
            ('service', self.service.binary),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        try:
            self.cmd.take_action(parsed_args)
            self.fail("CommandError should be raised.")
        except exceptions.CommandError as e:
            self.assertEqual(
                "Cannot specify option --disable-reason without "
                "--disable specified.",
                str(e),
            )
