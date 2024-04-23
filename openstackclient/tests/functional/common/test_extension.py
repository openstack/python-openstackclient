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

from tempest.lib import exceptions as tempest_exc

from openstackclient.tests.functional import base


class ExtensionTests(base.TestCase):
    """Functional tests for extension"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.haz_network = cls.is_service_enabled('network')

    def test_extension_list_compute(self):
        """Test compute extension list"""
        output = self.openstack(
            'extension list --compute',
            parse_output=True,
        )
        name_list = [item.get('Name') for item in output]
        self.assertIn(
            'ImageSize',
            name_list,
        )

    def test_extension_list_volume(self):
        """Test volume extension list"""
        output = self.openstack(
            'extension list --volume',
            parse_output=True,
        )
        name_list = [item.get('Name') for item in output]
        self.assertIn(
            'TypesManage',
            name_list,
        )

    def test_extension_list_network(self):
        """Test network extension list"""
        if not self.haz_network:
            self.skipTest("No Network service present")

        output = self.openstack(
            'extension list --network',
            parse_output=True,
        )
        name_list = [item.get('Name') for item in output]
        self.assertIn(
            'Default Subnetpools',
            name_list,
        )

    def test_extension_show_network(self):
        """Test network extension show"""
        if not self.haz_network:
            self.skipTest("No Network service present")

        name = 'agent'
        output = self.openstack(
            'extension show ' + name,
            parse_output=True,
        )
        self.assertEqual(
            name,
            output.get('alias'),
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
