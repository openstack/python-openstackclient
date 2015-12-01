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
from openstackclient.tests.compute.v2 import fakes as compute_fakes
from openstackclient.tests import fakes
from openstackclient.tests.identity.v2_0 import fakes as identity_fakes
from openstackclient.tests.network.v2 import fakes as network_fakes


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
        volume_mock = mock.Mock()
        volume_mock.quotas = mock.Mock()
        self.app.client_manager.volume = volume_mock
        self.volume_quotas_mock = volume_mock.quotas
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


class TestQuotaSet(TestQuota):

    def setUp(self):
        super(TestQuotaSet, self).setUp()

        self.quotas_mock.find.return_value = FakeQuotaResource(
            None,
            copy.deepcopy(compute_fakes.QUOTA),
            loaded=True,
        )

        self.quotas_mock.update.return_value = FakeQuotaResource(
            None,
            copy.deepcopy(compute_fakes.QUOTA),
            loaded=True,
        )

        self.volume_quotas_mock.find.return_value = FakeQuotaResource(
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
            ('project', identity_fakes.project_name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

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
        }

        self.quotas_mock.update.assert_called_with(
            identity_fakes.project_id,
            **kwargs
        )

    def test_quota_set_volume(self):
        arglist = [
            '--gigabytes', str(compute_fakes.floating_ip_num),
            '--snapshots', str(compute_fakes.fix_ip_num),
            '--volumes', str(compute_fakes.injected_file_num),
            identity_fakes.project_name,
        ]
        verifylist = [
            ('gigabytes', compute_fakes.floating_ip_num),
            ('snapshots', compute_fakes.fix_ip_num),
            ('volumes', compute_fakes.injected_file_num),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        kwargs = {
            'gigabytes': compute_fakes.floating_ip_num,
            'snapshots': compute_fakes.fix_ip_num,
            'volumes': compute_fakes.injected_file_num,
        }

        self.volume_quotas_mock.update.assert_called_with(
            identity_fakes.project_id,
            **kwargs
        )


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
            copy.deepcopy(compute_fakes.QUOTA),
            loaded=True,
        )

        self.volume_quotas_mock.defaults.return_value = FakeQuotaResource(
            None,
            copy.deepcopy(compute_fakes.QUOTA),
            loaded=True,
        )

        self.service_catalog_mock.get_endpoints.return_value = [
            fakes.FakeResource(
                None,
                copy.deepcopy(identity_fakes.ENDPOINT),
                loaded=True,
            )
        ]

        self.quotas_class_mock.get.return_value = FakeQuotaResource(
            None,
            copy.deepcopy(compute_fakes.QUOTA),
            loaded=True,
        )

        self.volume_quotas_class_mock.get.return_value = FakeQuotaResource(
            None,
            copy.deepcopy(compute_fakes.QUOTA),
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

        self.quotas_mock.get.assert_called_with(identity_fakes.project_id)

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

        self.quotas_mock.defaults.assert_called_with(identity_fakes.project_id)

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

        self.quotas_class_mock.get.assert_called_with(
            identity_fakes.project_id)
