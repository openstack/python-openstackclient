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

from openstackclient.common import quota
from openstackclient.tests.unit.compute.v2 import fakes as compute_fakes
from openstackclient.tests.unit import fakes
from openstackclient.tests.unit.identity.v2_0 import fakes as identity_fakes
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
