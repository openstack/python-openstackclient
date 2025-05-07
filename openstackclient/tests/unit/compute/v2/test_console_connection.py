# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import uuid

from openstack.compute.v2 import console_auth_token as _console_auth_token
from openstack.test import fakes as sdk_fakes

from openstackclient.compute.v2 import console_connection
from openstackclient.tests.unit.compute.v2 import fakes as compute_fakes


class TestConsoleTokens(compute_fakes.TestComputev2):
    def setUp(self):
        super().setUp()

        self._console_auth_token = sdk_fakes.generate_fake_resource(
            _console_auth_token.ConsoleAuthToken,
            host='127.0.0.1',
            instance_uuid=uuid.uuid4().hex,
            internal_access_path=None,
            port=5900,
            tls_port=5901,
        )
        self.compute_client.validate_console_auth_token.return_value = (
            self._console_auth_token
        )

        self.columns = (
            'host',
            'instance_uuid',
            'internal_access_path',
            'port',
            'tls_port',
        )
        self.data = (
            self._console_auth_token.host,
            self._console_auth_token.instance_uuid,
            self._console_auth_token.internal_access_path,
            self._console_auth_token.port,
            self._console_auth_token.tls_port,
        )

        self.cmd = console_connection.ShowConsoleConnectionInformation(
            self.app, None
        )

    def test_console_connection_show(self):
        arglist = [
            'token',
        ]
        verifylist = [
            ('token', 'token'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.compute_client.validate_console_auth_token.assert_called_once_with(
            'token'
        )
        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)
