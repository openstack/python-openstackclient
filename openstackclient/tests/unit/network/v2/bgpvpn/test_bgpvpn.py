# Copyright (c) 2016 Juniper Networks Inc.
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

import copy
import operator
from unittest import mock

from osc_lib import exceptions
from osc_lib import utils as osc_utils
from osc_lib.utils import columns as column_util

from openstackclient.network.v2.bgpvpn import bgpvpn
from openstackclient.tests.unit.network.v2.bgpvpn import fakes


columns_short = tuple(
    col
    for col, _, listing_mode in bgpvpn._attr_map
    if listing_mode in (column_util.LIST_BOTH, column_util.LIST_SHORT_ONLY)
)
columns_long = tuple(
    col
    for col, _, listing_mode in bgpvpn._attr_map
    if listing_mode in (column_util.LIST_BOTH, column_util.LIST_LONG_ONLY)
)
headers_short = tuple(
    head
    for _, head, listing_mode in bgpvpn._attr_map
    if listing_mode in (column_util.LIST_BOTH, column_util.LIST_SHORT_ONLY)
)
headers_long = tuple(
    head
    for _, head, listing_mode in bgpvpn._attr_map
    if listing_mode in (column_util.LIST_BOTH, column_util.LIST_LONG_ONLY)
)
sorted_attr_map = sorted(bgpvpn._attr_map, key=operator.itemgetter(1))
sorted_columns = tuple(col for col, _, _ in sorted_attr_map)
sorted_headers = tuple(head for _, head, _ in sorted_attr_map)


def _get_data(attrs, columns=sorted_columns):
    return osc_utils.get_dict_properties(
        attrs, columns, formatters=bgpvpn._formatters
    )


class TestCreateBgpvpn(fakes.TestNeutronClientBgpvpn):
    def setUp(self):
        super().setUp()
        self.cmd = bgpvpn.CreateBgpvpn(self.app, None)

    def test_create_bgpvpn_with_no_args(self):
        fake_bgpvpn = fakes.create_one_bgpvpn()
        self.network_client.create_bgpvpn.return_value = fake_bgpvpn
        arglist = []
        verifylist = [
            ('project', None),
            ('name', None),
            ('type', 'l3'),
            ('vni', None),
            ('local_pref', None),
            ('route_targets', None),
            ('import_targets', None),
            ('export_targets', None),
            ('route_distinguishers', None),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        cols, _data = self.cmd.take_action(parsed_args)

        self.network_client.create_bgpvpn.assert_called_once_with(
            **{'type': 'l3'}
        )

        self.assertEqual(sorted(sorted_columns), sorted(cols))

    @mock.patch('osc_lib.cli.identity.find_project')
    def test_create_bgpvpn_with_all_args(self, mock_find_project):
        attrs = {
            'tenant_id': 'new_fake_project_id',
            'name': 'fake_name',
            'type': 'l2',
            'vni': 100,
            'local_pref': 777,
            'route_targets': ['fake_rt1', 'fake_rt2', 'fake_rt3'],
            'import_targets': ['fake_irt1', 'fake_irt2', 'fake_irt3'],
            'export_targets': ['fake_ert1', 'fake_ert2', 'fake_ert3'],
            'route_distinguishers': ['fake_rd1', 'fake_rd2', 'fake_rd3'],
        }
        fake_bgpvpn = fakes.create_one_bgpvpn(attrs)
        self.network_client.create_bgpvpn.return_value = fake_bgpvpn
        mock_find_project.return_value = mock.Mock(id=fake_bgpvpn['tenant_id'])
        arglist = [
            '--project',
            fake_bgpvpn['tenant_id'],
            '--name',
            fake_bgpvpn['name'],
            '--type',
            fake_bgpvpn['type'],
            '--vni',
            str(fake_bgpvpn['vni']),
            '--local-pref',
            str(fake_bgpvpn['local_pref']),
        ]
        for rt in fake_bgpvpn['route_targets']:
            arglist.extend(['--route-target', rt])
        for rt in fake_bgpvpn['import_targets']:
            arglist.extend(['--import-target', rt])
        for rt in fake_bgpvpn['export_targets']:
            arglist.extend(['--export-target', rt])
        for rd in fake_bgpvpn['route_distinguishers']:
            arglist.extend(['--route-distinguisher', rd])
        verifylist = [
            ('project', fake_bgpvpn['tenant_id']),
            ('name', fake_bgpvpn['name']),
            ('type', fake_bgpvpn['type']),
            ('vni', fake_bgpvpn['vni']),
            ('local_pref', fake_bgpvpn['local_pref']),
            ('route_targets', fake_bgpvpn['route_targets']),
            ('import_targets', fake_bgpvpn['import_targets']),
            ('export_targets', fake_bgpvpn['export_targets']),
            ('route_distinguishers', fake_bgpvpn['route_distinguishers']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        cols, _data = self.cmd.take_action(parsed_args)

        fake_bgpvpn_call = copy.deepcopy(attrs)

        self.network_client.create_bgpvpn.assert_called_once_with(
            **fake_bgpvpn_call
        )
        self.assertEqual(sorted(sorted_columns), sorted(cols))


class TestSetBgpvpn(fakes.TestNeutronClientBgpvpn):
    def setUp(self):
        super().setUp()
        self.network_client.find_bgpvpn.side_effect = (
            lambda name_or_id, **kwargs: {'id': name_or_id}
        )

        self.cmd = bgpvpn.SetBgpvpn(self.app, None)

    def test_set_bgpvpn(self):
        attrs = {
            'route_targets': ['set_rt1', 'set_rt2', 'set_rt3'],
            'import_targets': ['set_irt1', 'set_irt2', 'set_irt3'],
            'export_targets': ['set_ert1', 'set_ert2', 'set_ert3'],
            'route_distinguishers': ['set_rd1', 'set_rd2', 'set_rd3'],
        }
        fake_bgpvpn = fakes.create_one_bgpvpn(attrs)
        self.network_client.get_bgpvpn.return_value = fake_bgpvpn
        arglist = [
            fake_bgpvpn['id'],
            '--name',
            'set_name',
            '--route-target',
            'set_rt1',
            '--import-target',
            'set_irt1',
            '--export-target',
            'set_ert1',
            '--route-distinguisher',
            'set_rd1',
        ]
        verifylist = [
            ('bgpvpn', fake_bgpvpn['id']),
            ('name', 'set_name'),
            ('route_targets', ['set_rt1']),
            ('purge_route_target', False),
            ('import_targets', ['set_irt1']),
            ('purge_import_target', False),
            ('export_targets', ['set_ert1']),
            ('purge_export_target', False),
            ('route_distinguishers', ['set_rd1']),
            ('purge_route_distinguisher', False),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        attrs = {
            'name': 'set_name',
            'route_targets': list(
                set(fake_bgpvpn['route_targets']) | set(['set_rt1'])
            ),
            'import_targets': list(
                set(fake_bgpvpn['import_targets']) | set(['set_irt1'])
            ),
            'export_targets': list(
                set(fake_bgpvpn['export_targets']) | set(['set_ert1'])
            ),
            'route_distinguishers': list(
                set(fake_bgpvpn['route_distinguishers']) | set(['set_rd1'])
            ),
        }
        self.network_client.update_bgpvpn.assert_called_once_with(
            fake_bgpvpn['id'], **attrs
        )
        self.assertIsNone(result)

    def test_set_bgpvpn_with_purge_list(self):
        fake_bgpvpn = fakes.create_one_bgpvpn()
        self.network_client.get_bgpvpn.return_value = fake_bgpvpn
        arglist = [
            fake_bgpvpn['id'],
            '--route-target',
            'set_rt1',
            '--no-route-target',
            '--import-target',
            'set_irt1',
            '--no-import-target',
            '--export-target',
            'set_ert1',
            '--no-export-target',
            '--route-distinguisher',
            'set_rd1',
            '--no-route-distinguisher',
        ]
        verifylist = [
            ('bgpvpn', fake_bgpvpn['id']),
            ('route_targets', ['set_rt1']),
            ('purge_route_target', True),
            ('import_targets', ['set_irt1']),
            ('purge_import_target', True),
            ('export_targets', ['set_ert1']),
            ('purge_export_target', True),
            ('route_distinguishers', ['set_rd1']),
            ('purge_route_distinguisher', True),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        attrs = {
            'route_targets': [],
            'import_targets': [],
            'export_targets': [],
            'route_distinguishers': [],
        }
        self.network_client.update_bgpvpn.assert_called_once_with(
            fake_bgpvpn['id'], **attrs
        )
        self.assertIsNone(result)


class TestUnsetBgpvpn(fakes.TestNeutronClientBgpvpn):
    def setUp(self):
        super().setUp()
        self.network_client.find_bgpvpn.side_effect = (
            lambda name_or_id, **kwargs: {'id': name_or_id}
        )
        self.cmd = bgpvpn.UnsetBgpvpn(self.app, None)

    def test_unset_bgpvpn(self):
        attrs = {
            'route_targets': ['unset_rt1', 'unset_rt2', 'unset_rt3'],
            'import_targets': ['unset_irt1', 'unset_irt2', 'unset_irt3'],
            'export_targets': ['unset_ert1', 'unset_ert2', 'unset_ert3'],
            'route_distinguishers': ['unset_rd1', 'unset_rd2', 'unset_rd3'],
        }
        fake_bgpvpn = fakes.create_one_bgpvpn(attrs)
        self.network_client.get_bgpvpn.return_value = fake_bgpvpn
        arglist = [
            fake_bgpvpn['id'],
            '--route-target',
            'unset_rt1',
            '--import-target',
            'unset_irt1',
            '--export-target',
            'unset_ert1',
            '--route-distinguisher',
            'unset_rd1',
        ]
        verifylist = [
            ('bgpvpn', fake_bgpvpn['id']),
            ('route_targets', ['unset_rt1']),
            ('purge_route_target', False),
            ('import_targets', ['unset_irt1']),
            ('purge_import_target', False),
            ('export_targets', ['unset_ert1']),
            ('purge_export_target', False),
            ('route_distinguishers', ['unset_rd1']),
            ('purge_route_distinguisher', False),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        attrs = {
            'route_targets': list(
                set(fake_bgpvpn['route_targets']) - set(['unset_rt1'])
            ),
            'import_targets': list(
                set(fake_bgpvpn['import_targets']) - set(['unset_irt1'])
            ),
            'export_targets': list(
                set(fake_bgpvpn['export_targets']) - set(['unset_ert1'])
            ),
            'route_distinguishers': list(
                set(fake_bgpvpn['route_distinguishers']) - set(['unset_rd1'])
            ),
        }
        self.network_client.update_bgpvpn.assert_called_once_with(
            fake_bgpvpn['id'], **attrs
        )
        self.assertIsNone(result)

    def test_unset_bgpvpn_with_purge_list(self):
        fake_bgpvpn = fakes.create_one_bgpvpn()
        self.network_client.get_bgpvpn.return_value = fake_bgpvpn
        arglist = [
            fake_bgpvpn['id'],
            '--route-target',
            'unset_rt1',
            '--all-route-target',
            '--import-target',
            'unset_irt1',
            '--all-import-target',
            '--export-target',
            'unset_ert1',
            '--all-export-target',
            '--route-distinguisher',
            'unset_rd1',
            '--all-route-distinguisher',
        ]
        verifylist = [
            ('bgpvpn', fake_bgpvpn['id']),
            ('route_targets', ['unset_rt1']),
            ('purge_route_target', True),
            ('import_targets', ['unset_irt1']),
            ('purge_import_target', True),
            ('export_targets', ['unset_ert1']),
            ('purge_export_target', True),
            ('route_distinguishers', ['unset_rd1']),
            ('purge_route_distinguisher', True),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        attrs = {
            'route_targets': [],
            'import_targets': [],
            'export_targets': [],
            'route_distinguishers': [],
        }
        self.network_client.update_bgpvpn.assert_called_once_with(
            fake_bgpvpn['id'], **attrs
        )
        self.assertIsNone(result)


class TestDeleteBgpvpn(fakes.TestNeutronClientBgpvpn):
    def setUp(self):
        super().setUp()
        self.network_client.find_bgpvpn.side_effect = (
            lambda name_or_id, **kwargs: {'id': name_or_id}
        )
        self.cmd = bgpvpn.DeleteBgpvpn(self.app, None)

    def test_delete_one_bgpvpn(self):
        fake_bgpvpn = fakes.create_one_bgpvpn()
        arglist = [
            fake_bgpvpn['id'],
        ]
        verifylist = [
            ('bgpvpns', [fake_bgpvpn['id']]),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.network_client.delete_bgpvpn.assert_called_once_with(
            fake_bgpvpn['id']
        )
        self.assertIsNone(result)

    def test_delete_multi_bpgvpn(self):
        fake_bgpvpns = fakes.create_bgpvpns(count=3)
        fake_bgpvpn_ids = [fake_bgpvpn['id'] for fake_bgpvpn in fake_bgpvpns]
        arglist = fake_bgpvpn_ids
        verifylist = [
            ('bgpvpns', fake_bgpvpn_ids),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.network_client.delete_bgpvpn.assert_has_calls(
            [mock.call(id) for id in fake_bgpvpn_ids]
        )
        self.assertIsNone(result)

    def test_delete_multi_bpgvpn_with_unknown(self):
        count = 3
        fake_bgpvpns = fakes.create_bgpvpns(count=count)
        fake_bgpvpn_ids = [fake_bgpvpn['id'] for fake_bgpvpn in fake_bgpvpns]

        def raise_unknonw_resource(resource_path, name_or_id):
            if str(count - 2) in name_or_id:
                raise Exception()

        self.network_client.delete_bgpvpn.side_effect = raise_unknonw_resource
        arglist = fake_bgpvpn_ids
        verifylist = [
            ('bgpvpns', fake_bgpvpn_ids),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )

        self.network_client.delete_bgpvpn.assert_has_calls(
            [mock.call(id) for id in fake_bgpvpn_ids]
        )


class TestListBgpvpn(fakes.TestNeutronClientBgpvpn):
    def setUp(self):
        super().setUp()
        self.cmd = bgpvpn.ListBgpvpn(self.app, None)

    def test_list_all_bgpvpn(self):
        count = 3
        fake_bgpvpns = fakes.create_bgpvpns(count=count)
        self.network_client.bgpvpns.return_value = fake_bgpvpns
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        headers, data = self.cmd.take_action(parsed_args)

        self.network_client.bgpvpns.assert_called_once()
        self.assertEqual(headers, list(headers_short))
        self.assertListEqual(
            list(data),
            [
                _get_data(fake_bgpvpn, columns_short)
                for fake_bgpvpn in fake_bgpvpns
            ],
        )

    def test_list_all_bgpvpn_long_mode(self):
        count = 3
        fake_bgpvpns = fakes.create_bgpvpns(count=count)
        self.network_client.bgpvpns.return_value = fake_bgpvpns
        arglist = [
            '--long',
        ]
        verifylist = [
            ('long', True),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        headers, data = self.cmd.take_action(parsed_args)

        self.network_client.bgpvpns.assert_called_once()
        self.assertEqual(headers, list(headers_long))
        self.assertListEqual(
            list(data),
            [
                _get_data(fake_bgpvpn, columns_long)
                for fake_bgpvpn in fake_bgpvpns
            ],
        )

    @mock.patch('osc_lib.cli.identity.find_project')
    def test_list_project_bgpvpn(self, mock_find_project):
        count = 3
        project_id = 'list_fake_project_id'
        attrs = {'tenant_id': project_id}
        fake_bgpvpns = fakes.create_bgpvpns(count=count, attrs=attrs)
        self.network_client.bgpvpns.return_value = fake_bgpvpns
        mock_find_project.return_value = mock.Mock(id=project_id)
        arglist = [
            '--project',
            project_id,
        ]
        verifylist = [
            ('project', project_id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        headers, data = self.cmd.take_action(parsed_args)

        self.network_client.bgpvpns.assert_called_once_with(
            tenant_id=project_id
        )
        self.assertEqual(headers, list(headers_short))
        self.assertListEqual(
            list(data),
            [
                _get_data(fake_bgpvpn, columns_short)
                for fake_bgpvpn in fake_bgpvpns
            ],
        )

    def test_list_bgpvpn_with_filters(self):
        count = 3
        name = 'fake_id0'
        layer_type = 'l2'
        attrs = {'type': layer_type}
        fake_bgpvpns = fakes.create_bgpvpns(count=count, attrs=attrs)
        returned_bgpvpn = fake_bgpvpns[0]
        self.network_client.bgpvpns.return_value = [returned_bgpvpn]
        arglist = [
            '--property',
            f'name={name}',
            '--property',
            f'type={layer_type}',
        ]
        verifylist = [
            ('property', {'name': name, 'type': layer_type}),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        headers, data = self.cmd.take_action(parsed_args)

        self.network_client.bgpvpns.assert_called_once_with(
            name=name, type=layer_type
        )
        self.assertEqual(headers, list(headers_short))
        self.assertListEqual(
            list(data), [_get_data(returned_bgpvpn, columns_short)]
        )


class TestShowBgpvpn(fakes.TestNeutronClientBgpvpn):
    def setUp(self):
        super().setUp()
        self.cmd = bgpvpn.ShowBgpvpn(self.app, None)
        self.network_client.find_bgpvpn.side_effect = (
            lambda name_or_id, **kwargs: {'id': name_or_id}
        )

    def test_show_bgpvpn(self):
        fake_bgpvpn = fakes.create_one_bgpvpn()
        self.network_client.get_bgpvpn.return_value = fake_bgpvpn
        arglist = [
            fake_bgpvpn['id'],
        ]
        verifylist = [
            ('bgpvpn', fake_bgpvpn['id']),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        headers, _data = self.cmd.take_action(parsed_args)

        self.network_client.get_bgpvpn.assert_called_once_with(
            fake_bgpvpn['id']
        )
        self.assertEqual(sorted(sorted_columns), sorted(headers))
