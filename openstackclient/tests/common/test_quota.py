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
        volume_mock = mock.Mock()
        volume_mock.quotas = mock.Mock()
        self.app.client_manager.volume = volume_mock
        self.volume_quotas_mock = volume_mock.quotas
        self.volume_quotas_mock.reset_mock()


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

        self.cmd = quota.SetQuota(self.app, None)

    def test_quota_set(self):
        arglist = [
            '--floating-ips', str(compute_fakes.floating_ip_num),
            '--fixed-ips', str(compute_fakes.fix_ip_num),
            '--injected-files', str(compute_fakes.injected_file_num),
            '--key-pairs', str(compute_fakes.key_pair_num),
            compute_fakes.project_name,
        ]
        verifylist = [
            ('floating_ips', compute_fakes.floating_ip_num),
            ('fixed_ips', compute_fakes.fix_ip_num),
            ('injected_files', compute_fakes.injected_file_num),
            ('key_pairs', compute_fakes.key_pair_num),
            ('project', compute_fakes.project_name),
        ]

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)

        kwargs = {
            'floating_ips': compute_fakes.floating_ip_num,
            'fixed_ips': compute_fakes.fix_ip_num,
            'injected_files': compute_fakes.injected_file_num,
            'key_pairs': compute_fakes.key_pair_num,
        }

        self.quotas_mock.update.assert_called_with('project_test', **kwargs)

    def test_quota_set_volume(self):
        arglist = [
            '--gigabytes', str(compute_fakes.floating_ip_num),
            '--snapshots', str(compute_fakes.fix_ip_num),
            '--volumes', str(compute_fakes.injected_file_num),
            compute_fakes.project_name,
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

        self.volume_quotas_mock.update.assert_called_with('project_test',
                                                          **kwargs)
