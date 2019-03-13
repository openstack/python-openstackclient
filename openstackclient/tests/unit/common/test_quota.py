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

import copy

import mock
from osc_lib import exceptions

from openstackclient.common import quota
from openstackclient.tests.unit.compute.v2 import fakes as compute_fakes
from openstackclient.tests.unit import fakes
from openstackclient.tests.unit.identity.v2_0 import fakes as identity_fakes
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes_v3
from openstackclient.tests.unit.network.v2 import fakes as network_fakes
from openstackclient.tests.unit.volume.v2 import fakes as volume_fakes


class FakeQuotaResource(fakes.FakeResource):

    _keys = {'property': 'value'}

    def set_keys(self, args):
        self._keys.update(args)

    def unset_keys(self, keys):
        for key in keys:
            self._keys.pop(key, None)

    def get_keys(self):
        return self._keys


class TestQuota(compute_fakes.TestComputev2):

    def setUp(self):
        super(TestQuota, self).setUp()

        # Set up common projects
        self.projects = identity_fakes_v3.FakeProject.create_projects(count=2)
        self.projects_mock = self.app.client_manager.identity.projects
        self.projects_mock.reset_mock()
        self.projects_mock.get.return_value = self.projects[0]

        self.compute_quotas_mock = self.app.client_manager.compute.quotas
        self.compute_quotas_mock.reset_mock()
        self.compute_quotas_class_mock = \
            self.app.client_manager.compute.quota_classes
        self.compute_quotas_class_mock.reset_mock()

        self.volume_quotas_mock = self.app.client_manager.volume.quotas
        self.volume_quotas_mock.reset_mock()
        self.volume_quotas_class_mock = \
            self.app.client_manager.volume.quota_classes
        self.volume_quotas_class_mock.reset_mock()

        self.app.client_manager.auth_ref = mock.Mock()
        self.app.client_manager.auth_ref.service_catalog = mock.Mock()
        self.service_catalog_mock = \
            self.app.client_manager.auth_ref.service_catalog
        self.service_catalog_mock.reset_mock()
        self.app.client_manager.auth_ref.project_id = identity_fakes.project_id


class TestQuotaList(TestQuota):
    """Test cases for quota list command"""

    compute_column_header = (
        'Project ID',
        'Cores',
        'Fixed IPs',
        'Injected Files',
        'Injected File Content Bytes',
        'Injected File Path Bytes',
        'Instances',
        'Key Pairs',
        'Metadata Items',
        'Ram',
        'Server Groups',
        'Server Group Members',
    )

    network_column_header = (
        'Project ID',
        'Floating IPs',
        'Networks',
        'Ports',
        'RBAC Policies',
        'Routers',
        'Security Groups',
        'Security Group Rules',
        'Subnets',
        'Subnet Pools'
    )

    volume_column_header = (
        'Project ID',
        'Backups',
        'Backup Gigabytes',
        'Gigabytes',
        'Per Volume Gigabytes',
        'Snapshots',
        'Volumes',
    )

    def setUp(self):
        super(TestQuotaList, self).setUp()

        # Work with multiple projects in this class
        self.projects_mock.get.side_effect = self.projects
        self.projects_mock.list.return_value = self.projects

        self.compute_quotas = [
            compute_fakes.FakeQuota.create_one_comp_quota(),
            compute_fakes.FakeQuota.create_one_comp_quota(),
        ]
        self.compute_default_quotas = [
            compute_fakes.FakeQuota.create_one_default_comp_quota(),
            compute_fakes.FakeQuota.create_one_default_comp_quota(),
        ]
        self.compute = self.app.client_manager.compute
        self.compute.quotas.defaults = mock.Mock(
            side_effect=self.compute_default_quotas,
        )

        self.compute_reference_data = (
            self.projects[0].id,
            self.compute_quotas[0].cores,
            self.compute_quotas[0].fixed_ips,
            self.compute_quotas[0].injected_files,
            self.compute_quotas[0].injected_file_content_bytes,
            self.compute_quotas[0].injected_file_path_bytes,
            self.compute_quotas[0].instances,
            self.compute_quotas[0].key_pairs,
            self.compute_quotas[0].metadata_items,
            self.compute_quotas[0].ram,
            self.compute_quotas[0].server_groups,
            self.compute_quotas[0].server_group_members,
        )

        self.network_quotas = [
            network_fakes.FakeQuota.create_one_net_quota(),
            network_fakes.FakeQuota.create_one_net_quota(),
        ]
        self.network_default_quotas = [
            network_fakes.FakeQuota.create_one_default_net_quota(),
            network_fakes.FakeQuota.create_one_default_net_quota(),
        ]
        self.network = self.app.client_manager.network
        self.network.get_quota_default = mock.Mock(
            side_effect=self.network_default_quotas,
        )

        self.network_reference_data = (
            self.projects[0].id,
            self.network_quotas[0].floating_ips,
            self.network_quotas[0].networks,
            self.network_quotas[0].ports,
            self.network_quotas[0].rbac_policies,
            self.network_quotas[0].routers,
            self.network_quotas[0].security_groups,
            self.network_quotas[0].security_group_rules,
            self.network_quotas[0].subnets,
            self.network_quotas[0].subnet_pools,
        )

        self.volume_quotas = [
            volume_fakes.FakeQuota.create_one_vol_quota(),
            volume_fakes.FakeQuota.create_one_vol_quota(),
        ]
        self.volume_default_quotas = [
            volume_fakes.FakeQuota.create_one_default_vol_quota(),
            volume_fakes.FakeQuota.create_one_default_vol_quota(),
        ]
        self.volume = self.app.client_manager.volume
        self.volume.quotas.defaults = mock.Mock(
            side_effect=self.volume_default_quotas,
        )

        self.volume_reference_data = (
            self.projects[0].id,
            self.volume_quotas[0].backups,
            self.volume_quotas[0].backup_gigabytes,
            self.volume_quotas[0].gigabytes,
            self.volume_quotas[0].per_volume_gigabytes,
            self.volume_quotas[0].snapshots,
            self.volume_quotas[0].volumes,
        )

        self.cmd = quota.ListQuota(self.app, None)

    @staticmethod
    def _get_detailed_reference_data(quota):
        reference_data = []
        for name, values in quota.to_dict().items():
            if type(values) is dict:
                if 'used' in values:
                    # For network quota it's "used" key instead of "in_use"
                    in_use = values['used']
                else:
                    in_use = values['in_use']
                resource_values = [
                    in_use,
                    values['reserved'],
                    values['limit']]
                reference_data.append(tuple([name] + resource_values))
        return reference_data

    def test_quota_list_details_compute(self):
        detailed_quota = (
            compute_fakes.FakeQuota.create_one_comp_detailed_quota())

        detailed_column_header = (
            'Resource',
            'In Use',
            'Reserved',
            'Limit',
        )
        detailed_reference_data = (
            self._get_detailed_reference_data(detailed_quota))

        self.compute.quotas.get = mock.Mock(return_value=detailed_quota)

        arglist = [
            '--detail', '--compute',
        ]
        verifylist = [
            ('detail', True),
            ('compute', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        ret_quotas = list(data)

        self.assertEqual(detailed_column_header, columns)
        self.assertEqual(
            sorted(detailed_reference_data), sorted(ret_quotas))

    def test_quota_list_details_network(self):
        detailed_quota = (
            network_fakes.FakeQuota.create_one_net_detailed_quota())

        detailed_column_header = (
            'Resource',
            'In Use',
            'Reserved',
            'Limit',
        )
        detailed_reference_data = (
            self._get_detailed_reference_data(detailed_quota))

        self.network.get_quota = mock.Mock(return_value=detailed_quota)

        arglist = [
            '--detail', '--network',
        ]
        verifylist = [
            ('detail', True),
            ('network', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        ret_quotas = list(data)

        self.assertEqual(detailed_column_header, columns)
        self.assertEqual(
            sorted(detailed_reference_data), sorted(ret_quotas))

    def test_quota_list_compute(self):
        # Two projects with non-default quotas
        self.compute.quotas.get = mock.Mock(
            side_effect=self.compute_quotas,
        )

        arglist = [
            '--compute',
        ]
        verifylist = [
            ('compute', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        ret_quotas = list(data)

        self.assertEqual(self.compute_column_header, columns)
        self.assertEqual(self.compute_reference_data, ret_quotas[0])
        self.assertEqual(2, len(ret_quotas))

    def test_quota_list_compute_default(self):
        # One of the projects is at defaults
        self.compute.quotas.get = mock.Mock(
            side_effect=[
                self.compute_quotas[0],
                compute_fakes.FakeQuota.create_one_default_comp_quota(),
            ],
        )

        arglist = [
            '--compute',
        ]
        verifylist = [
            ('compute', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        ret_quotas = list(data)

        self.assertEqual(self.compute_column_header, columns)
        self.assertEqual(self.compute_reference_data, ret_quotas[0])
        self.assertEqual(1, len(ret_quotas))

    def test_quota_list_compute_no_project_not_found(self):
        # Make one of the projects disappear
        self.compute.quotas.get = mock.Mock(
            side_effect=[
                self.compute_quotas[0],
                exceptions.NotFound("NotFound"),
            ],
        )

        arglist = [
            '--compute',
        ]
        verifylist = [
            ('compute', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        ret_quotas = list(data)

        self.assertEqual(self.compute_column_header, columns)
        self.assertEqual(self.compute_reference_data, ret_quotas[0])
        self.assertEqual(1, len(ret_quotas))

    def test_quota_list_compute_no_project_4xx(self):
        # Make one of the projects disappear
        self.compute.quotas.get = mock.Mock(
            side_effect=[
                self.compute_quotas[0],
                exceptions.BadRequest("Bad request"),
            ],
        )

        arglist = [
            '--compute',
        ]
        verifylist = [
            ('compute', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        ret_quotas = list(data)

        self.assertEqual(self.compute_column_header, columns)
        self.assertEqual(self.compute_reference_data, ret_quotas[0])
        self.assertEqual(1, len(ret_quotas))

    def test_quota_list_compute_no_project_5xx(self):
        # Make one of the projects disappear
        self.compute.quotas.get = mock.Mock(
            side_effect=[
                self.compute_quotas[0],
                exceptions.HTTPNotImplemented("Not implemented??"),
            ],
        )

        arglist = [
            '--compute',
        ]
        verifylist = [
            ('compute', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            exceptions.HTTPNotImplemented,
            self.cmd.take_action,
            parsed_args,
        )

    def test_quota_list_network(self):
        # Two projects with non-default quotas
        self.network.get_quota = mock.Mock(
            side_effect=self.network_quotas,
        )

        arglist = [
            '--network',
        ]
        verifylist = [
            ('network', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        ret_quotas = list(data)

        self.assertEqual(self.network_column_header, columns)
        self.assertEqual(self.network_reference_data, ret_quotas[0])
        self.assertEqual(2, len(ret_quotas))

    def test_quota_list_network_default(self):
        # Two projects with non-default quotas
        self.network.get_quota = mock.Mock(
            side_effect=[
                self.network_quotas[0],
                network_fakes.FakeQuota.create_one_default_net_quota(),
            ],
        )

        arglist = [
            '--network',
        ]
        verifylist = [
            ('network', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        ret_quotas = list(data)

        self.assertEqual(self.network_column_header, columns)
        self.assertEqual(self.network_reference_data, ret_quotas[0])
        self.assertEqual(1, len(ret_quotas))

    def test_quota_list_network_no_project(self):
        # Two projects with non-default quotas
        self.network.get_quota = mock.Mock(
            side_effect=[
                self.network_quotas[0],
                exceptions.NotFound("NotFound"),
            ],
        )

        arglist = [
            '--network',
        ]
        verifylist = [
            ('network', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        ret_quotas = list(data)

        self.assertEqual(self.network_column_header, columns)
        self.assertEqual(self.network_reference_data, ret_quotas[0])
        self.assertEqual(1, len(ret_quotas))

    def test_quota_list_volume(self):
        # Two projects with non-default quotas
        self.volume.quotas.get = mock.Mock(
            side_effect=self.volume_quotas,
        )

        arglist = [
            '--volume',
        ]
        verifylist = [
            ('volume', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        ret_quotas = list(data)

        self.assertEqual(self.volume_column_header, columns)
        self.assertEqual(self.volume_reference_data, ret_quotas[0])
        self.assertEqual(2, len(ret_quotas))

    def test_quota_list_volume_default(self):
        # Two projects with non-default quotas
        self.volume.quotas.get = mock.Mock(
            side_effect=[
                self.volume_quotas[0],
                volume_fakes.FakeQuota.create_one_default_vol_quota(),
            ],
        )

        arglist = [
            '--volume',
        ]
        verifylist = [
            ('volume', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        ret_quotas = list(data)

        self.assertEqual(self.volume_column_header, columns)
        self.assertEqual(self.volume_reference_data, ret_quotas[0])
        self.assertEqual(1, len(ret_quotas))

    def test_quota_list_volume_no_project(self):
        # Two projects with non-default quotas
        self.volume.quotas.get = mock.Mock(
            side_effect=[
                self.volume_quotas[0],
                volume_fakes.FakeQuota.create_one_default_vol_quota(),
            ],
        )

        arglist = [
            '--volume',
        ]
        verifylist = [
            ('volume', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)
        ret_quotas = list(data)

        self.assertEqual(self.volume_column_header, columns)
        self.assertEqual(self.volume_reference_data, ret_quotas[0])
        self.assertEqual(1, len(ret_quotas))


class TestQuotaSet(TestQuota):

    def setUp(self):
        super(TestQuotaSet, self).setUp()

        self.compute_quotas_mock.update.return_value = FakeQuotaResource(
            None,
            copy.deepcopy(compute_fakes.QUOTA),
            loaded=True,
        )
        self.compute_quotas_class_mock.update.return_value = FakeQuotaResource(
            None,
            copy.deepcopy(compute_fakes.QUOTA),
            loaded=True,
        )

        self.volume_quotas_mock.update.return_value = FakeQuotaResource(
            None,
            copy.deepcopy(compute_fakes.QUOTA),
            loaded=True,
        )
        self.volume_quotas_class_mock.update.return_value = FakeQuotaResource(
            None,
            copy.deepcopy(compute_fakes.QUOTA),
            loaded=True,
        )

        self.network_mock = self.app.client_manager.network
        self.network_mock.update_quota = mock.Mock()

        self.cmd = quota.SetQuota(self.app, None)

    def test_quota_set(self):
        arglist = [
            '--floating-ips', str(compute_fakes.floating_ip_num),
            '--fixed-ips', str(compute_fakes.fix_ip_num),
            '--injected-files', str(compute_fakes.injected_file_num),
            '--injected-file-size', str(compute_fakes.injected_file_size_num),
            '--injected-path-size', str(compute_fakes.injected_path_size_num),
            '--key-pairs', str(compute_fakes.key_pair_num),
            '--cores', str(compute_fakes.core_num),
            '--ram', str(compute_fakes.ram_num),
            '--instances', str(compute_fakes.instance_num),
            '--properties', str(compute_fakes.property_num),
            '--secgroup-rules', str(compute_fakes.secgroup_rule_num),
            '--secgroups', str(compute_fakes.secgroup_num),
            '--server-groups', str(compute_fakes.servgroup_num),
            '--server-group-members', str(compute_fakes.servgroup_members_num),
            self.projects[0].name,
        ]
        verifylist = [
            ('floating_ips', compute_fakes.floating_ip_num),
            ('fixed_ips', compute_fakes.fix_ip_num),
            ('injected_files', compute_fakes.injected_file_num),
            ('injected_file_content_bytes',
             compute_fakes.injected_file_size_num),
            ('injected_file_path_bytes', compute_fakes.injected_path_size_num),
            ('key_pairs', compute_fakes.key_pair_num),
            ('cores', compute_fakes.core_num),
            ('ram', compute_fakes.ram_num),
            ('instances', compute_fakes.instance_num),
            ('metadata_items', compute_fakes.property_num),
            ('security_group_rules', compute_fakes.secgroup_rule_num),
            ('security_groups', compute_fakes.secgroup_num),
            ('server_groups', compute_fakes.servgroup_num),
            ('server_group_members', compute_fakes.servgroup_members_num),
            ('project', self.projects[0].name),
        ]
        self.app.client_manager.network_endpoint_enabled = False
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        kwargs = {
            'floating_ips': compute_fakes.floating_ip_num,
            'fixed_ips': compute_fakes.fix_ip_num,
            'injected_files': compute_fakes.injected_file_num,
            'injected_file_content_bytes':
                compute_fakes.injected_file_size_num,
            'injected_file_path_bytes': compute_fakes.injected_path_size_num,
            'key_pairs': compute_fakes.key_pair_num,
            'cores': compute_fakes.core_num,
            'ram': compute_fakes.ram_num,
            'instances': compute_fakes.instance_num,
            'metadata_items': compute_fakes.property_num,
            'security_group_rules': compute_fakes.secgroup_rule_num,
            'security_groups': compute_fakes.secgroup_num,
            'server_groups': compute_fakes.servgroup_num,
            'server_group_members': compute_fakes.servgroup_members_num,
        }

        self.compute_quotas_mock.update.assert_called_once_with(
            self.projects[0].id,
            **kwargs
        )
        self.assertIsNone(result)

    def test_quota_set_volume(self):
        arglist = [
            '--gigabytes', str(volume_fakes.QUOTA['gigabytes']),
            '--snapshots', str(volume_fakes.QUOTA['snapshots']),
            '--volumes', str(volume_fakes.QUOTA['volumes']),
            '--backups', str(volume_fakes.QUOTA['backups']),
            '--backup-gigabytes', str(volume_fakes.QUOTA['backup_gigabytes']),
            '--per-volume-gigabytes',
            str(volume_fakes.QUOTA['per_volume_gigabytes']),
            self.projects[0].name,
        ]
        verifylist = [
            ('gigabytes', volume_fakes.QUOTA['gigabytes']),
            ('snapshots', volume_fakes.QUOTA['snapshots']),
            ('volumes', volume_fakes.QUOTA['volumes']),
            ('backups', volume_fakes.QUOTA['backups']),
            ('backup_gigabytes', volume_fakes.QUOTA['backup_gigabytes']),
            ('per_volume_gigabytes',
                volume_fakes.QUOTA['per_volume_gigabytes']),
            ('project', self.projects[0].name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        kwargs = {
            'gigabytes': volume_fakes.QUOTA['gigabytes'],
            'snapshots': volume_fakes.QUOTA['snapshots'],
            'volumes': volume_fakes.QUOTA['volumes'],
            'backups': volume_fakes.QUOTA['backups'],
            'backup_gigabytes': volume_fakes.QUOTA['backup_gigabytes'],
            'per_volume_gigabytes': volume_fakes.QUOTA['per_volume_gigabytes']
        }

        self.volume_quotas_mock.update.assert_called_once_with(
            self.projects[0].id,
            **kwargs
        )

        self.assertIsNone(result)

    def test_quota_set_volume_with_volume_type(self):
        arglist = [
            '--gigabytes', str(volume_fakes.QUOTA['gigabytes']),
            '--snapshots', str(volume_fakes.QUOTA['snapshots']),
            '--volumes', str(volume_fakes.QUOTA['volumes']),
            '--backups', str(volume_fakes.QUOTA['backups']),
            '--backup-gigabytes', str(volume_fakes.QUOTA['backup_gigabytes']),
            '--per-volume-gigabytes',
            str(volume_fakes.QUOTA['per_volume_gigabytes']),
            '--volume-type', 'volume_type_backend',
            self.projects[0].name,
        ]
        verifylist = [
            ('gigabytes', volume_fakes.QUOTA['gigabytes']),
            ('snapshots', volume_fakes.QUOTA['snapshots']),
            ('volumes', volume_fakes.QUOTA['volumes']),
            ('backups', volume_fakes.QUOTA['backups']),
            ('backup_gigabytes', volume_fakes.QUOTA['backup_gigabytes']),
            ('per_volume_gigabytes',
                volume_fakes.QUOTA['per_volume_gigabytes']),
            ('volume_type', 'volume_type_backend'),
            ('project', self.projects[0].name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        kwargs = {
            'gigabytes_volume_type_backend': volume_fakes.QUOTA['gigabytes'],
            'snapshots_volume_type_backend': volume_fakes.QUOTA['snapshots'],
            'volumes_volume_type_backend': volume_fakes.QUOTA['volumes'],
            'backups': volume_fakes.QUOTA['backups'],
            'backup_gigabytes': volume_fakes.QUOTA['backup_gigabytes'],
            'per_volume_gigabytes': volume_fakes.QUOTA['per_volume_gigabytes']
        }

        self.volume_quotas_mock.update.assert_called_once_with(
            self.projects[0].id,
            **kwargs
        )
        self.assertIsNone(result)

    def test_quota_set_network(self):
        arglist = [
            '--subnets', str(network_fakes.QUOTA['subnet']),
            '--networks', str(network_fakes.QUOTA['network']),
            '--floating-ips', str(network_fakes.QUOTA['floatingip']),
            '--subnetpools', str(network_fakes.QUOTA['subnetpool']),
            '--secgroup-rules',
            str(network_fakes.QUOTA['security_group_rule']),
            '--secgroups', str(network_fakes.QUOTA['security_group']),
            '--routers', str(network_fakes.QUOTA['router']),
            '--rbac-policies', str(network_fakes.QUOTA['rbac_policy']),
            '--ports', str(network_fakes.QUOTA['port']),
            self.projects[0].name,
        ]
        verifylist = [
            ('subnet', network_fakes.QUOTA['subnet']),
            ('network', network_fakes.QUOTA['network']),
            ('floatingip', network_fakes.QUOTA['floatingip']),
            ('subnetpool', network_fakes.QUOTA['subnetpool']),
            ('security_group_rule',
                network_fakes.QUOTA['security_group_rule']),
            ('security_group', network_fakes.QUOTA['security_group']),
            ('router', network_fakes.QUOTA['router']),
            ('rbac_policy', network_fakes.QUOTA['rbac_policy']),
            ('port', network_fakes.QUOTA['port']),
            ('project', self.projects[0].name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        kwargs = {
            'subnet': network_fakes.QUOTA['subnet'],
            'network': network_fakes.QUOTA['network'],
            'floatingip': network_fakes.QUOTA['floatingip'],
            'subnetpool': network_fakes.QUOTA['subnetpool'],
            'security_group_rule':
                network_fakes.QUOTA['security_group_rule'],
            'security_group': network_fakes.QUOTA['security_group'],
            'router': network_fakes.QUOTA['router'],
            'rbac_policy': network_fakes.QUOTA['rbac_policy'],
            'port': network_fakes.QUOTA['port'],
        }
        self.network_mock.update_quota.assert_called_once_with(
            self.projects[0].id,
            **kwargs
        )
        self.assertIsNone(result)

    def test_quota_set_with_class(self):
        arglist = [
            '--injected-files', str(compute_fakes.injected_file_num),
            '--injected-file-size', str(compute_fakes.injected_file_size_num),
            '--injected-path-size', str(compute_fakes.injected_path_size_num),
            '--key-pairs', str(compute_fakes.key_pair_num),
            '--cores', str(compute_fakes.core_num),
            '--ram', str(compute_fakes.ram_num),
            '--instances', str(compute_fakes.instance_num),
            '--properties', str(compute_fakes.property_num),
            '--server-groups', str(compute_fakes.servgroup_num),
            '--server-group-members', str(compute_fakes.servgroup_members_num),
            '--gigabytes', str(compute_fakes.floating_ip_num),
            '--snapshots', str(compute_fakes.fix_ip_num),
            '--volumes', str(volume_fakes.QUOTA['volumes']),
            '--network', str(network_fakes.QUOTA['network']),
            '--class',
            self.projects[0].name,
        ]
        verifylist = [
            ('injected_files', compute_fakes.injected_file_num),
            ('injected_file_content_bytes',
                compute_fakes.injected_file_size_num),
            ('injected_file_path_bytes', compute_fakes.injected_path_size_num),
            ('key_pairs', compute_fakes.key_pair_num),
            ('cores', compute_fakes.core_num),
            ('ram', compute_fakes.ram_num),
            ('instances', compute_fakes.instance_num),
            ('metadata_items', compute_fakes.property_num),
            ('server_groups', compute_fakes.servgroup_num),
            ('server_group_members', compute_fakes.servgroup_members_num),
            ('gigabytes', compute_fakes.floating_ip_num),
            ('snapshots', compute_fakes.fix_ip_num),
            ('volumes', volume_fakes.QUOTA['volumes']),
            ('network', network_fakes.QUOTA['network']),
            ('quota_class', True),
            ('project', self.projects[0].name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        kwargs_compute = {
            'injected_files': compute_fakes.injected_file_num,
            'injected_file_content_bytes':
                compute_fakes.injected_file_size_num,
            'injected_file_path_bytes': compute_fakes.injected_path_size_num,
            'key_pairs': compute_fakes.key_pair_num,
            'cores': compute_fakes.core_num,
            'ram': compute_fakes.ram_num,
            'instances': compute_fakes.instance_num,
            'metadata_items': compute_fakes.property_num,
            'server_groups': compute_fakes.servgroup_num,
            'server_group_members': compute_fakes.servgroup_members_num,
        }
        kwargs_volume = {
            'gigabytes': compute_fakes.floating_ip_num,
            'snapshots': compute_fakes.fix_ip_num,
            'volumes': volume_fakes.QUOTA['volumes'],
        }

        self.compute_quotas_class_mock.update.assert_called_with(
            self.projects[0].name,
            **kwargs_compute
        )
        self.volume_quotas_class_mock.update.assert_called_with(
            self.projects[0].name,
            **kwargs_volume
        )
        self.assertNotCalled(self.network_mock.update_quota)
        self.assertIsNone(result)


class TestQuotaShow(TestQuota):

    def setUp(self):
        super(TestQuotaShow, self).setUp()

        self.compute_quota = compute_fakes.FakeQuota.create_one_comp_quota()
        self.compute_quotas_mock.get.return_value = self.compute_quota
        self.compute_default_quota = \
            compute_fakes.FakeQuota.create_one_default_comp_quota()
        self.compute_quotas_mock.defaults.return_value = \
            self.compute_default_quota
        self.compute_quotas_class_mock.get.return_value = FakeQuotaResource(
            None,
            copy.deepcopy(compute_fakes.QUOTA),
            loaded=True,
        )

        self.volume_quota = volume_fakes.FakeQuota.create_one_vol_quota()
        self.volume_quotas_mock.get.return_value = self.volume_quota
        self.volume_default_quota = \
            volume_fakes.FakeQuota.create_one_default_vol_quota()
        self.volume_quotas_mock.defaults.return_value = \
            self.volume_default_quota
        self.volume_quotas_class_mock.get.return_value = FakeQuotaResource(
            None,
            copy.deepcopy(volume_fakes.QUOTA),
            loaded=True,
        )

        fake_network_endpoint = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.ENDPOINT),
            loaded=True,
        )

        self.service_catalog_mock.get_endpoints.return_value = {
            'network': fake_network_endpoint
        }

        self.app.client_manager.network = network_fakes.FakeNetworkV2Client(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN,
        )
        self.network = self.app.client_manager.network
        self.network.get_quota = mock.Mock(
            return_value=network_fakes.QUOTA,
        )
        self.network.get_quota_default = mock.Mock(
            return_value=network_fakes.QUOTA,
        )

        self.cmd = quota.ShowQuota(self.app, None)

    def test_quota_show(self):
        arglist = [
            self.projects[0].name,
        ]
        verifylist = [
            ('project', self.projects[0].name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.compute_quotas_mock.get.assert_called_once_with(
            self.projects[0].id, detail=False
        )
        self.volume_quotas_mock.get.assert_called_once_with(
            self.projects[0].id,
        )
        self.network.get_quota.assert_called_once_with(
            self.projects[0].id, details=False
        )
        self.assertNotCalled(self.network.get_quota_default)

    def test_quota_show_with_default(self):
        arglist = [
            '--default',
            self.projects[0].name,
        ]
        verifylist = [
            ('default', True),
            ('project', self.projects[0].name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.compute_quotas_mock.defaults.assert_called_once_with(
            self.projects[0].id,
        )
        self.volume_quotas_mock.defaults.assert_called_once_with(
            self.projects[0].id,
        )
        self.network.get_quota_default.assert_called_once_with(
            self.projects[0].id,
        )
        self.assertNotCalled(self.network.get_quota)

    def test_quota_show_with_class(self):
        arglist = [
            '--class',
            self.projects[0].name,
        ]
        verifylist = [
            ('quota_class', True),
            ('project', self.projects[0].name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.compute_quotas_class_mock.get.assert_called_once_with(
            self.projects[0].name,
        )
        self.volume_quotas_class_mock.get.assert_called_once_with(
            self.projects[0].name,
        )
        self.assertNotCalled(self.network.get_quota)
        self.assertNotCalled(self.network.get_quota_default)

    def test_quota_show_no_project(self):
        parsed_args = self.check_parser(self.cmd, [], [])

        self.cmd.take_action(parsed_args)

        self.compute_quotas_mock.get.assert_called_once_with(
            identity_fakes.project_id, detail=False
        )
        self.volume_quotas_mock.get.assert_called_once_with(
            identity_fakes.project_id,
        )
        self.network.get_quota.assert_called_once_with(
            identity_fakes.project_id, details=False
        )
        self.assertNotCalled(self.network.get_quota_default)
