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

from unittest import mock

from openstack.block_storage.v3 import quota_set as _volume_quota_set
from openstack.compute.v2 import quota_set as _compute_quota_set
from openstack.identity.v3 import project as _project
from openstack.network.v2 import quota as _network_quota_set
from openstack.test import fakes as sdk_fakes

from openstack import exceptions as sdk_exceptions
from openstackclient.common import quota
from openstackclient.tests.unit.compute.v2 import fakes as compute_fakes
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes
from openstackclient.tests.unit.network.v2 import fakes as network_fakes
from openstackclient.tests.unit import utils
from openstackclient.tests.unit.volume.v3 import fakes as volume_fakes


class TestQuota(
    identity_fakes.FakeClientMixin,
    compute_fakes.FakeClientMixin,
    network_fakes.FakeClientMixin,
    volume_fakes.FakeClientMixin,
    utils.TestCommand,
):
    def setUp(self):
        super().setUp()

        self.projects = list(
            sdk_fakes.generate_fake_resources(_project.Project, count=2)
        )
        self.app.client_manager.auth_ref = mock.Mock()
        self.app.client_manager.auth_ref.project_id = self.projects[1].id


class TestQuotaList(TestQuota):
    """Test cases for quota list command"""

    compute_column_header = (
        'Project ID',
        'Cores',
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
        'Subnet Pools',
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
        super().setUp()

        self.identity_sdk_client.get_project.side_effect = self.projects[0]
        self.identity_sdk_client.projects.return_value = self.projects

        self.compute_quotas = [
            sdk_fakes.generate_fake_resource(_compute_quota_set.QuotaSet),
            sdk_fakes.generate_fake_resource(_compute_quota_set.QuotaSet),
        ]
        self.default_compute_quotas = sdk_fakes.generate_fake_resource(
            _compute_quota_set.QuotaSet
        )
        # the defaults are global hence use of return_value here
        self.compute_client.get_quota_set_defaults.return_value = (
            self.default_compute_quotas
        )
        self.compute_reference_data = (
            self.projects[0].id,
            self.compute_quotas[0].cores,
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
            sdk_fakes.generate_fake_resource(_network_quota_set.Quota),
            sdk_fakes.generate_fake_resource(_network_quota_set.Quota),
        ]
        self.default_network_quotas = sdk_fakes.generate_fake_resource(
            _network_quota_set.QuotaDefault
        )
        # the defaults are global hence use of return_value here
        self.network_client.get_quota_default.return_value = (
            self.default_network_quotas
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
            sdk_fakes.generate_fake_resource(_volume_quota_set.QuotaSet),
            sdk_fakes.generate_fake_resource(_volume_quota_set.QuotaSet),
        ]
        self.default_volume_quotas = sdk_fakes.generate_fake_resource(
            _volume_quota_set.QuotaSet
        )
        # the defaults are global hence use of return_value here
        self.volume_sdk_client.get_quota_set_defaults.return_value = (
            self.default_volume_quotas
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

    def test_quota_list_compute(self):
        # Two projects with non-default quotas
        self.compute_client.get_quota_set.side_effect = self.compute_quotas

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
        self.compute_client.get_quota_set.side_effect = [
            self.compute_quotas[0],
            self.default_compute_quotas,
        ]

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

    def test_quota_list_compute_project_not_found(self):
        # Make one of the projects disappear
        self.compute_client.get_quota_set.side_effect = [
            self.compute_quotas[0],
            sdk_exceptions.NotFoundException("NotFound"),
        ]

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

    def test_quota_list_compute_project_inaccessible(self):
        # Make one of the projects inaccessible
        self.compute_client.get_quota_set.side_effect = [
            self.compute_quotas[0],
            sdk_exceptions.ForbiddenException("Forbidden"),
        ]

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

    def test_quota_list_compute_server_error(self):
        # Make the server "break"
        self.compute_client.get_quota_set.side_effect = (
            sdk_exceptions.HttpException("Not implemented?")
        )

        arglist = [
            '--compute',
        ]
        verifylist = [
            ('compute', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(
            sdk_exceptions.HttpException,
            self.cmd.take_action,
            parsed_args,
        )

    def test_quota_list_network(self):
        # Two projects with non-default quotas
        self.network_client.get_quota.side_effect = self.network_quotas

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
        self.network_client.get_quota.side_effect = [
            self.network_quotas[0],
            self.default_network_quotas,
        ]

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
        self.network_client.get_quota.side_effect = [
            self.network_quotas[0],
            sdk_exceptions.NotFoundException("NotFound"),
        ]

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
        self.volume_sdk_client.get_quota_set.side_effect = self.volume_quotas

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
        self.volume_sdk_client.get_quota_set.side_effect = [
            self.volume_quotas[0],
            self.default_volume_quotas,
        ]

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
        super().setUp()

        self.identity_sdk_client.find_project.return_value = self.projects[0]

        self.cmd = quota.SetQuota(self.app, None)

    def test_quota_set(self):
        floating_ip_num = 100
        fix_ip_num = 100
        injected_file_num = 100
        injected_file_size_num = 10240
        injected_path_size_num = 255
        key_pair_num = 100
        core_num = 20
        ram_num = 51200
        instance_num = 10
        property_num = 128
        secgroup_rule_num = 20
        secgroup_num = 10
        servgroup_num = 10
        servgroup_members_num = 10

        arglist = [
            '--floating-ips',
            str(floating_ip_num),
            '--fixed-ips',
            str(fix_ip_num),
            '--injected-files',
            str(injected_file_num),
            '--injected-file-size',
            str(injected_file_size_num),
            '--injected-path-size',
            str(injected_path_size_num),
            '--key-pairs',
            str(key_pair_num),
            '--cores',
            str(core_num),
            '--ram',
            str(ram_num),
            '--instances',
            str(instance_num),
            '--properties',
            str(property_num),
            '--secgroup-rules',
            str(secgroup_rule_num),
            '--secgroups',
            str(secgroup_num),
            '--server-groups',
            str(servgroup_num),
            '--server-group-members',
            str(servgroup_members_num),
            self.projects[0].name,
        ]
        verifylist = [
            ('floating_ips', floating_ip_num),
            ('fixed_ips', fix_ip_num),
            ('injected_files', injected_file_num),
            (
                'injected_file_content_bytes',
                injected_file_size_num,
            ),
            ('injected_file_path_bytes', injected_path_size_num),
            ('key_pairs', key_pair_num),
            ('cores', core_num),
            ('ram', ram_num),
            ('instances', instance_num),
            ('metadata_items', property_num),
            ('security_group_rules', secgroup_rule_num),
            ('security_groups', secgroup_num),
            ('server_groups', servgroup_num),
            ('server_group_members', servgroup_members_num),
            ('force', False),
            ('project', self.projects[0].name),
        ]
        self.app.client_manager.network_endpoint_enabled = False
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        kwargs = {
            'floating_ips': floating_ip_num,
            'fixed_ips': fix_ip_num,
            'injected_files': injected_file_num,
            'injected_file_content_bytes': injected_file_size_num,  # noqa: E501
            'injected_file_path_bytes': injected_path_size_num,
            'key_pairs': key_pair_num,
            'cores': core_num,
            'ram': ram_num,
            'instances': instance_num,
            'metadata_items': property_num,
            'security_group_rules': secgroup_rule_num,
            'security_groups': secgroup_num,
            'server_groups': servgroup_num,
            'server_group_members': servgroup_members_num,
        }

        self.compute_client.update_quota_set.assert_called_once_with(
            self.projects[0].id, **kwargs
        )
        self.assertIsNone(result)

    def test_quota_set_volume(self):
        gigabytes = 1000
        volumes = 11
        snapshots = 10
        backups = 10
        backup_gigabytes = 1000
        per_volume_gigabytes = -1

        arglist = [
            '--gigabytes',
            str(gigabytes),
            '--snapshots',
            str(snapshots),
            '--volumes',
            str(volumes),
            '--backups',
            str(backups),
            '--backup-gigabytes',
            str(backup_gigabytes),
            '--per-volume-gigabytes',
            str(per_volume_gigabytes),
            self.projects[0].name,
        ]
        verifylist = [
            ('gigabytes', gigabytes),
            ('snapshots', snapshots),
            ('volumes', volumes),
            ('backups', backups),
            ('backup_gigabytes', backup_gigabytes),
            (
                'per_volume_gigabytes',
                per_volume_gigabytes,
            ),
            ('project', self.projects[0].name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        kwargs = {
            'gigabytes': gigabytes,
            'snapshots': snapshots,
            'volumes': volumes,
            'backups': backups,
            'backup_gigabytes': backup_gigabytes,
            'per_volume_gigabytes': per_volume_gigabytes,
        }

        self.volume_sdk_client.update_quota_set.assert_called_once_with(
            self.projects[0].id, **kwargs
        )

        self.assertIsNone(result)

    def test_quota_set_volume_with_volume_type(self):
        gigabytes = 1000
        volumes = 11
        snapshots = 10
        backups = 10
        backup_gigabytes = 1000
        per_volume_gigabytes = -1

        arglist = [
            '--gigabytes',
            str(gigabytes),
            '--snapshots',
            str(snapshots),
            '--volumes',
            str(volumes),
            '--backups',
            str(backups),
            '--backup-gigabytes',
            str(backup_gigabytes),
            '--per-volume-gigabytes',
            str(per_volume_gigabytes),
            '--volume-type',
            'volume_type_backend',
            self.projects[0].name,
        ]
        verifylist = [
            ('gigabytes', gigabytes),
            ('snapshots', snapshots),
            ('volumes', volumes),
            ('backups', backups),
            ('backup_gigabytes', backup_gigabytes),
            (
                'per_volume_gigabytes',
                per_volume_gigabytes,
            ),
            ('volume_type', 'volume_type_backend'),
            ('project', self.projects[0].name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        kwargs = {
            'gigabytes_volume_type_backend': gigabytes,
            'snapshots_volume_type_backend': snapshots,
            'volumes_volume_type_backend': volumes,
            'backups': backups,
            'backup_gigabytes': backup_gigabytes,
            'per_volume_gigabytes': per_volume_gigabytes,
        }

        self.volume_sdk_client.update_quota_set.assert_called_once_with(
            self.projects[0].id, **kwargs
        )
        self.assertIsNone(result)

    def test_quota_set_network(self):
        subnet = 10
        network = 10
        floatingip = 50
        subnetpool = -1
        security_group_rule = 100
        security_group = 10
        router = 10
        rbac_policy = -1
        port = 50

        arglist = [
            '--subnets',
            str(subnet),
            '--networks',
            str(network),
            '--floating-ips',
            str(floatingip),
            '--subnetpools',
            str(subnetpool),
            '--secgroup-rules',
            str(security_group_rule),
            '--secgroups',
            str(security_group),
            '--routers',
            str(router),
            '--rbac-policies',
            str(rbac_policy),
            '--ports',
            str(port),
            self.projects[0].name,
        ]
        verifylist = [
            ('subnet', subnet),
            ('network', network),
            ('floatingip', floatingip),
            ('subnetpool', subnetpool),
            (
                'security_group_rule',
                security_group_rule,
            ),
            ('security_group', security_group),
            ('router', router),
            ('rbac_policy', rbac_policy),
            ('port', port),
            ('force', False),
            ('project', self.projects[0].name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)
        kwargs = {
            'check_limit': True,
            'subnet': subnet,
            'network': network,
            'floatingip': floatingip,
            'subnetpool': subnetpool,
            'security_group_rule': security_group_rule,
            'security_group': security_group,
            'router': router,
            'rbac_policy': rbac_policy,
            'port': port,
        }
        self.network_client.update_quota.assert_called_once_with(
            self.projects[0].id, **kwargs
        )
        self.assertIsNone(result)

    def test_quota_set_with_class(self):
        floating_ip_num = 100
        fix_ip_num = 100
        injected_file_num = 100
        injected_file_size_num = 10240
        injected_path_size_num = 255
        key_pair_num = 100
        core_num = 20
        ram_num = 51200
        instance_num = 10
        property_num = 128
        servgroup_num = 10
        servgroup_members_num = 10
        volumes = 11
        network = 10

        arglist = [
            '--injected-files',
            str(injected_file_num),
            '--injected-file-size',
            str(injected_file_size_num),
            '--injected-path-size',
            str(injected_path_size_num),
            '--key-pairs',
            str(key_pair_num),
            '--cores',
            str(core_num),
            '--ram',
            str(ram_num),
            '--instances',
            str(instance_num),
            '--properties',
            str(property_num),
            '--server-groups',
            str(servgroup_num),
            '--server-group-members',
            str(servgroup_members_num),
            '--gigabytes',
            str(floating_ip_num),
            '--snapshots',
            str(fix_ip_num),
            '--volumes',
            str(volumes),
            '--network',
            str(network),
            '--class',
            self.projects[0].name,
        ]
        verifylist = [
            ('injected_files', injected_file_num),
            (
                'injected_file_content_bytes',
                injected_file_size_num,
            ),
            ('injected_file_path_bytes', injected_path_size_num),
            ('key_pairs', key_pair_num),
            ('cores', core_num),
            ('ram', ram_num),
            ('instances', instance_num),
            ('metadata_items', property_num),
            ('server_groups', servgroup_num),
            ('server_group_members', servgroup_members_num),
            ('gigabytes', floating_ip_num),
            ('snapshots', fix_ip_num),
            ('volumes', volumes),
            ('network', network),
            ('quota_class', True),
            ('project', self.projects[0].name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        kwargs_compute = {
            'injected_files': injected_file_num,
            'injected_file_content_bytes': injected_file_size_num,  # noqa: E501
            'injected_file_path_bytes': injected_path_size_num,
            'key_pairs': key_pair_num,
            'cores': core_num,
            'ram': ram_num,
            'instances': instance_num,
            'metadata_items': property_num,
            'server_groups': servgroup_num,
            'server_group_members': servgroup_members_num,
        }
        kwargs_volume = {
            'gigabytes': floating_ip_num,
            'snapshots': fix_ip_num,
            'volumes': volumes,
        }

        self.compute_client.update_quota_class_set.assert_called_with(
            self.projects[0].name, **kwargs_compute
        )
        self.volume_sdk_client.update_quota_class_set.assert_called_with(
            self.projects[0].name, **kwargs_volume
        )
        self.assertNotCalled(self.network_client.update_quota)
        self.assertIsNone(result)

    def test_quota_set_default(self):
        floating_ip_num = 100
        fix_ip_num = 100
        injected_file_num = 100
        injected_file_size_num = 10240
        injected_path_size_num = 255
        key_pair_num = 100
        core_num = 20
        ram_num = 51200
        instance_num = 10
        property_num = 128
        servgroup_num = 10
        servgroup_members_num = 10
        volumes = 11
        network = 10

        arglist = [
            '--injected-files',
            str(injected_file_num),
            '--injected-file-size',
            str(injected_file_size_num),
            '--injected-path-size',
            str(injected_path_size_num),
            '--key-pairs',
            str(key_pair_num),
            '--cores',
            str(core_num),
            '--ram',
            str(ram_num),
            '--instances',
            str(instance_num),
            '--properties',
            str(property_num),
            '--server-groups',
            str(servgroup_num),
            '--server-group-members',
            str(servgroup_members_num),
            '--gigabytes',
            str(floating_ip_num),
            '--snapshots',
            str(fix_ip_num),
            '--volumes',
            str(volumes),
            '--network',
            str(network),
            '--default',
        ]
        verifylist = [
            ('injected_files', injected_file_num),
            (
                'injected_file_content_bytes',
                injected_file_size_num,
            ),
            ('injected_file_path_bytes', injected_path_size_num),
            ('key_pairs', key_pair_num),
            ('cores', core_num),
            ('ram', ram_num),
            ('instances', instance_num),
            ('metadata_items', property_num),
            ('server_groups', servgroup_num),
            ('server_group_members', servgroup_members_num),
            ('gigabytes', floating_ip_num),
            ('snapshots', fix_ip_num),
            ('volumes', volumes),
            ('network', network),
            ('default', True),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        kwargs_compute = {
            'injected_files': injected_file_num,
            'injected_file_content_bytes': injected_file_size_num,  # noqa: E501
            'injected_file_path_bytes': injected_path_size_num,
            'key_pairs': key_pair_num,
            'cores': core_num,
            'ram': ram_num,
            'instances': instance_num,
            'metadata_items': property_num,
            'server_groups': servgroup_num,
            'server_group_members': servgroup_members_num,
        }
        kwargs_volume = {
            'gigabytes': floating_ip_num,
            'snapshots': fix_ip_num,
            'volumes': volumes,
        }

        self.compute_client.update_quota_class_set.assert_called_with(
            'default', **kwargs_compute
        )
        self.volume_sdk_client.update_quota_class_set.assert_called_with(
            'default', **kwargs_volume
        )
        self.assertNotCalled(self.network_client.update_quota)
        self.assertIsNone(result)

    def test_quota_set_with_force(self):
        core_num = 20
        ram_num = 51200
        instance_num = 10
        volumes = 11
        subnet = 10

        arglist = [
            '--cores',
            str(core_num),
            '--ram',
            str(ram_num),
            '--instances',
            str(instance_num),
            '--volumes',
            str(volumes),
            '--subnets',
            str(subnet),
            '--force',
            self.projects[0].name,
        ]
        verifylist = [
            ('cores', core_num),
            ('ram', ram_num),
            ('instances', instance_num),
            ('volumes', volumes),
            ('subnet', subnet),
            ('force', True),
            ('project', self.projects[0].name),
        ]
        self.app.client_manager.network_endpoint_enabled = True
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        kwargs_compute = {
            'cores': core_num,
            'ram': ram_num,
            'instances': instance_num,
            'force': True,
        }
        kwargs_volume = {
            'volumes': volumes,
        }
        kwargs_network = {
            'subnet': subnet,
            'force': True,
        }
        self.compute_client.update_quota_set.assert_called_once_with(
            self.projects[0].id, **kwargs_compute
        )
        self.volume_sdk_client.update_quota_set.assert_called_once_with(
            self.projects[0].id, **kwargs_volume
        )
        self.network_client.update_quota.assert_called_once_with(
            self.projects[0].id, **kwargs_network
        )
        self.assertIsNone(result)

    def test_quota_set_with_no_force(self):
        arglist = [
            '--subnets',
            str(10),
            '--volumes',
            str(30),
            '--cores',
            str(20),
            '--no-force',
            self.projects[0].name,
        ]
        verifylist = [
            ('subnet', 10),
            ('volumes', 30),
            ('cores', 20),
            ('force', False),
            ('project', self.projects[0].name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        kwargs_compute = {
            'cores': 20,
        }
        kwargs_volume = {
            'volumes': 30,
        }
        kwargs_network = {
            'subnet': 10,
            'check_limit': True,
        }
        self.compute_client.update_quota_set.assert_called_once_with(
            self.projects[0].id, **kwargs_compute
        )
        self.volume_sdk_client.update_quota_set.assert_called_once_with(
            self.projects[0].id, **kwargs_volume
        )
        self.network_client.update_quota.assert_called_once_with(
            self.projects[0].id, **kwargs_network
        )
        self.assertIsNone(result)


class TestQuotaShow(TestQuota):
    _network_quota_details = {
        'floating_ips': {'limit': 0, 'reserved': 0, 'used': 0},
        'health_monitors': {'limit': 0, 'reserved': 0, 'used': 0},
        'l7_policies': {'limit': 0, 'reserved': 0, 'used': 0},
        'listeners': {'limit': 0, 'reserved': 0, 'used': 0},
        'load_balancers': {'limit': 0, 'reserved': 0, 'used': 0},
        'networks': {'limit': 0, 'reserved': 0, 'used': 0},
        'pools': {'limit': 0, 'reserved': 0, 'used': 0},
        'ports': {'limit': 0, 'reserved': 0, 'used': 0},
        'rbac_policies': {'limit': 0, 'reserved': 0, 'used': 0},
        'routers': {'limit': 0, 'reserved': 0, 'used': 0},
        'security_group_rules': {'limit': 0, 'reserved': 0, 'used': 0},
        'security_groups': {'limit': 0, 'reserved': 0, 'used': 0},
        'subnet_pools': {'limit': 0, 'reserved': 0, 'used': 0},
        'subnets': {'limit': 0, 'reserved': 0, 'used': 0},
    }

    def setUp(self):
        super().setUp()

        self.identity_sdk_client.find_project.return_value = self.projects[0]

        self.compute_client.get_quota_set.return_value = (
            sdk_fakes.generate_fake_resource(_compute_quota_set.QuotaSet)
        )
        self.default_compute_quotas = sdk_fakes.generate_fake_resource(
            _compute_quota_set.QuotaSet
        )
        self.compute_client.get_quota_set_defaults.return_value = (
            self.default_compute_quotas
        )

        self.volume_sdk_client.get_quota_set.return_value = (
            sdk_fakes.generate_fake_resource(_volume_quota_set.QuotaSet)
        )
        self.default_volume_quotas = sdk_fakes.generate_fake_resource(
            _volume_quota_set.QuotaSet
        )
        self.volume_sdk_client.get_quota_set_defaults.return_value = (
            self.default_volume_quotas
        )

        def get_network_quota_mock(*args, **kwargs):
            if kwargs.get("details"):
                return sdk_fakes.generate_fake_resource(
                    _network_quota_set.QuotaDetails,
                    **self._network_quota_details,
                )
            return sdk_fakes.generate_fake_resource(_network_quota_set.Quota)

        self.network_client.get_quota.side_effect = get_network_quota_mock
        self.default_network_quotas = sdk_fakes.generate_fake_resource(
            _network_quota_set.QuotaDefault
        )
        self.network_client.get_quota_default.return_value = (
            self.default_network_quotas
        )

        self.cmd = quota.ShowQuota(self.app, None)

    def test_quota_show(self):
        arglist = [
            self.projects[0].name,
        ]
        verifylist = [
            ('service', 'all'),
            ('project', self.projects[0].name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.compute_client.get_quota_set.assert_called_once_with(
            self.projects[0].id,
            usage=False,
        )
        self.volume_sdk_client.get_quota_set.assert_called_once_with(
            self.projects[0].id,
            usage=False,
        )
        self.network_client.get_quota.assert_called_once_with(
            self.projects[0].id,
            details=False,
        )
        self.assertNotCalled(self.network_client.get_quota_default)

    def test_quota_show__with_compute(self):
        arglist = [
            '--compute',
            self.projects[0].name,
        ]
        verifylist = [
            ('service', 'compute'),
            ('project', self.projects[0].name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.compute_client.get_quota_set.assert_called_once_with(
            self.projects[0].id,
            usage=False,
        )
        self.volume_sdk_client.get_quota_set.assert_not_called()
        self.network_client.get_quota.assert_not_called()

    def test_quota_show__with_volume(self):
        arglist = [
            '--volume',
            self.projects[0].name,
        ]
        verifylist = [
            ('service', 'volume'),
            ('project', self.projects[0].name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.compute_client.get_quota_set.assert_not_called()
        self.volume_sdk_client.get_quota_set.assert_called_once_with(
            self.projects[0].id,
            usage=False,
        )
        self.network_client.get_quota.assert_not_called()

    def test_quota_show__with_network(self):
        arglist = [
            '--network',
            self.projects[0].name,
        ]
        verifylist = [
            ('service', 'network'),
            ('project', self.projects[0].name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.compute_client.get_quota_set.assert_not_called()
        self.volume_sdk_client.get_quota_set.assert_not_called()
        self.network_client.get_quota.assert_called_once_with(
            self.projects[0].id,
            details=False,
        )
        self.assertNotCalled(self.network_client.get_quota_default)

    def test_quota_show__with_default(self):
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

        self.compute_client.get_quota_set_defaults.assert_called_once_with(
            self.projects[0].id,
        )
        self.volume_sdk_client.get_quota_set_defaults.assert_called_once_with(
            self.projects[0].id,
        )
        self.network_client.get_quota_default.assert_called_once_with(
            self.projects[0].id,
        )
        self.assertNotCalled(self.network_client.get_quota)

    def test_quota_show__with_usage(self):
        arglist = [
            '--usage',
            self.projects[0].name,
        ]
        verifylist = [
            ('usage', True),
            ('project', self.projects[0].name),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.compute_client.get_quota_set.assert_called_once_with(
            self.projects[0].id,
            usage=True,
        )
        self.volume_sdk_client.get_quota_set.assert_called_once_with(
            self.projects[0].id,
            usage=True,
        )
        self.network_client.get_quota.assert_called_once_with(
            self.projects[0].id,
            details=True,
        )

    def test_quota_show__no_project(self):
        arglist = []
        verifylist = [
            ('project', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        self.compute_client.get_quota_set.assert_called_once_with(
            self.projects[1].id, usage=False
        )
        self.volume_sdk_client.get_quota_set.assert_called_once_with(
            self.projects[1].id, usage=False
        )
        self.network_client.get_quota.assert_called_once_with(
            self.projects[1].id, details=False
        )
        self.assertNotCalled(self.network_client.get_quota_default)


class TestQuotaDelete(TestQuota):
    """Test cases for quota delete command"""

    def setUp(self):
        super().setUp()

        self.identity_sdk_client.find_project.return_value = self.projects[0]

        self.compute_client.revert_quota_set.return_value = None
        self.volume_sdk_client.revert_quota_set.return_value = None
        self.network_client.delete_quota.return_value = None

        self.cmd = quota.DeleteQuota(self.app, None)

    def test_delete(self):
        """Delete all quotas"""
        arglist = [
            self.projects[0].id,
        ]
        verifylist = [
            ('service', 'all'),
            ('project', self.projects[0].id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)
        self.identity_sdk_client.find_project.assert_called_once_with(
            self.projects[0].id, ignore_missing=False
        )
        self.compute_client.revert_quota_set.assert_called_once_with(
            self.projects[0].id,
        )
        self.volume_sdk_client.revert_quota_set.assert_called_once_with(
            self.projects[0].id,
        )
        self.network_client.delete_quota.assert_called_once_with(
            self.projects[0].id,
        )

    def test_delete__compute(self):
        """Delete compute quotas only"""
        arglist = [
            '--compute',
            self.projects[0].id,
        ]
        verifylist = [
            ('service', 'compute'),
            ('project', self.projects[0].id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)
        self.identity_sdk_client.find_project.assert_called_once_with(
            self.projects[0].id, ignore_missing=False
        )
        self.compute_client.revert_quota_set.assert_called_once_with(
            self.projects[0].id,
        )
        self.volume_sdk_client.revert_quota_set.assert_not_called()
        self.network_client.delete_quota.assert_not_called()

    def test_delete__volume(self):
        """Delete volume quotas only"""
        arglist = [
            '--volume',
            self.projects[0].id,
        ]
        verifylist = [
            ('service', 'volume'),
            ('project', self.projects[0].id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)
        self.identity_sdk_client.find_project.assert_called_once_with(
            self.projects[0].id, ignore_missing=False
        )
        self.compute_client.revert_quota_set.assert_not_called()
        self.volume_sdk_client.revert_quota_set.assert_called_once_with(
            self.projects[0].id,
        )
        self.network_client.delete_quota.assert_not_called()

    def test_delete__network(self):
        """Delete network quotas only"""
        arglist = [
            '--network',
            self.projects[0].id,
        ]
        verifylist = [
            ('service', 'network'),
            ('project', self.projects[0].id),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.assertIsNone(result)
        self.identity_sdk_client.find_project.assert_called_once_with(
            self.projects[0].id, ignore_missing=False
        )
        self.compute_client.revert_quota_set.assert_not_called()
        self.volume_sdk_client.revert_quota_set.assert_not_called()
        self.network_client.delete_quota.assert_called_once_with(
            self.projects[0].id,
        )
