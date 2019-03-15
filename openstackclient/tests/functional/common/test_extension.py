# Copyright (c) 2017, Intel Corporation.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import json

from tempest.lib import exceptions as tempest_exc

from openstackclient.tests.functional import base


class ExtensionTests(base.TestCase):
    """Functional tests for extension"""

    @classmethod
    def setUpClass(cls):
        super(ExtensionTests, cls).setUpClass()
        cls.haz_network = cls.is_service_enabled('network')

    def test_extension_list_compute(self):
        """Test compute extension list"""
        json_output = json.loads(self.openstack(
            'extension list -f json ' +
            '--compute'
        ))
        name_list = [item.get('Name') for item in json_output]
        self.assertIn(
            'ImageSize',
            name_list,
        )

    def test_extension_list_volume(self):
        """Test volume extension list"""
        json_output = json.loads(self.openstack(
            'extension list -f json ' +
            '--volume'
        ))
        name_list = [item.get('Name') for item in json_output]
        self.assertIn(
            'TypesManage',
            name_list,
        )

    def test_extension_list_network(self):
        """Test network extension list"""
        if not self.haz_network:
            self.skipTest("No Network service present")

        json_output = json.loads(self.openstack(
            'extension list -f json ' +
            '--network'
        ))
        name_list = [item.get('Name') for item in json_output]
        self.assertIn(
            'Default Subnetpools',
            name_list,
        )

    # NOTE(dtroyer): Only network extensions are currently supported but
    #                I am going to leave this here anyway as a reminder
    #                fix that.
    # def test_extension_show_compute(self):
    #     """Test compute extension show"""
    #     json_output = json.loads(self.openstack(
    #         'extension show -f json ' +
    #         'ImageSize'
    #     ))
    #     self.assertEqual(
    #         'OS-EXT-IMG-SIZE',
    #         json_output.get('Alias'),
    #     )

    def test_extension_show_network(self):
        """Test network extension show"""
        if not self.haz_network:
            self.skipTest("No Network service present")

        name = 'agent'
        json_output = json.loads(self.openstack(
            'extension show -f json ' +
            name
        ))
        self.assertEqual(
            name,
            json_output.get('alias'),
        )

    def test_extension_show_not_exist(self):
        """Test extension show with not existed name"""
        if not self.haz_network:
            self.skipTest("No Network service present")

        name = 'not_existed_ext'
        try:
            self.openstack('extension show ' + name)
        except tempest_exc.CommandFailed as e:
            self.assertIn('No Extension found for', str(e))
            self.assertIn(name, str(e))
        else:
            self.fail('CommandFailed should be raised')
