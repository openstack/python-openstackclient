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

import re
import uuid

from openstackclient.tests.functional import base


class NetworkFlavorTests(base.TestCase):
    """Functional tests for network flavor."""

    @classmethod
    def setUpClass(cls):
        # Set up some regex for matching below
        cls.re_name = re.compile("name\s+\|\s+([^|]+?)\s+\|")
        cls.re_enabled = re.compile("enabled\s+\|\s+(\S+)")
        cls.re_description = re.compile("description\s+\|\s+([^|]+?)\s+\|")
        cls.SERVICE_TYPE = 'L3_ROUTER_NAT'

    def test_network_flavor_delete(self):
        """Test create, delete multiple"""
        name1 = uuid.uuid4().hex
        raw_output = self.openstack(
            'network flavor create --description testdescription --enable'
            ' --service-type ' + self.SERVICE_TYPE + ' ' + name1,
        )
        self.assertEqual(
            name1,
            re.search(self.re_name, raw_output).group(1))
        self.assertEqual(
            'True',
            re.search(self.re_enabled, raw_output).group(1))
        self.assertEqual(
            'testdescription',
            re.search(self.re_description, raw_output).group(1))

        name2 = uuid.uuid4().hex
        raw_output = self.openstack(
            'network flavor create --description testdescription1 --disable'
            ' --service-type ' + self.SERVICE_TYPE + ' ' + name2,
        )
        self.assertEqual(
            name2,
            re.search(self.re_name, raw_output).group(1))
        self.assertEqual(
            'False',
            re.search(self.re_enabled, raw_output).group(1))
        self.assertEqual(
            'testdescription1',
            re.search(self.re_description, raw_output).group(1))

        raw_output = self.openstack(
            'network flavor delete ' + name1 + " " + name2)
        self.assertOutput('', raw_output)

    def test_network_flavor_list(self):
        name1 = uuid.uuid4().hex
        raw_output = self.openstack(
            'network flavor create --description testdescription --enable'
            ' --service-type ' + self.SERVICE_TYPE + ' ' + name1,
        )
        self.addCleanup(self.openstack, "network flavor delete " + name1)
        self.assertEqual(
            name1,
            re.search(self.re_name, raw_output).group(1))
        self.assertEqual(
            'True',
            re.search(self.re_enabled, raw_output).group(1))
        self.assertEqual(
            'testdescription',
            re.search(self.re_description, raw_output).group(1))

        name2 = uuid.uuid4().hex
        raw_output = self.openstack(
            'network flavor create --description testdescription --disable'
            ' --service-type ' + self.SERVICE_TYPE + ' ' + name2,
        )
        self.assertEqual(
            name2,
            re.search(self.re_name, raw_output).group(1))
        self.assertEqual(
            'False',
            re.search(self.re_enabled, raw_output).group(1))
        self.assertEqual(
            'testdescription',
            re.search(self.re_description, raw_output).group(1))
        self.addCleanup(self.openstack, "network flavor delete " + name2)

        # Test list
        raw_output = self.openstack('network flavor list')
        self.assertIsNotNone(raw_output)
        self.assertIsNotNone(re.search(name1, raw_output))
        self.assertIsNotNone(re.search(name2, raw_output))

    def test_network_flavor_set(self):
        name = uuid.uuid4().hex
        newname = name + "_"
        raw_output = self.openstack(
            'network flavor create --description testdescription --enable'
            ' --service-type ' + self.SERVICE_TYPE + ' ' + name,
        )
        self.addCleanup(self.openstack, "network flavor delete " + newname)
        self.assertEqual(
            name,
            re.search(self.re_name, raw_output).group(1))
        self.assertEqual(
            'True',
            re.search(self.re_enabled, raw_output).group(1))
        self.assertEqual(
            'testdescription',
            re.search(self.re_description, raw_output).group(1))

        self.openstack(
            'network flavor set --name ' + newname + ' --disable ' + name
        )
        raw_output = self.openstack('network flavor show ' + newname)
        self.assertEqual(
            newname,
            re.search(self.re_name, raw_output).group(1))
        self.assertEqual(
            'False',
            re.search(self.re_enabled, raw_output).group(1))
        self.assertEqual(
            'testdescription',
            re.search(self.re_description, raw_output).group(1))

    def test_network_flavor_show(self):
        name = uuid.uuid4().hex
        self.openstack(
            'network flavor create --description testdescription --enable'
            ' --service-type ' + self.SERVICE_TYPE + ' ' + name,
        )
        self.addCleanup(self.openstack, "network flavor delete " + name)
        raw_output = self.openstack('network flavor show ' + name)
        self.assertEqual(
            name,
            re.search(self.re_name, raw_output).group(1))
        self.assertEqual(
            'True',
            re.search(self.re_enabled, raw_output).group(1))
        self.assertEqual(
            'testdescription',
            re.search(self.re_description, raw_output).group(1))
