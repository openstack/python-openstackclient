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

from openstackclient.network.v2.bgpvpn import port_association
from openstackclient.tests.unit.network.v2.bgpvpn import fakes


columns_short = tuple(
    col
    for col, _, listing_mode in port_association._attr_map
    if listing_mode in (column_util.LIST_BOTH, column_util.LIST_SHORT_ONLY)
)
columns_long = tuple(
    col
    for col, _, listing_mode in port_association._attr_map
    if listing_mode in (column_util.LIST_BOTH, column_util.LIST_LONG_ONLY)
)
headers_short = tuple(
    head
    for _, head, listing_mode in port_association._attr_map
    if listing_mode in (column_util.LIST_BOTH, column_util.LIST_SHORT_ONLY)
)
headers_long = tuple(
    head
    for _, head, listing_mode in port_association._attr_map
    if listing_mode in (column_util.LIST_BOTH, column_util.LIST_LONG_ONLY)
)
sorted_attr_map = sorted(
    port_association._attr_map, key=operator.itemgetter(1)
)
sorted_columns = tuple(col for col, _, _ in sorted_attr_map)
sorted_headers = tuple(head for _, head, _ in sorted_attr_map)


def _get_data(attrs, columns=sorted_columns):
    return osc_utils.get_dict_properties(
        attrs, columns, formatters=port_association._formatters
    )


class TestCreatePortAssoc(fakes.TestNeutronClientBgpvpn):
    def setUp(self):
        super().setUp()
        self.cmd = port_association.CreateBgpvpnPortAssoc(self.app, None)
        self.fake_bgpvpn = fakes.create_one_bgpvpn()
        self.fake_port = fakes.create_one_resource()
        self.network_client.find_bgpvpn.side_effect = (
            lambda name_or_id, **kwargs: {'id': name_or_id}
        )
        self.network_client.find_port.side_effect = (
            lambda name_or_id, **kwargs: {'id': name_or_id}
        )
        self.fake_project = mock.Mock(id='fake_project_id')
        self.identity_sdk_client.find_project = mock.Mock(
            return_value=self.fake_project
        )

    @mock.patch('osc_lib.cli.identity.find_project')
    def test_create_port_association(self, mock_find_project):
        fake_assoc = fakes.create_one_port_association()
        self.network_client.create_bgpvpn_port_association.return_value = (
            fake_assoc
        )
        mock_find_project.return_value = mock.Mock(
            id=self.fake_bgpvpn['project_id']
        )
        arglist = [
            self.fake_bgpvpn['id'],
            self.fake_port['id'],
            '--project',
            self.fake_bgpvpn['project_id'],
        ]
        verifylist = [
            ('bgpvpn', self.fake_bgpvpn['id']),
            ('port', self.fake_port['id']),
            ('project', self.fake_bgpvpn['project_id']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        cols, _data = self.cmd.take_action(parsed_args)

        self.network_client.create_bgpvpn_port_association.assert_called_once_with(
            self.fake_bgpvpn['id'],
            port_id=self.fake_port['id'],
            project_id='fake_project_id',
            routes=[],
        )
        self.assertIn('id', cols)
        self.assertIn('port_id', cols)


class TestSetPortAssoc(fakes.TestNeutronClientBgpvpn):
    def setUp(self):
        super().setUp()
        self.cmd = port_association.SetBgpvpnPortAssoc(self.app, None)
        self.fake_bgpvpn = fakes.create_one_bgpvpn()
        self.network_client.find_bgpvpn.side_effect = (
            lambda name_or_id, **kwargs: {'id': name_or_id}
        )
        self.network_client.find_bgpvpn_port_association.return_value = {
            'routes': []
        }

    def test_set_port_association_advertise(self):
        fake_assoc = fakes.create_one_port_association()
        arglist = [
            fake_assoc['id'],
            self.fake_bgpvpn['id'],
            '--advertise-fixed-ips',
        ]
        verifylist = [
            ('port_association_id', fake_assoc['id']),
            ('bgpvpn', self.fake_bgpvpn['id']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.network_client.update_bgpvpn_port_association.assert_called_once_with(
            self.fake_bgpvpn['id'],
            fake_assoc['id'],
            advertise_fixed_ips=True,
            routes=[],
        )
        self.assertIsNone(result)

    def test_set_port_association_no_advertise(self):
        fake_assoc = fakes.create_one_port_association()
        arglist = [
            fake_assoc['id'],
            self.fake_bgpvpn['id'],
            '--no-advertise-fixed-ips',
        ]
        verifylist = [
            ('port_association_id', fake_assoc['id']),
            ('bgpvpn', self.fake_bgpvpn['id']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.network_client.update_bgpvpn_port_association.assert_called_once_with(
            self.fake_bgpvpn['id'],
            fake_assoc['id'],
            advertise_fixed_ips=False,
            routes=[],
        )
        self.assertIsNone(result)


class TestUnsetPortAssoc(fakes.TestNeutronClientBgpvpn):
    def setUp(self):
        super().setUp()
        self.cmd = port_association.UnsetBgpvpnPortAssoc(self.app, None)
        self.fake_bgpvpn = fakes.create_one_bgpvpn()
        self.network_client.find_bgpvpn.side_effect = (
            lambda name_or_id, **kwargs: {'id': name_or_id}
        )
        self.network_client.find_bgpvpn_port_association.return_value = {
            'routes': []
        }

    def test_unset_port_association_advertise(self):
        fake_assoc = fakes.create_one_port_association()
        arglist = [
            fake_assoc['id'],
            self.fake_bgpvpn['id'],
            '--advertise-fixed-ips',
        ]
        verifylist = [
            ('port_association_id', fake_assoc['id']),
            ('bgpvpn', self.fake_bgpvpn['id']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        result = self.cmd.take_action(parsed_args)

        self.network_client.update_bgpvpn_port_association.assert_called_once_with(
            self.fake_bgpvpn['id'],
            fake_assoc['id'],
            advertise_fixed_ips=False,
            routes=[],
        )
        self.assertIsNone(result)


class TestDeletePortAssoc(fakes.TestNeutronClientBgpvpn):
    def setUp(self):
        super().setUp()
        self.network_client.find_bgpvpn.side_effect = (
            lambda name_or_id, **kwargs: {'id': name_or_id}
        )
        self.cmd = port_association.DeleteBgpvpnPortAssoc(self.app, None)

    def test_delete_one_association(self):
        fake_bgpvpn = fakes.create_one_bgpvpn()
        fake_assoc = fakes.create_one_port_association()
        arglist = [
            fake_assoc['id'],
            fake_bgpvpn['id'],
        ]
        verifylist = [
            ('port_association_ids', [fake_assoc['id']]),
            ('bgpvpn', fake_bgpvpn['id']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.network_client.delete_bgpvpn_port_association.assert_called_once_with(
            fake_bgpvpn['id'], fake_assoc['id']
        )
        self.assertIsNone(result)

    def test_delete_multi_association(self):
        count = 3
        fake_bgpvpn = fakes.create_one_bgpvpn()
        fake_assocs = fakes.create_port_associations(count=count)
        fake_assoc_ids = [a['id'] for a in fake_assocs]
        arglist = [*fake_assoc_ids, fake_bgpvpn['id']]
        verifylist = [
            ('port_association_ids', fake_assoc_ids),
            ('bgpvpn', fake_bgpvpn['id']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.network_client.delete_bgpvpn_port_association.assert_has_calls(
            [mock.call(fake_bgpvpn['id'], id) for id in fake_assoc_ids]
        )
        self.assertIsNone(result)

    def test_delete_multi_association_with_unknown(self):
        count = 3
        fake_bgpvpn = fakes.create_one_bgpvpn()
        fake_assocs = fakes.create_port_associations(count=count)
        fake_assoc_ids = [a['id'] for a in fake_assocs]

        def raise_unknown_resource(bgpvpn_id, association_id):
            if str(count - 2) in association_id:
                raise Exception()

        self.network_client.delete_bgpvpn_port_association.side_effect = (
            raise_unknown_resource
        )
        arglist = [*fake_assoc_ids, fake_bgpvpn['id']]
        verifylist = [
            ('port_association_ids', fake_assoc_ids),
            ('bgpvpn', fake_bgpvpn['id']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

        self.network_client.delete_bgpvpn_port_association.assert_has_calls(
            [mock.call(fake_bgpvpn['id'], id) for id in fake_assoc_ids]
        )


class TestListPortAssoc(fakes.TestNeutronClientBgpvpn):
    def setUp(self):
        super().setUp()
        self.network_client.find_bgpvpn.side_effect = (
            lambda name_or_id, **kwargs: {'id': name_or_id}
        )
        self.cmd = port_association.ListBgpvpnPortAssoc(self.app, None)

    def test_list_port_associations(self):
        count = 3
        fake_bgpvpn = fakes.create_one_bgpvpn()
        fake_assocs = fakes.create_port_associations(count=count)
        self.network_client.bgpvpn_port_associations.return_value = fake_assocs
        arglist = [
            fake_bgpvpn['id'],
        ]
        verifylist = [
            ('bgpvpn', fake_bgpvpn['id']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        headers, data = self.cmd.take_action(parsed_args)

        self.network_client.bgpvpn_port_associations.assert_called_once_with(
            fake_bgpvpn['id'], retrieve_all=True
        )
        self.assertEqual(headers, list(headers_short))
        self.assertEqual(
            list(data),
            [_get_data(a, columns_short) for a in fake_assocs],
        )

    def test_list_port_associations_long_mode(self):
        count = 3
        fake_bgpvpn = fakes.create_one_bgpvpn()
        fake_assocs = fakes.create_port_associations(count=count)
        self.network_client.bgpvpn_port_associations.return_value = fake_assocs
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

        self.network_client.bgpvpn_port_associations.assert_called_once_with(
            fake_bgpvpn['id'], retrieve_all=True
        )
        self.assertEqual(headers, list(headers_long))
        self.assertEqual(
            list(data),
            [_get_data(a, columns_long) for a in fake_assocs],
        )


class TestShowPortAssoc(fakes.TestNeutronClientBgpvpn):
    def setUp(self):
        super().setUp()
        self.network_client.find_bgpvpn.side_effect = (
            lambda name_or_id, **kwargs: {'id': name_or_id}
        )
        self.cmd = port_association.ShowBgpvpnPortAssoc(self.app, None)

    def test_show_port_association(self):
        fake_bgpvpn = fakes.create_one_bgpvpn()
        fake_assoc = fakes.create_one_port_association()
        self.network_client.get_bgpvpn_port_association.return_value = (
            fake_assoc
        )

        arglist = [
            fake_assoc['id'],
            fake_bgpvpn['id'],
        ]
        verifylist = [
            ('port_association_id', fake_assoc['id']),
            ('bgpvpn', fake_bgpvpn['id']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        cols, _data = self.cmd.take_action(parsed_args)

        self.network_client.get_bgpvpn_port_association.assert_called_once_with(
            fake_bgpvpn['id'], fake_assoc['id']
        )
        # _transform_resource removes 'routes' and only adds
        # prefix_routes/bgpvpn_routes if routes exist, so with empty
        # routes the show columns won't include those fields
        self.assertIn('id', cols)
        self.assertIn('port_id', cols)
