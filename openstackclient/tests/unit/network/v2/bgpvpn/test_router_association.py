# Copyright (c) 2018 Orange SA.
# All Rights Reserved.
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

import operator
from unittest import mock

from osc_lib import utils as osc_utils
from osc_lib.utils import columns as column_util

from openstackclient.network.v2.bgpvpn import router_association
from openstackclient.tests.unit.network.v2.bgpvpn import fakes
from openstackclient.tests.unit import utils


columns_short = tuple(
    col
    for col, _, listing_mode in router_association._attr_map
    if listing_mode in (column_util.LIST_BOTH, column_util.LIST_SHORT_ONLY)
)
columns_long = tuple(
    col
    for col, _, listing_mode in router_association._attr_map
    if listing_mode in (column_util.LIST_BOTH, column_util.LIST_LONG_ONLY)
)
headers_short = tuple(
    head
    for _, head, listing_mode in router_association._attr_map
    if listing_mode in (column_util.LIST_BOTH, column_util.LIST_SHORT_ONLY)
)
headers_long = tuple(
    head
    for _, head, listing_mode in router_association._attr_map
    if listing_mode in (column_util.LIST_BOTH, column_util.LIST_LONG_ONLY)
)
sorted_attr_map = sorted(
    router_association._attr_map, key=operator.itemgetter(1)
)
sorted_columns = tuple(col for col, _, _ in sorted_attr_map)
sorted_headers = tuple(head for _, head, _ in sorted_attr_map)


def _get_data(attrs, columns=sorted_columns):
    return osc_utils.get_dict_properties(
        attrs, columns, formatters=router_association._formatters
    )


class TestCreateRouterAssoc(fakes.TestNeutronClientBgpvpn):
    def setUp(self):
        super().setUp()
        self.cmd = router_association.CreateBgpvpnRouterAssoc(self.app, None)
        self.fake_bgpvpn = fakes.create_one_bgpvpn()
        self.fake_router = fakes.create_one_resource()
        self.network_client.find_bgpvpn.side_effect = (
            lambda name_or_id, **kwargs: {'id': name_or_id}
        )
        self.network_client.find_router.side_effect = (
            lambda name_or_id, **kwargs: {'id': name_or_id}
        )
        self.fake_project = mock.Mock(id='fake_project_id')
        self.identity_sdk_client.find_project = mock.Mock(
            return_value=self.fake_project
        )

    def _build_args(self, param=None):
        arglist_base = [
            self.fake_bgpvpn['id'],
            self.fake_router['id'],
            '--project',
            self.fake_bgpvpn['project_id'],
        ]
        if param is not None:
            if isinstance(param, list):
                arglist_base.extend(param)
            else:
                arglist_base.append(param)
        return arglist_base

    def _build_verify_list(self, param=None):
        verifylist = [
            ('bgpvpn', self.fake_bgpvpn['id']),
            ('resource', self.fake_router['id']),
            ('project', self.fake_bgpvpn['project_id']),
        ]
        if param is not None:
            verifylist.append(param)
        return verifylist

    def _exec_create_router_association(
        self,
        fake_assoc,
        arglist,
        verifylist,
    ):
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        cols, data = self.cmd.take_action(parsed_args)

        fake_assoc_call = {
            'router_id': self.fake_router['id'],
            'project_id': 'fake_project_id',
        }
        if verifylist:
            for key, value in verifylist:
                if (
                    key
                    not in (
                        'bgpvpn',
                        'resource',
                        'project',
                    )
                    and value not in fake_assoc_call.values()
                ):
                    fake_assoc_call[key] = value
        self.network_client.create_bgpvpn_router_association.assert_called_once_with(
            self.fake_bgpvpn['id'], **fake_assoc_call
        )
        return cols, data

    def test_create_router_association(self):
        fake_assoc = fakes.create_one_router_association()

        self.network_client.create_bgpvpn_router_association.return_value = (
            fake_assoc
        )

        arglist = self._build_args()
        # advertise_extra_routes will be False since none
        # of the mutually exclusive args present
        verifylist = self._build_verify_list(('advertise_extra_routes', False))

        self._exec_create_router_association(fake_assoc, arglist, verifylist)

    def test_create_router_association_advertise(self):
        fake_assoc = fakes.create_one_router_association(
            {'advertise_extra_routes': True}
        )

        self.network_client.create_bgpvpn_router_association.return_value = (
            fake_assoc
        )

        arglist = self._build_args('--advertise_extra_routes')
        verifylist = self._build_verify_list(('advertise_extra_routes', True))

        cols, data = self._exec_create_router_association(
            fake_assoc, arglist, verifylist
        )
        self.assertEqual(sorted(sorted_columns), sorted(cols))
        self.assertEqual(_get_data(fake_assoc, cols), data)

    def test_create_router_association_no_advertise(self):
        fake_assoc = fakes.create_one_router_association(
            {'advertise_extra_routes': False}
        )

        self.network_client.create_bgpvpn_router_association.return_value = (
            fake_assoc
        )

        arglist = self._build_args('--no-advertise_extra_routes')
        verifylist = self._build_verify_list(('advertise_extra_routes', False))

        cols, data = self._exec_create_router_association(
            fake_assoc, arglist, verifylist
        )
        self.assertEqual(sorted(sorted_columns), sorted(cols))
        self.assertEqual(_get_data(fake_assoc, cols), data)

    def test_create_router_association_advertise_fault(self):
        arglist = self._build_args(
            ['--advertise_extra_routes', '--no-advertise_extra_routes']
        )

        try:
            self._exec_create_router_association(None, arglist, None)
        except utils.ParserException as e:
            self.assertIn('Argument parse failed', format(e))

    def test_router_association_unknown_arg(self):
        arglist = self._build_args('--unknown arg')

        try:
            self._exec_create_router_association(None, arglist, None)
        except utils.ParserException as e:
            self.assertIn('Argument parse failed', format(e))


class TestSetRouterAssoc(fakes.TestNeutronClientBgpvpn):
    def setUp(self):
        super().setUp()
        self.cmd = router_association.SetBgpvpnRouterAssoc(self.app, None)
        self.fake_bgpvpn = fakes.create_one_bgpvpn()
        self.fake_router = fakes.create_one_resource()
        self.network_client.find_bgpvpn.side_effect = (
            lambda name_or_id, **kwargs: {'id': name_or_id}
        )

    def _build_args(self, fake_assoc, param=None):
        arglist_base = [fake_assoc['id'], self.fake_bgpvpn['id']]
        if param is not None:
            if isinstance(param, list):
                arglist_base.extend(param)
            else:
                arglist_base.append(param)
        return arglist_base

    def test_set_router_association_no_advertise(self):
        fake_assoc = fakes.create_one_router_association(
            {'advertise_extra_routes': True}
        )

        arglist = self._build_args(fake_assoc, '--no-advertise_extra_routes')
        verifylist = [
            ('resource_association_id', fake_assoc['id']),
            ('bgpvpn', self.fake_bgpvpn['id']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.network_client.update_bgpvpn_router_association.assert_called_once_with(
            self.fake_bgpvpn['id'],
            fake_assoc['id'],
            **{'advertise_extra_routes': False},
        )
        self.assertIsNone(result)

    def test_set_router_association_advertise(self):
        fake_assoc = fakes.create_one_router_association(
            {'advertise_extra_routes': False}
        )

        arglist = self._build_args(fake_assoc, '--advertise_extra_routes')
        verifylist = [
            ('resource_association_id', fake_assoc['id']),
            ('bgpvpn', self.fake_bgpvpn['id']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.network_client.update_bgpvpn_router_association.assert_called_once_with(
            self.fake_bgpvpn['id'],
            fake_assoc['id'],
            **{'advertise_extra_routes': True},
        )
        self.assertIsNone(result)


class TestShowRouterAssoc(fakes.TestNeutronClientBgpvpn):
    def setUp(self):
        super().setUp()
        self.cmd = router_association.ShowBgpvpnRouterAssoc(self.app, None)
        self.network_client.find_bgpvpn.side_effect = (
            lambda name_or_id, **kwargs: {'id': name_or_id}
        )

    def test_show_router_association(self):
        fake_bgpvpn = fakes.create_one_bgpvpn()
        fake_assoc = fakes.create_one_router_association(
            {'advertise_extra_routes': True}
        )
        self.network_client.get_bgpvpn_router_association.return_value = (
            fake_assoc
        )
        arglist = [
            fake_assoc['id'],
            fake_bgpvpn['id'],
        ]
        verifylist = [
            ('resource_association_id', fake_assoc['id']),
            ('bgpvpn', fake_bgpvpn['id']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        cols, data = self.cmd.take_action(parsed_args)

        self.network_client.get_bgpvpn_router_association.assert_called_once_with(
            fake_bgpvpn['id'], fake_assoc['id']
        )
        self.assertEqual(sorted(sorted_columns), sorted(cols))
        self.assertEqual(data, _get_data(fake_assoc, cols))
