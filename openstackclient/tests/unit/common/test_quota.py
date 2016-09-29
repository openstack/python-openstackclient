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

from openstack.network.v2 import quota as _quota

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
        self.quotas_mock = self.app.client_manager.compute.quotas
        self.quotas_mock.reset_mock()
        self.quotas_class_mock = self.app.client_manager.compute.quota_classes
        self.quotas_class_mock.reset_mock()
        self.volume_quotas_mock = self.app.client_manager.volume.quotas
        self.volume_quotas_mock.reset_mock()
        self.volume_quotas_class_mock = \
            self.app.client_manager.volume.quota_classes
        self.volume_quotas_class_mock.reset_mock()
        self.projects_mock = self.app.client_manager.identity.projects
        self.projects_mock.reset_mock()
        self.app.client_manager.auth_ref = mock.Mock()
        self.app.client_manager.auth_ref.service_catalog = mock.Mock()
        self.service_catalog_mock = \
            self.app.client_manager.auth_ref.service_catalog
        self.service_catalog_mock.reset_mock()
        self.app.client_manager.auth_ref.project_id = identity_fakes.project_id


class TestQuotaSet(TestQuota):

    def setUp(self):
        super(TestQuotaSet, self).setUp()

        self.quotas_mock.update.return_value = FakeQuotaResource(
            None,
            copy.deepcopy(compute_fakes.QUOTA),
            loaded=True,
        )

        self.volume_quotas_mock.update.return_value = FakeQuotaResource(
            None,
            copy.deepcopy(compute_fakes.QUOTA),
            loaded=True,
        )

        self.projects_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.PROJECT),
            loaded=True,
        )

        self.quotas_class_mock.update.return_value = FakeQuotaResource(
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
            identity_fakes.project_name,
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
            ('project', identity_fakes.project_name),
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

        self.quotas_mock.update.assert_called_once_with(
            identity_fakes.project_id,
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
            identity_fakes.project_name,
        ]
        verifylist = [
            ('gigabytes', volume_fakes.QUOTA['gigabytes']),
            ('snapshots', volume_fakes.QUOTA['snapshots']),
            ('volumes', volume_fakes.QUOTA['volumes']),
            ('backups', volume_fakes.QUOTA['backups']),
            ('backup_gigabytes', volume_fakes.QUOTA['backup_gigabytes']),
            ('per_volume_gigabytes',
             volume_fakes.QUOTA['per_volume_gigabytes']),
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
            identity_fakes.project_id,
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
            identity_fakes.project_name,
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
            identity_fakes.project_id,
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
            '--vips', str(network_fakes.QUOTA['vip']),
            '--health-monitors', str(network_fakes.QUOTA['healthmonitor']),
            '--l7policies', str(network_fakes.QUOTA['l7policy']),
            identity_fakes.project_name,
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
            ('vip', network_fakes.QUOTA['vip']),
            ('healthmonitor', network_fakes.QUOTA['healthmonitor']),
            ('l7policy', network_fakes.QUOTA['l7policy']),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # TODO(huanxuan): Remove this if condition once the fixed
        # SDK Quota class is the minimum required version.
        # This is expected to be SDK release 0.9.13
        if not hasattr(_quota.Quota, 'allow_get'):
            # Just run this when sdk <= 0.9.10
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
                'vip': network_fakes.QUOTA['vip'],
                'healthmonitor': network_fakes.QUOTA['healthmonitor'],
                'l7policy': network_fakes.QUOTA['l7policy'],
            }
            self.network_mock.update_quota.assert_called_once_with(
                identity_fakes.project_id,
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
            '--class', identity_fakes.project_name,
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
            ('project', identity_fakes.project_name),
            ('quota_class', True),
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

        self.quotas_class_mock.update.assert_called_with(
            identity_fakes.project_name,
            **kwargs_compute
        )
        self.volume_quotas_class_mock.update.assert_called_with(
            identity_fakes.project_name,
            **kwargs_volume
        )
        self.assertNotCalled(self.network_mock.update_quota)
        self.assertIsNone(result)


class TestQuotaShow(TestQuota):

    def setUp(self):
        super(TestQuotaShow, self).setUp()

        self.quotas_mock.get.return_value = FakeQuotaResource(
            None,
            copy.deepcopy(compute_fakes.QUOTA),
            loaded=True,
        )

        self.quotas_mock.defaults.return_value = FakeQuotaResource(
            None,
            copy.deepcopy(compute_fakes.QUOTA),
            loaded=True,
        )

        self.volume_quotas_mock.get.return_value = FakeQuotaResource(
            None,
            copy.deepcopy(volume_fakes.QUOTA),
            loaded=True,
        )

        self.volume_quotas_mock.defaults.return_value = FakeQuotaResource(
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

        self.quotas_class_mock.get.return_value = FakeQuotaResource(
            None,
            copy.deepcopy(compute_fakes.QUOTA),
            loaded=True,
        )

        self.volume_quotas_class_mock.get.return_value = FakeQuotaResource(
            None,
            copy.deepcopy(volume_fakes.QUOTA),
            loaded=True,
        )

        self.projects_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.PROJECT),
            loaded=True,
        )

        self.app.client_manager.network = network_fakes.FakeNetworkV2Client(
            endpoint=fakes.AUTH_URL,
            token=fakes.AUTH_TOKEN,
        )
        self.network = self.app.client_manager.network
        self.network.get_quota = mock.Mock(return_value=network_fakes.QUOTA)
        self.network.get_quota_default = mock.Mock(
            return_value=network_fakes.QUOTA)

        self.cmd = quota.ShowQuota(self.app, None)

    def test_quota_show(self):
        arglist = [
            identity_fakes.project_name,
        ]
        verifylist = [
            ('project', identity_fakes.project_name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.quotas_mock.get.assert_called_once_with(identity_fakes.project_id)
        self.volume_quotas_mock.get.assert_called_once_with(
            identity_fakes.project_id)
        self.network.get_quota.assert_called_once_with(
            identity_fakes.project_id)
        self.assertNotCalled(self.network.get_quota_default)

    def test_quota_show_with_default(self):
        arglist = [
            '--default',
            identity_fakes.project_name,
        ]
        verifylist = [
            ('default', True),
            ('project', identity_fakes.project_name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        # TODO(huanxuan): Remove this if condition once the fixed
        # SDK QuotaDefault class is the minimum required version.
        # This is expected to be SDK release 0.9.13
        if not hasattr(_quota.QuotaDefault, 'project'):
            # Just run this when sdk <= 0.9.10
            self.cmd.take_action(parsed_args)

            self.quotas_mock.defaults.assert_called_once_with(
                identity_fakes.project_id)
            self.volume_quotas_mock.defaults.assert_called_once_with(
                identity_fakes.project_id)
            self.network.get_quota_default.assert_called_once_with(
                identity_fakes.project_id)
            self.assertNotCalled(self.network.get_quota)

    def test_quota_show_with_class(self):
        arglist = [
            '--class',
            identity_fakes.project_name,
        ]
        verifylist = [
            ('quota_class', True),
            ('project', identity_fakes.project_name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.quotas_class_mock.get.assert_called_once_with(
            identity_fakes.project_name)
        self.volume_quotas_class_mock.get.assert_called_once_with(
            identity_fakes.project_name)
        self.assertNotCalled(self.network.get_quota)
        self.assertNotCalled(self.network.get_quota_default)

    def test_quota_show_no_project(self):
        parsed_args = self.check_parser(self.cmd, [], [])

        self.cmd.take_action(parsed_args)

        self.quotas_mock.get.assert_called_once_with(identity_fakes.project_id)
        self.volume_quotas_mock.get.assert_called_once_with(
            identity_fakes.project_id)
        self.network.get_quota.assert_called_once_with(
            identity_fakes.project_id)
        self.assertNotCalled(self.network.get_quota_default)


class TestQuotaList(TestQuota):
    """Test cases for quota list command"""

    project = identity_fakes_v3.FakeProject.create_one_project()

    quota_list = network_fakes.FakeQuota.create_one_net_quota()
    quota_list1 = compute_fakes.FakeQuota.create_one_comp_quota()
    quota_list2 = volume_fakes.FakeQuota.create_one_vol_quota()

    default_quota = network_fakes.FakeQuota.create_one_default_net_quota()
    default_quota1 = compute_fakes.FakeQuota.create_one_default_comp_quota()
    default_quota2 = volume_fakes.FakeQuota.create_one_default_vol_quota()

    reference_data = (project.id,
                      quota_list.floating_ips,
                      quota_list.networks,
                      quota_list.ports,
                      quota_list.rbac_policies,
                      quota_list.routers,
                      quota_list.security_groups,
                      quota_list.security_group_rules,
                      quota_list.subnets,
                      quota_list.subnet_pools)

    comp_reference_data = (project.id,
                           quota_list1.cores,
                           quota_list1.fixed_ips,
                           quota_list1.injected_files,
                           quota_list1.injected_file_content_bytes,
                           quota_list1.injected_file_path_bytes,
                           quota_list1.instances,
                           quota_list1.key_pairs,
                           quota_list1.metadata_items,
                           quota_list1.ram,
                           quota_list1.server_groups,
                           quota_list1.server_group_members)

    vol_reference_data = (project.id,
                          quota_list2.backups,
                          quota_list2.backup_gigabytes,
                          quota_list2.gigabytes,
                          quota_list2.per_volume_gigabytes,
                          quota_list2.snapshots,
                          quota_list2.volumes)

    net_column_header = (
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

    comp_column_header = (
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

    vol_column_header = (
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

        self.projects_mock.get.return_value = fakes.FakeResource(
            None,
            copy.deepcopy(identity_fakes.PROJECT),
            loaded=True,
        )

        self.identity = self.app.client_manager.identity
        self.identity.tenants.list = mock.Mock(return_value=[self.project])

        self.network = self.app.client_manager.network
        self.compute = self.app.client_manager.compute
        self.volume = self.app.client_manager.volume

        self.network.get_quota = mock.Mock(return_value=self.quota_list)
        self.compute.quotas.get = mock.Mock(return_value=self.quota_list1)
        self.volume.quotas.get = mock.Mock(return_value=self.quota_list2)

        self.network.get_quota_default = mock.Mock(
            return_value=self.default_quota)
        self.compute.quotas.defaults = mock.Mock(
            return_value=self.default_quota1)
        self.volume.quotas.defaults = mock.Mock(
            return_value=self.default_quota2)

        self.cmd = quota.ListQuota(self.app, None)

    def test_quota_list_network(self):
        arglist = [
            '--network'
        ]
        verifylist = [
            ('network', True)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(self.net_column_header, columns)

        self.assertEqual(self.reference_data, list(data)[0])

    def test_quota_list_compute(self):
        arglist = [
            '--compute'
        ]
        verifylist = [
            ('compute', True)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(self.comp_column_header, columns)

        self.assertEqual(self.comp_reference_data, list(data)[0])

    def test_quota_list_volume(self):
        arglist = [
            '--volume'
        ]
        verifylist = [
            ('volume', True)
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(self.vol_column_header, columns)

        self.assertEqual(self.vol_reference_data, list(data)[0])
