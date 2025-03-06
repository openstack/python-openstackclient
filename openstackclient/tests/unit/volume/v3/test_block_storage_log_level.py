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

import ddt
from openstack.block_storage.v3 import service as _service
from openstack.test import fakes as sdk_fakes
from osc_lib import exceptions

from openstackclient.tests.unit import utils as tests_utils
from openstackclient.tests.unit.volume.v3 import fakes as volume_fakes
from openstackclient.volume.v3 import block_storage_log_level as service


class TestBlockStorageLogLevelList(volume_fakes.TestVolume):
    def setUp(self):
        super().setUp()

        self.log_level = sdk_fakes.generate_fake_resource(
            _service.LogLevel, binary='cinder-scheduler'
        )
        self.volume_sdk_client.get_service_log_levels.return_value = [
            self.log_level
        ]

        self.cmd = service.BlockStorageLogLevelList(self.app, None)

    def test_block_storage_log_level_list(self):
        self.set_volume_api_version('3.32')

        arglist = [
            '--host',
            self.log_level.host,
            '--service',
            self.log_level.binary,
            '--log-prefix',
            'cinder.',
        ]
        verifylist = [
            ('host', self.log_level.host),
            ('service', self.log_level.binary),
            ('log_prefix', 'cinder.'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        expected_columns = [
            'Binary',
            'Host',
            'Prefix',
            'Level',
        ]
        datalist = tuple(
            (
                self.log_level.binary,
                self.log_level.host,
                prefix,
                level,
            )
            for prefix, level in self.log_level.levels.values()
        )
        self.assertEqual(expected_columns, columns)
        self.assertEqual(datalist, tuple(data))

        self.volume_sdk_client.get_service_log_levels.assert_called_with(
            server=self.log_level.host,
            binary=self.log_level.binary,
            prefix='cinder.',
        )

    def test_block_storage_log_level_list_pre_332(self):
        arglist = [
            '--host',
            self.log_level.host,
            '--service',
            'cinder-api',
            '--log-prefix',
            'cinder_test.api.common',
        ]
        verifylist = [
            ('host', self.log_level.host),
            ('service', 'cinder-api'),
            ('log_prefix', 'cinder_test.api.common'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-volume-api-version 3.32 or greater is required', str(exc)
        )

    def test_block_storage_log_level_list_invalid_service_name(self):
        self.set_volume_api_version('3.32')

        arglist = [
            '--host',
            self.log_level.host,
            '--service',
            'nova-api',
            '--log-prefix',
            'cinder_test.api.common',
        ]
        verifylist = [
            ('host', self.log_level.host),
            ('service', 'nova-api'),
            ('log_prefix', 'cinder_test.api.common'),
        ]

        self.assertRaises(
            tests_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )


@ddt.ddt
class TestBlockStorageLogLevelSet(volume_fakes.TestVolume):
    def setUp(self):
        super().setUp()

        self.log_level = sdk_fakes.generate_fake_resource(
            _service.LogLevel, binary='cinder-api'
        )
        self.volume_sdk_client.set_service_log_levels.return_value = None

        self.cmd = service.BlockStorageLogLevelSet(self.app, None)

    def test_block_storage_log_level_set(self):
        self.set_volume_api_version('3.32')

        arglist = [
            'ERROR',
            '--host',
            self.log_level.host,
            '--service',
            self.log_level.binary,
            '--log-prefix',
            'cinder.api.common',
        ]
        verifylist = [
            ('level', 'ERROR'),
            ('host', self.log_level.host),
            ('service', self.log_level.binary),
            ('log_prefix', 'cinder.api.common'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        ret = self.cmd.take_action(parsed_args)

        self.assertIsNone(ret)
        self.volume_sdk_client.set_service_log_levels.assert_called_with(
            level='ERROR',
            server=self.log_level.host,
            binary=self.log_level.binary,
            prefix='cinder.api.common',
        )

    def test_block_storage_log_level_set_pre_332(self):
        arglist = [
            'ERROR',
            '--host',
            self.log_level.host,
            '--service',
            'cinder-api',
            '--log-prefix',
            'cinder.api.common',
        ]
        verifylist = [
            ('level', 'ERROR'),
            ('host', self.log_level.host),
            ('service', 'cinder-api'),
            ('log_prefix', 'cinder.api.common'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-volume-api-version 3.32 or greater is required', str(exc)
        )

    def test_block_storage_log_level_set_invalid_service_name(self):
        self.set_volume_api_version('3.32')

        arglist = [
            'ERROR',
            '--host',
            self.log_level.host,
            '--service',
            'nova-api',
            '--log-prefix',
            'cinder.api.common',
        ]
        verifylist = [
            ('level', 'ERROR'),
            ('host', self.log_level.host),
            ('service', 'nova-api'),
            ('log_prefix', 'cinder.api.common'),
        ]

        self.assertRaises(
            tests_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    @ddt.data('WARNING', 'info', 'Error', 'debuG', 'fake-log-level')
    def test_block_storage_log_level_set_log_level(self, log_level):
        self.set_volume_api_version('3.32')

        arglist = [
            log_level,
            '--host',
            self.log_level.host,
            '--service',
            'cinder-api',
            '--log-prefix',
            'cinder.api.common',
        ]
        verifylist = [
            ('level', log_level.upper()),
            ('host', self.log_level.host),
            ('service', 'cinder-api'),
            ('log_prefix', 'cinder.api.common'),
        ]

        if log_level == 'fake-log-level':
            self.assertRaises(
                tests_utils.ParserException,
                self.check_parser,
                self.cmd,
                arglist,
                verifylist,
            )
        else:
            parsed_args = self.check_parser(self.cmd, arglist, verifylist)

            self.cmd.take_action(parsed_args)

            self.volume_sdk_client.set_service_log_levels.assert_called_with(
                level=log_level.upper(),
                server=self.log_level.host,
                binary=self.log_level.binary,
                prefix='cinder.api.common',
            )
