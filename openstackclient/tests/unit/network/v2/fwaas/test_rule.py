# Copyright 2016 FUJITSU LIMITED
# All Rights Reserved
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#

import re
from unittest import mock

from cliff import columns as cliff_columns
from openstack.network.v2 import firewall_rule
from openstack.test import fakes as sdk_fakes
from osc_lib import exceptions
import testtools

from openstackclient.network.v2.fwaas import rule as fwaas_rule
from openstackclient.tests.unit.network.v2 import fakes as network_fakes
from openstackclient.tests.unit import utils as test_utils


CONVERT_MAP = {
    'project': 'project_id',
}


def _generate_data(source=None, data=None):
    if data:
        source.update(data)
    ret = tuple(_replace_display_columns(key, source[key]) for key in source)
    return ret


def _replace_display_columns(key, val):
    if key == 'protocol':
        return fwaas_rule.ProtocolColumn(val)
    return val


def _generate_req_and_res(verifylist, response):
    request = dict(verifylist)
    for key, val in verifylist:
        converted = CONVERT_MAP.get(key, key)
        del request[key]
        if re.match('^no_', key) and val is True:
            new_value = None
        elif key == 'protocol' and val and val.lower() == 'any':
            new_value = None
        elif val is True or val is False:
            new_value = val
        elif key in ('name', 'description'):
            new_value = val
        else:
            new_value = val
        request[converted] = new_value
        response[converted] = new_value
    return request, response


class TestFirewallRule(network_fakes.TestNetworkV2):
    def check_results(self, headers, data, exp_req=None, is_list=False):
        if is_list:
            req_body = {self.res_plural: [exp_req]}
        else:
            req_body = exp_req
        if not exp_req:
            self.mocked.assert_called_once_with()
        else:
            self.mocked.assert_called_once_with(**req_body)
        self.assertEqual(self.ordered_headers, headers)

    # TODO(slaweq): remove this method once network_fakes.TestNetworkV2 will
    # inherit from the osc_lib.test.base.TestCommand
    def assertListItemEqual(self, expected, actual):
        self.assertEqual(len(expected), len(actual))
        for item_expected, item_actual in zip(expected, actual):
            self.assertItemEqual(item_expected, item_actual)

    # TODO(slaweq): remove this method once network_fakes.TestNetworkV2 will
    # inherit from the osc_lib.test.base.TestCommand
    def assertItemEqual(self, expected, actual):
        self.assertEqual(len(expected), len(actual))
        for col_expected, col_actual in zip(expected, actual):
            if isinstance(col_expected, cliff_columns.FormattableColumn):
                self.assertIsInstance(col_actual, col_expected.__class__)
                self.assertEqual(
                    col_expected.human_readable(), col_actual.human_readable()
                )
            else:
                self.assertEqual(col_expected, col_actual)

    def setUp(self):
        super().setUp()

        self.identity_client.projects.get.side_effect = lambda x: mock.Mock(
            id=x
        )
        self.res = 'firewall_rule'
        self.res_plural = 'firewall_rules'
        self.resource = sdk_fakes.generate_fake_resource(
            firewall_rule.FirewallRule
        )
        self.headers = (
            'ID',
            'Name',
            'Enabled',
            'Description',
            'Firewall Policy',
            'IP Version',
            'Action',
            'Protocol',
            'Source IP Address',
            'Source Port',
            'Destination IP Address',
            'Destination Port',
            'Shared',
            'Project',
            'Source Firewall Group ID',
            'Destination Firewall Group ID',
        )
        self.data = _generate_data(self.resource)
        self.ordered_headers = (
            'Action',
            'Description',
            'Destination Firewall Group ID',
            'Destination IP Address',
            'Destination Port',
            'Enabled',
            'Firewall Policy',
            'ID',
            'IP Version',
            'Name',
            'Project',
            'Protocol',
            'Shared',
            'Source Firewall Group ID',
            'Source IP Address',
            'Source Port',
            'Summary',
        )
        self.ordered_data = (
            self.resource['action'],
            self.resource['description'],
            self.resource['destination_ip_address'],
            self.resource['destination_port'],
            self.resource['firewall_policy_id'],
            self.resource['enabled'],
            self.resource['id'],
            self.resource['ip_version'],
            self.resource['name'],
            self.resource['project_id'],
            _replace_display_columns('protocol', self.resource['protocol']),
            self.resource['shared'],
            self.resource['source_ip_address'],
            self.resource['source_port'],
        )
        self.ordered_columns = (
            'action',
            'description',
            'destination_ip_address',
            'destination_port',
            'enabled',
            'id',
            'ip_version',
            'name',
            'project_id',
            'protocol',
            'shared',
            'source_ip_address',
            'source_port',
        )


class TestCreateFirewallRule(TestFirewallRule):
    def setUp(self):
        super().setUp()
        self.network_client.create_firewall_rule.return_value = self.resource
        self.mocked = self.network_client.create_firewall_rule

        def _mock_find_group(*args, **kwargs):
            return self.resource

        self.network_client.find_firewall_group.side_effect = _mock_find_group

        self.cmd = fwaas_rule.CreateFirewallRule(self.app, None)

    def _update_expect_response(self, request, response):
        """Set expected request and response

        :param request
            A dictionary of request body(dict of verifylist)
        :param response
            A OrderedDict of request body
        """
        # Update response body
        self.network_client.create_firewall_rule.return_value = response
        # Update response(finally returns 'data')
        self.data = _generate_data(source=response)
        self.ordered_data = tuple(
            _replace_display_columns(column, response[column])
            for column in self.ordered_columns
        )

    def _set_all_params(self, args={}):
        name = args.get('name') or 'my-name'
        description = args.get('description') or 'my-desc'
        source_ip = args.get('source_ip_address') or '192.168.1.0/24'
        destination_ip = args.get('destination_ip_address') or '192.168.2.0/24'
        source_port = args.get('source_port') or '0:65535'
        protocol = args.get('protocol') or 'udp'
        action = args.get('action') or 'deny'
        ip_version = args.get('ip_version') or '4'
        destination_port = args.get('destination_port') or '0:65535'
        project_id = args.get('project_id') or 'my-tenant'
        arglist = [
            '--description',
            description,
            '--name',
            name,
            '--protocol',
            protocol,
            '--ip-version',
            ip_version,
            '--source-ip-address',
            source_ip,
            '--destination-ip-address',
            destination_ip,
            '--source-port',
            source_port,
            '--destination-port',
            destination_port,
            '--action',
            action,
            '--project',
            project_id,
            '--disable-rule',
            '--share',
        ]

        verifylist = [
            ('name', name),
            ('description', description),
            ('shared', True),
            ('protocol', protocol),
            ('ip_version', ip_version),
            ('source_ip_address', source_ip),
            ('destination_ip_address', destination_ip),
            ('source_port', source_port),
            ('destination_port', destination_port),
            ('action', action),
            ('enabled', False),
            ('project', project_id),
        ]
        return arglist, verifylist

    def _test_create_with_all_params(self, args={}):
        arglist, verifylist = self._set_all_params(args)
        request, response = _generate_req_and_res(verifylist, self.resource)
        self._update_expect_response(request, response)
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)

        self.check_results(headers, data, request)

    def test_create_with_no_options(self):
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)
        self.check_results(headers, data, None)

    def test_create_with_all_params(self):
        self._test_create_with_all_params()

    def test_create_with_all_params_protocol_any(self):
        self._test_create_with_all_params({'protocol': 'any'})

    def test_create_with_all_params_ip_version_6(self):
        self._test_create_with_all_params({'ip_version': '6'})

    def test_create_with_all_params_invalid_ip_version(self):
        arglist, verifylist = self._set_all_params({'ip_version': '128'})
        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_create_with_all_params_action_upper_capitalized(self):
        for action in ('Allow', 'DENY', 'Reject'):
            arglist, verifylist = self._set_all_params({'action': action})
            self.assertRaises(
                testtools.matchers._impl.MismatchError,
                self.check_parser,
                self.cmd,
                arglist,
                verifylist,
            )

    def test_create_with_all_params_protocol_upper_capitalized(self):
        for protocol in ('TCP', 'Tcp', 'ANY', 'AnY', 'iCMp'):
            arglist, verifylist = self._set_all_params({'protocol': protocol})
            self.assertRaises(
                testtools.matchers._impl.MismatchError,
                self.check_parser,
                self.cmd,
                arglist,
                verifylist,
            )


class TestListFirewallRule(TestFirewallRule):
    def _setup_summary(self, expect=None):
        protocol = (self.resource['protocol'] or 'any').upper()
        src = 'source(port): 192.168.1.0/24(1:11111)'
        dst = 'dest(port): 192.168.2.2(2:22222)'
        action = 'deny'
        if expect:
            if expect.get('protocol'):
                protocol = expect['protocol'].upper()
            if expect.get('source_ip_address'):
                src_ip = expect['source_ip_address']
            if expect.get('source_port'):
                src_port = expect['source_port']
            if expect.get('destination_ip_address'):
                dst_ip = expect['destination_ip_address']
            if expect.get('destination_port'):
                dst_port = expect['destination_port']
            if expect.get('action'):
                action = expect['action']
            src = 'source(port): ' + src_ip + '(' + src_port + ')'
            dst = 'dest(port): ' + dst_ip + '(' + dst_port + ')'
        return ',\n '.join([protocol, src, dst, action])

    def setUp(self):
        super().setUp()
        self.cmd = fwaas_rule.ListFirewallRule(self.app, None)

        self.short_header = (
            'ID',
            'Name',
            'Enabled',
            'Summary',
            'Firewall Policy',
        )

        summary = self._setup_summary(self.resource)

        self.short_data = (
            self.resource['id'],
            self.resource['name'],
            self.resource['enabled'],
            summary,
            self.resource['firewall_policy_id'],
        )
        self.network_client.firewall_rules.return_value = [self.resource]
        self.mocked = self.network_client.firewall_rules

    def test_list_with_long_option(self):
        arglist = ['--long']
        verifylist = [('long', True)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, _data = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with()
        self.assertEqual(list(self.headers), headers)

    def test_list_with_no_option(self):
        arglist = []
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, data = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with()
        self.assertEqual(list(self.short_header), headers)
        self.assertListItemEqual([self.short_data], list(data))


class TestShowFirewallRule(TestFirewallRule):
    def setUp(self):
        super().setUp()
        self.network_client.get_firewall_rule.return_value = self.resource
        self.mocked = self.network_client.get_firewall_rule
        self.cmd = fwaas_rule.ShowFirewallRule(self.app, None)

    def test_show_filtered_by_id_or_name(self):
        target = self.resource['id']

        def _mock_fwaas(*args, **kwargs):
            return sdk_fakes.generate_fake_resource(
                firewall_rule.FirewallRule, id=args[0]
            )

        self.network_client.find_firewall_rule.side_effect = _mock_fwaas

        arglist = [target]
        verifylist = [(self.res, target)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        headers, _data = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(target)
        self.assertEqual(self.ordered_headers, headers)


class TestSetFirewallRule(TestFirewallRule):
    def setUp(self):
        super().setUp()
        self.network_client.update_firewall_rule.return_value = self.resource
        self.mocked = self.network_client.update_firewall_rule

        def _mock_find_rule(*args, **kwargs):
            return sdk_fakes.generate_fake_resource(
                firewall_rule.FirewallRule, id=args[0]
            )

        self.network_client.find_firewall_rule.side_effect = _mock_find_rule

        self.cmd = fwaas_rule.SetFirewallRule(self.app, None)

    def test_set_name(self):
        target = self.resource['id']
        update = 'change'
        arglist = [target, '--name', update]
        verifylist = [
            (self.res, target),
            ('name', update),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(target, **{'name': update})
        self.assertIsNone(result)

    def test_set_options(self):
        target = self.resource['id']
        updated_desc = 'change-desc'
        arglist = [target, '--description', updated_desc, '--share']
        verifylist = [
            (self.res, target),
            ('description', updated_desc),
            ('shared', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(
            target, shared=True, description=updated_desc
        )
        self.assertIsNone(result)

    def test_set_protocol_with_any(self):
        target = self.resource['id']
        protocol = 'any'
        arglist = [target, '--protocol', protocol]
        verifylist = [
            (self.res, target),
            ('protocol', protocol),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(target, **{'protocol': None})
        self.assertIsNone(result)

    def test_set_protocol_with_udp(self):
        target = self.resource['id']
        protocol = 'udp'
        arglist = [target, '--protocol', protocol]
        verifylist = [
            (self.res, target),
            ('protocol', protocol),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(target, **{'protocol': protocol})
        self.assertIsNone(result)

    def test_set_source_ip_address(self):
        target = self.resource['id']
        src_ip = '192.192.192.192'
        arglist = [target, '--source-ip-address', src_ip]
        verifylist = [
            (self.res, target),
            ('source_ip_address', src_ip),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(
            target, **{'source_ip_address': src_ip}
        )
        self.assertIsNone(result)

    def test_set_source_port(self):
        target = self.resource['id']
        src_port = '32678'
        arglist = [target, '--source-port', src_port]
        verifylist = [
            (self.res, target),
            ('source_port', src_port),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(
            target, **{'source_port': src_port}
        )
        self.assertIsNone(result)

    def test_set_destination_ip_address(self):
        target = self.resource['id']
        dst_ip = '0.1.0.1'
        arglist = [target, '--destination-ip-address', dst_ip]
        verifylist = [
            (self.res, target),
            ('destination_ip_address', dst_ip),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(
            target, **{'destination_ip_address': dst_ip}
        )
        self.assertIsNone(result)

    def test_set_destination_port(self):
        target = self.resource['id']
        dst_port = '65432'
        arglist = [target, '--destination-port', dst_port]
        verifylist = [
            (self.res, target),
            ('destination_port', dst_port),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(
            target, **{'destination_port': dst_port}
        )
        self.assertIsNone(result)

    def test_set_enable_rule(self):
        target = self.resource['id']
        arglist = [target, '--enable-rule']
        verifylist = [
            (self.res, target),
            ('enabled', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(target, **{'enabled': True})
        self.assertIsNone(result)

    def test_set_disable_rule(self):
        target = self.resource['id']
        arglist = [target, '--disable-rule']
        verifylist = [
            (self.res, target),
            ('enabled', False),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(target, **{'enabled': False})
        self.assertIsNone(result)

    def test_set_action(self):
        target = self.resource['id']
        action = 'reject'
        arglist = [target, '--action', action]
        verifylist = [
            (self.res, target),
            ('action', action),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(target, **{'action': action})
        self.assertIsNone(result)

    def test_set_enable_rule_and_disable_rule(self):
        target = self.resource['id']
        arglist = [target, '--enable-rule', '--disable-rule']
        verifylist = [
            (self.res, target),
            ('enabled', True),
        ]
        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_set_no_source_ip_address(self):
        target = self.resource['id']
        arglist = [
            target,
            '--no-source-ip-address',
        ]
        verifylist = [
            (self.res, target),
            ('no_source_ip_address', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(
            target, **{'source_ip_address': None}
        )
        self.assertIsNone(result)

    def test_set_no_source_port(self):
        target = self.resource['id']
        arglist = [
            target,
            '--no-source-port',
        ]
        verifylist = [
            (self.res, target),
            ('no_source_port', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(target, **{'source_port': None})
        self.assertIsNone(result)

    def test_set_no_destination_ip_address(self):
        target = self.resource['id']
        arglist = [
            target,
            '--no-destination-ip-address',
        ]
        verifylist = [
            (self.res, target),
            ('no_destination_ip_address', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(
            target, **{'destination_ip_address': None}
        )
        self.assertIsNone(result)

    def test_set_no_destination_port(self):
        target = self.resource['id']
        arglist = [
            target,
            '--no-destination-port',
        ]
        verifylist = [
            (self.res, target),
            ('no_destination_port', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(
            target, **{'destination_port': None}
        )
        self.assertIsNone(result)

    def test_set_source_ip_address_and_no(self):
        target = self.resource['id']
        arglist = [
            target,
            '--source-ip-address',
            '192.168.1.0/24',
            '--no-source-ip-address',
        ]
        verifylist = [
            (self.res, target),
            ('source_ip_address', '192.168.1.0/24'),
            ('no_source_ip_address', True),
        ]
        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_set_destination_ip_address_and_no(self):
        target = self.resource['id']
        arglist = [
            target,
            '--destination-ip-address',
            '192.168.2.0/24',
            '--no-destination-ip-address',
        ]
        verifylist = [
            (self.res, target),
            ('destination_ip_address', '192.168.2.0/24'),
            ('no_destination_ip_address', True),
        ]
        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_set_source_port_and_no(self):
        target = self.resource['id']
        arglist = [
            target,
            '--source-port',
            '1:12345',
            '--no-source-port',
        ]
        verifylist = [
            (self.res, target),
            ('source_port', '1:12345'),
            ('no_source_port', True),
        ]
        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_set_destination_port_and_no(self):
        target = self.resource['id']
        arglist = [
            target,
            '--destination-port',
            '1:54321',
            '--no-destination-port',
        ]
        verifylist = [
            (self.res, target),
            ('destination_port', '1:54321'),
            ('no_destination_port', True),
        ]
        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_set_and_raises(self):
        self.network_client.update_firewall_rule.side_effect = Exception
        target = self.resource['id']
        arglist = [target, '--name', 'my-name']
        verifylist = [(self.res, target), ('name', 'my-name')]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )


class TestUnsetFirewallRule(TestFirewallRule):
    def setUp(self):
        super().setUp()
        self.mocked = self.network_client.update_firewall_rule

        def _mock_find_rule(*args, **kwargs):
            return sdk_fakes.generate_fake_resource(
                firewall_rule.FirewallRule, id=args[0]
            )

        self.network_client.find_firewall_rule.side_effect = _mock_find_rule

        self.cmd = fwaas_rule.UnsetFirewallRule(self.app, None)

    def test_unset_shared(self):
        target = self.resource['id']
        arglist = [
            target,
            '--share',
        ]
        verifylist = [
            (self.res, target),
            ('share', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.mocked.assert_called_once_with(target, **{'shared': False})
        self.assertIsNone(result)

    def test_unset_protocol_and_raise(self):
        self.network_client.update_firewall_rule.side_effect = Exception
        target = self.resource['id']
        arglist = [
            target,
            '--protocol',
        ]
        verifylist = [(self.res, target), ('protocol', False)]
        self.assertRaises(
            test_utils.ParserException,
            self.check_parser,
            self.cmd,
            arglist,
            verifylist,
        )

    def test_unset_source_port(self):
        target = self.resource['id']
        arglist = [
            target,
            '--source-port',
        ]
        verifylist = [
            (self.res, target),
            ('source_port', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(target, **{'source_port': None})
        self.assertIsNone(result)

    def test_unset_destination_port(self):
        target = self.resource['id']
        arglist = [
            target,
            '--destination-port',
        ]
        verifylist = [
            (self.res, target),
            ('destination_port', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(
            target, **{'destination_port': None}
        )
        self.assertIsNone(result)

    def test_unset_source_ip_address(self):
        target = self.resource['id']
        arglist = [
            target,
            '--source-ip-address',
        ]
        verifylist = [
            (self.res, target),
            ('source_ip_address', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(
            target, **{'source_ip_address': None}
        )
        self.assertIsNone(result)

    def test_unset_destination_ip_address(self):
        target = self.resource['id']
        arglist = [
            target,
            '--destination-ip-address',
        ]
        verifylist = [
            (self.res, target),
            ('destination_ip_address', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(
            target, **{'destination_ip_address': None}
        )
        self.assertIsNone(result)

    def test_unset_enable_rule(self):
        target = self.resource['id']
        arglist = [
            target,
            '--enable-rule',
        ]
        verifylist = [
            (self.res, target),
            ('enable_rule', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(target, **{'enabled': False})
        self.assertIsNone(result)


class TestDeleteFirewallRule(TestFirewallRule):
    def setUp(self):
        super().setUp()
        self.mocked = self.network_client.delete_firewall_rule
        self.cmd = fwaas_rule.DeleteFirewallRule(self.app, None)

    def test_delete_with_one_resource(self):
        target = self.resource['id']

        def _mock_fwaas(*args, **kwargs):
            return sdk_fakes.generate_fake_resource(
                firewall_rule.FirewallRule, id=args[0]
            )

        self.network_client.find_firewall_rule.side_effect = _mock_fwaas

        arglist = [target]
        verifylist = [(self.res, [target])]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.mocked.assert_called_once_with(target)
        self.assertIsNone(result)

    def test_delete_with_multiple_resources(self):

        def _mock_fwaas(*args, **kwargs):
            return sdk_fakes.generate_fake_resource(
                firewall_rule.FirewallRule, id=args[0]
            )

        self.network_client.find_firewall_rule.side_effect = _mock_fwaas

        target1 = 'target1'
        target2 = 'target2'
        arglist = [target1, target2]
        verifylist = [(self.res, [target1, target2])]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)
        self.assertIsNone(result)

        self.assertEqual(2, self.mocked.call_count)
        for idx, reference in enumerate([target1, target2]):
            actual = ''.join(self.mocked.call_args_list[idx][0][0])
            self.assertEqual(reference, actual)

    def test_delete_multiple_with_exception(self):
        target1 = 'target1'
        target2 = 'target2'
        arglist = [target1, target2]
        verifylist = [(self.res, [target1, target2])]

        def _mock_find(*args, **kwargs):
            if args[0] == target2:
                raise Exception('Not found')
            return self.resource

        self.network_client.find_firewall_rule.side_effect = _mock_find

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
