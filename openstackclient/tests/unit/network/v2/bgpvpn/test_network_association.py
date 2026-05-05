# Copyright 2026 Openinfra Foundation
#
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

from osc_lib import exceptions
from osc_lib import utils as osc_utils
from osc_lib.utils import columns as column_util

from openstackclient.network.v2.bgpvpn import network_association
from openstackclient.tests.unit.network.v2.bgpvpn import fakes


columns_short = tuple(
    col
    for col, _, listing_mode in network_association._attr_map
    if listing_mode in (column_util.LIST_BOTH, column_util.LIST_SHORT_ONLY)
)
columns_long = tuple(
    col
    for col, _, listing_mode in network_association._attr_map
    if listing_mode in (column_util.LIST_BOTH, column_util.LIST_LONG_ONLY)
)
headers_short = tuple(
    head
    for _, head, listing_mode in network_association._attr_map
    if listing_mode in (column_util.LIST_BOTH, column_util.LIST_SHORT_ONLY)
)
headers_long = tuple(
    head
    for _, head, listing_mode in network_association._attr_map
    if listing_mode in (column_util.LIST_BOTH, column_util.LIST_LONG_ONLY)
)
sorted_attr_map = sorted(
    network_association._attr_map, key=operator.itemgetter(1)
)
sorted_columns = tuple(col for col, _, _ in sorted_attr_map)
sorted_headers = tuple(head for _, head, _ in sorted_attr_map)


def _get_data(attrs, columns=sorted_columns):
    return osc_utils.get_dict_properties(
        attrs, columns, formatters=network_association._formatters
    )


class TestCreateNetAssoc(fakes.TestNeutronClientBgpvpn):
    def setUp(self):
        super().setUp()
        self.network_client.find_bgpvpn.side_effect = (
            lambda name_or_id, **kwargs: {'id': name_or_id}
        )
        self.network_client.find_network.side_effect = (
            lambda name_or_id, **kwargs: {'id': name_or_id}
        )
        self.cmd = network_association.CreateBgpvpnNetAssoc(self.app, None)

    @mock.patch('osc_lib.cli.identity.find_project')
    def test_create_network_association(self, mock_find_project):
        fake_bgpvpn = fakes.create_one_bgpvpn()
        fake_res = fakes.create_one_resource()
        fake_assoc = fakes.create_one_network_association()
        self.network_client.create_bgpvpn_network_association.return_value = (
            fake_assoc
        )
        mock_find_project.return_value = mock.Mock(id=fake_bgpvpn['tenant_id'])
        arglist = [
            fake_bgpvpn['id'],
            fake_res['id'],
            '--project',
            fake_bgpvpn['tenant_id'],
        ]
        verifylist = [
            ('bgpvpn', fake_bgpvpn['id']),
            ('resource', fake_res['id']),
            ('project', fake_bgpvpn['tenant_id']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        cols, data = self.cmd.take_action(parsed_args)

        self.network_client.create_bgpvpn_network_association.assert_called_once_with(
            fake_bgpvpn['id'],
            network_id=fake_res['id'],
            tenant_id='fake_project_id',
        )
        self.assertEqual(sorted_columns, cols)
        self.assertEqual(_get_data(fake_assoc), data)


class TestDeleteNetAssoc(fakes.TestNeutronClientBgpvpn):
    def setUp(self):
        super().setUp()
        self.network_client.find_bgpvpn.side_effect = (
            lambda name_or_id, **kwargs: {'id': name_or_id}
        )
        self.cmd = network_association.DeleteBgpvpnNetAssoc(self.app, None)

    def test_delete_one_association(self):
        fake_bgpvpn = fakes.create_one_bgpvpn()
        fake_assoc = fakes.create_one_network_association()
        arglist = [
            fake_assoc['id'],
            fake_bgpvpn['id'],
        ]
        verifylist = [
            ('resource_association_ids', [fake_assoc['id']]),
            ('bgpvpn', fake_bgpvpn['id']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.network_client.delete_bgpvpn_network_association.assert_called_once_with(
            fake_bgpvpn['id'], fake_assoc['id']
        )
        self.assertIsNone(result)

    def test_delete_multi_association(self):
        count = 3
        fake_bgpvpn = fakes.create_one_bgpvpn()
        fake_assocs = fakes.create_network_associations(count=count)
        fake_assoc_ids = [a['id'] for a in fake_assocs]
        arglist = [*fake_assoc_ids, fake_bgpvpn['id']]
        verifylist = [
            ('resource_association_ids', fake_assoc_ids),
            ('bgpvpn', fake_bgpvpn['id']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.network_client.delete_bgpvpn_network_association.assert_has_calls(
            [mock.call(fake_bgpvpn['id'], id) for id in fake_assoc_ids]
        )
        self.assertIsNone(result)

    def test_delete_multi_association_with_unknown(self):
        count = 3
        fake_bgpvpn = fakes.create_one_bgpvpn()
        fake_assocs = fakes.create_network_associations(count=count)
        fake_assoc_ids = [a['id'] for a in fake_assocs]

        def raise_unknown_resource(bgpvpn_id, association_id):
            if str(count - 2) in association_id:
                raise Exception()

        self.network_client.delete_bgpvpn_network_association.side_effect = (
            raise_unknown_resource
        )
        arglist = [*fake_assoc_ids, fake_bgpvpn['id']]
        verifylist = [
            ('resource_association_ids', fake_assoc_ids),
            ('bgpvpn', fake_bgpvpn['id']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

        self.network_client.delete_bgpvpn_network_association.assert_has_calls(
            [mock.call(fake_bgpvpn['id'], id) for id in fake_assoc_ids]
        )


class TestListNetAssoc(fakes.TestNeutronClientBgpvpn):
    def setUp(self):
        super().setUp()
        self.network_client.find_bgpvpn.side_effect = (
            lambda name_or_id, **kwargs: {'id': name_or_id}
        )
        self.cmd = network_association.ListBgpvpnNetAssoc(self.app, None)

    def test_list_network_associations(self):
        count = 3
        fake_bgpvpn = fakes.create_one_bgpvpn()
        fake_assocs = fakes.create_network_associations(count=count)
        self.network_client.bgpvpn_network_associations.return_value = (
            fake_assocs
        )
        arglist = [
            fake_bgpvpn['id'],
        ]
        verifylist = [
            ('bgpvpn', fake_bgpvpn['id']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        headers, data = self.cmd.take_action(parsed_args)

        self.network_client.bgpvpn_network_associations.assert_called_once_with(
            fake_bgpvpn['id'], retrieve_all=True
        )
        self.assertEqual(headers, list(headers_short))
        self.assertEqual(
            list(data),
            [_get_data(a, columns_short) for a in fake_assocs],
        )

    def test_list_network_associations_long_mode(self):
        count = 3
        fake_bgpvpn = fakes.create_one_bgpvpn()
        fake_assocs = fakes.create_network_associations(count=count)
        self.network_client.bgpvpn_network_associations.return_value = (
            fake_assocs
        )
        arglist = [
            '--long',
            fake_bgpvpn['id'],
        ]
        verifylist = [
            ('long', True),
            ('bgpvpn', fake_bgpvpn['id']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        headers, data = self.cmd.take_action(parsed_args)

        self.network_client.bgpvpn_network_associations.assert_called_once_with(
            fake_bgpvpn['id'], retrieve_all=True
        )
        self.assertEqual(headers, list(headers_long))
        self.assertEqual(
            list(data),
            [_get_data(a, columns_long) for a in fake_assocs],
        )


class TestShowNetAssoc(fakes.TestNeutronClientBgpvpn):
    def setUp(self):
        super().setUp()
        self.network_client.find_bgpvpn.side_effect = (
            lambda name_or_id, **kwargs: {'id': name_or_id}
        )
        self.cmd = network_association.ShowBgpvpnNetAssoc(self.app, None)

    def test_show_network_association(self):
        fake_bgpvpn = fakes.create_one_bgpvpn()
        fake_assoc = fakes.create_one_network_association()
        self.network_client.get_bgpvpn_network_association.return_value = (
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

        columns, data = self.cmd.take_action(parsed_args)

        self.network_client.get_bgpvpn_network_association.assert_called_once_with(
            fake_bgpvpn['id'], fake_assoc['id']
        )
        self.assertEqual(sorted_columns, columns)
        self.assertEqual(data, _get_data(fake_assoc))
