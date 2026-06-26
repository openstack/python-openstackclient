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
from manilaclient import api_versions
from manilaclient.osc import utils
from osc_lib import exceptions
from osc_lib import utils as oscutils

from openstackclient.share.v2 import services as services
from openstackclient.tests.unit.share.v2 import fakes as share_fakes


class TestShareService(share_fakes.TestShare):
    def setUp(self):
        super().setUp()

        self.services_mock = self.share_client.services
        self.services_mock.reset_mock()


class TestShareServiceSet(TestShareService):
    def setUp(self):
        super().setUp()

        self.share_service = share_fakes.FakeShareService.create_fake_service()
        self.cmd = services.SetShareService(self.app, None)

    def test_share_service_set_enable(self):
        arglist = [
            self.share_service.host,
            self.share_service.binary,
            '--enable',
        ]
        verifylist = [
            ('host', self.share_service.host),
            ('binary', self.share_service.binary),
            ('enable', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.services_mock.enable.assert_called_with(
            self.share_service.host, self.share_service.binary
        )
        self.assertIsNone(result)

    def test_share_service_set_enable_exception(self):
        arglist = [
            self.share_service.host,
            self.share_service.binary,
            '--enable',
        ]
        verifylist = [
            ('host', self.share_service.host),
            ('binary', self.share_service.binary),
            ('enable', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.services_mock.enable.side_effect = Exception()
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

    def test_share_service_set_disable(self):
        arglist = [
            self.share_service.host,
            self.share_service.binary,
            '--disable',
        ]
        verifylist = [
            ('host', self.share_service.host),
            ('binary', self.share_service.binary),
            ('disable', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.services_mock.disable.assert_called_with(
            self.share_service.host, self.share_service.binary
        )
        self.assertIsNone(result)

    def test_service_set_disable_with_reason(self):
        self.set_share_api_version('2.83')
        reason = 'earthquake'
        arglist = [
            '--disable',
            '--disable-reason',
            reason,
            self.share_service.host,
            self.share_service.binary,
        ]
        verifylist = [
            ('host', self.share_service.host),
            ('binary', self.share_service.binary),
            ('disable', True),
            ('disable_reason', reason),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.services_mock.disable.assert_called_with(
            self.share_service.host,
            self.share_service.binary,
            disable_reason=reason,
        )
        self.assertIsNone(result)

    def test_share_service_set_disable_exception(self):
        arglist = [
            self.share_service.host,
            self.share_service.binary,
            '--disable',
        ]
        verifylist = [
            ('host', self.share_service.host),
            ('binary', self.share_service.binary),
            ('disable', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.services_mock.disable.side_effect = Exception()
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )


@ddt.ddt
class TestShareServiceList(TestShareService):
    columns = ['id', 'binary', 'host', 'zone', 'status', 'state', 'updated_at']
    columns_with_reason = [*columns, 'disabled_reason']

    column_headers = utils.format_column_headers(columns)
    column_headers_with_reason = utils.format_column_headers(
        columns_with_reason
    )

    def setUp(self):
        super().setUp()

        self.services_list = share_fakes.FakeShareService.create_fake_services(
            {'disabled_reason': ''}
        )
        self.services_mock.list.return_value = self.services_list
        self.values = (
            oscutils.get_dict_properties(i._info, self.columns)
            for i in self.services_list
        )
        self.values_with_reason = (
            oscutils.get_dict_properties(i._info, self.columns_with_reason)
            for i in self.services_list
        )

        self.cmd = services.ListShareService(self.app, None)

    @ddt.data('2.82', '2.83')
    def test_share_service_list(self, version):
        self.set_share_api_version(version)
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.services_mock.list.assert_called_with(
            search_opts={
                'host': None,
                'binary': None,
                'status': None,
                'state': None,
                'zone': None,
            }
        )
        if api_versions.APIVersion(version) >= api_versions.APIVersion("2.83"):
            self.assertEqual(self.column_headers_with_reason, columns)
            self.assertEqual(list(self.values_with_reason), list(data))
        else:
            self.assertEqual(self.column_headers, columns)
            self.assertEqual(list(self.values), list(data))

    @ddt.data('2.82', '2.83')
    def test_share_service_list_host_status(self, version):
        self.set_share_api_version(version)
        arglist = [
            '--host',
            self.services_list[0].host,
            '--status',
            self.services_list[1].status,
        ]
        verifylist = [
            ('host', self.services_list[0].host),
            ('status', self.services_list[1].status),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.services_mock.list.assert_called_with(
            search_opts={
                'host': self.services_list[0].host,
                'binary': None,
                'status': self.services_list[1].status,
                'state': None,
                'zone': None,
            }
        )
        if api_versions.APIVersion(version) >= api_versions.APIVersion("2.83"):
            self.assertEqual(self.column_headers_with_reason, columns)
            self.assertEqual(list(self.values_with_reason), list(data))
        else:
            self.assertEqual(self.column_headers, columns)
            self.assertEqual(list(self.values), list(data))

    @ddt.data('2.82', '2.83')
    def test_share_service_list_binary_state_zone(self, version):
        self.set_share_api_version(version)
        arglist = [
            '--binary',
            self.services_list[0].binary,
            '--state',
            self.services_list[1].state,
            '--zone',
            self.services_list[1].zone,
        ]
        verifylist = [
            ('binary', self.services_list[0].binary),
            ('state', self.services_list[1].state),
            ('zone', self.services_list[1].zone),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.services_mock.list.assert_called_with(
            search_opts={
                'host': None,
                'binary': self.services_list[0].binary,
                'status': None,
                'state': self.services_list[1].state,
                'zone': self.services_list[1].zone,
            }
        )
        if api_versions.APIVersion(version) >= api_versions.APIVersion("2.83"):
            self.assertEqual(self.column_headers_with_reason, columns)
            self.assertEqual(list(self.values_with_reason), list(data))
        else:
            self.assertEqual(self.column_headers, columns)
            self.assertEqual(list(self.values), list(data))


@ddt.ddt
class TestShareServiceEnsureShares(TestShareService):
    def setUp(self):
        super().setUp()

        self.cmd = services.EnsureShareService(self.app, None)

    def test_ensure_shares(self):
        self.set_share_api_version('2.86')
        fake_host = 'fake_host@fakebackend'
        arglist = [
            fake_host,
        ]
        verifylist = [
            ('host', fake_host),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.services_mock.ensure_shares.assert_called_with(fake_host)

    def test_ensure_shares_invalid_version(self):
        self.set_share_api_version('2.85')
        fake_host = 'fake_host@fakebackend'
        arglist = [
            fake_host,
        ]
        verifylist = [
            ('host', fake_host),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

    def test_ensure_shares_command_error(self):
        self.set_share_api_version('2.86')
        self.services_mock.ensure_shares.side_effect = Exception()
        fake_host = 'fake_host@fakebackend'
        arglist = [
            fake_host,
        ]
        verifylist = [
            ('host', fake_host),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
