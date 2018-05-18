#   Copyright 2017 Huawei, Inc. All rights reserved.
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

import json

from openstackclient.tests.functional import base


class ModuleTest(base.TestCase):
    """Functional tests for openstackclient module list output."""

    CLIENTS = ['openstackclient',
               'keystoneclient',
               'novaclient',
               'openstack']

    LIBS = ['osc_lib',
            'keystoneauth1']

    def test_module_list(self):
        # Test module list
        cmd_output = json.loads(self.openstack('module list -f json'))
        for one_module in self.CLIENTS:
            self.assertIn(one_module, cmd_output.keys())
        for one_module in self.LIBS:
            self.assertNotIn(one_module, cmd_output.keys())

        # Test module list --all
        cmd_output = json.loads(self.openstack('module list --all -f json'))
        for one_module in self.CLIENTS + self.LIBS:
            self.assertIn(one_module, cmd_output.keys())


class CommandTest(base.TestCase):
    """Functional tests for openstackclient command list."""
    GROUPS = [
        'openstack.volume.v3',
        'openstack.network.v2',
        'openstack.image.v2',
        'openstack.identity.v3',
        'openstack.compute.v2',
        'openstack.common',
        'openstack.cli',
    ]

    def test_command_list_no_option(self):
        cmd_output = json.loads(self.openstack('command list -f json'))
        group_names = [each.get('Command Group') for each in cmd_output]
        for one_group in self.GROUPS:
            self.assertIn(one_group, group_names)

    def test_command_list_with_group(self):
        input_groups = [
            'volume',
            'network',
            'image',
            'identity',
            'compute.v2'
        ]
        for each_input in input_groups:
            cmd_output = json.loads(self.openstack(
                'command list --group %s -f json' % each_input
            ))
            group_names = [each.get('Command Group') for each in cmd_output]
            for each_name in group_names:
                self.assertIn(each_input, each_name)
