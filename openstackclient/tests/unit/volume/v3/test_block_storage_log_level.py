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

import ddt
from osc_lib import exceptions

from openstackclient.tests.unit import utils as tests_utils
from openstackclient.tests.unit.volume.v3 import fakes as volume_fakes
from openstackclient.volume.v3 import block_storage_log_level as service


class TestService(volume_fakes.TestVolume):
    def setUp(self):
        super().setUp()

        # Get a shortcut to the ServiceManager Mock
        self.service_mock = self.volume_client.services
        self.service_mock.reset_mock()


class TestBlockStorageLogLevelList(TestService):
    service_log = volume_fakes.create_service_log_level_entry()

    def setUp(self):
        super().setUp()

        self.service_mock.get_log_levels.return_value = [self.service_log]

        # Get the command object to test
        self.cmd = service.BlockStorageLogLevelList(self.app, None)

    def test_block_storage_log_level_list(self):
        self.set_volume_api_version('3.32')

        arglist = [
            '--host',
            self.service_log.host,
            '--service',
            self.service_log.binary,
            '--log-prefix',
            self.service_log.prefix,
        ]
        verifylist = [
            ('host', self.service_log.host),
            ('service', self.service_log.binary),
            ('log_prefix', self.service_log.prefix),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        expected_columns = [
            'Binary',
            'Host',
            'Prefix',
            'Level',
        ]

        # confirming if all expected columns are present in the result.
        self.assertEqual(expected_columns, columns)

        datalist = (
            (
                self.service_log.binary,
                self.service_log.host,
                self.service_log.prefix,
                self.service_log.level,
            ),
        )

        # confirming if all expected values are present in the result.
        self.assertEqual(datalist, tuple(data))

        # checking if proper call was made to get log level of services
        self.service_mock.get_log_levels.assert_called_with(
            server=self.service_log.host,
            binary=self.service_log.binary,
            prefix=self.service_log.prefix,
        )

    def test_block_storage_log_level_list_pre_332(self):
        arglist = [
            '--host',
            self.service_log.host,
            '--service',
            'cinder-api',
            '--log-prefix',
            'cinder_test.api.common',
        ]
        verifylist = [
            ('host', self.service_log.host),
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
            self.service_log.host,
            '--service',
            'nova-api',
            '--log-prefix',
            'cinder_test.api.common',
        ]
        verifylist = [
            ('host', self.service_log.host),
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
class TestBlockStorageLogLevelSet(TestService):
    service_log = volume_fakes.create_service_log_level_entry()

    def setUp(self):
        super().setUp()

        # Get the command object to test
        self.cmd = service.BlockStorageLogLevelSet(self.app, None)

    def test_block_storage_log_level_set(self):
        self.set_volume_api_version('3.32')

        arglist = [
            'ERROR',
            '--host',
            self.service_log.host,
            '--service',
            self.service_log.binary,
            '--log-prefix',
            self.service_log.prefix,
        ]
        verifylist = [
            ('level', 'ERROR'),
            ('host', self.service_log.host),
            ('service', self.service_log.binary),
            ('log_prefix', self.service_log.prefix),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        # checking if proper call was made to set log level of services
        self.service_mock.set_log_levels.assert_called_with(
            level='ERROR',
            server=self.service_log.host,
            binary=self.service_log.binary,
            prefix=self.service_log.prefix,
        )

    def test_block_storage_log_level_set_pre_332(self):
        arglist = [
            'ERROR',
            '--host',
            self.service_log.host,
            '--service',
            'cinder-api',
            '--log-prefix',
            'cinder_test.api.common',
        ]
        verifylist = [
            ('level', 'ERROR'),
            ('host', self.service_log.host),
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

    def test_block_storage_log_level_set_invalid_service_name(self):
        self.set_volume_api_version('3.32')

        arglist = [
            'ERROR',
            '--host',
            self.service_log.host,
            '--service',
            'nova-api',
            '--log-prefix',
            'cinder.api.common',
        ]
        verifylist = [
            ('level', 'ERROR'),
            ('host', self.service_log.host),
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
            self.service_log.host,
            '--service',
            'cinder-api',
            '--log-prefix',
            'cinder.api.common',
        ]
        verifylist = [
            ('level', log_level.upper()),
            ('host', self.service_log.host),
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

            # checking if proper call was made to set log level of services
            self.service_mock.set_log_levels.assert_called_with(
                level=log_level.upper(),
                server=self.service_log.host,
                binary=self.service_log.binary,
                prefix=self.service_log.prefix,
            )
