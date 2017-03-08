# Copyright (c) 2016, Intel Corporation.
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

import re
import uuid

from openstackclient.tests.functional import base


class TestMeter(base.TestCase):
    """Functional tests for network meter."""

    # NOTE(dtroyer): Do not normalize the setup and teardown of the resource
    #                creation and deletion.  Little is gained when each test
    #                has its own needs and there are collisions when running
    #                tests in parallel.

    @classmethod
    def setUpClass(cls):
        # Set up some regex for matching below
        cls.re_name = re.compile("name\s+\|\s+([^|]+?)\s+\|")
        cls.re_shared = re.compile("shared\s+\|\s+(\S+)")
        cls.re_description = re.compile("description\s+\|\s+([^|]+?)\s+\|")

    def test_meter_delete(self):
        """Test create, delete multiple"""
        name1 = uuid.uuid4().hex
        name2 = uuid.uuid4().hex

        raw_output = self.openstack(
            'network meter create ' + name1,
        )
        self.assertEqual(
            name1,
            re.search(self.re_name, raw_output).group(1),
        )
        # Check if default shared values
        self.assertEqual(
            'False',
            re.search(self.re_shared, raw_output).group(1)
        )

        raw_output = self.openstack(
            'network meter create ' + name2,
        )
        self.assertEqual(
            name2,
            re.search(self.re_name, raw_output).group(1),
        )

        raw_output = self.openstack(
            'network meter delete ' + name1 + ' ' + name2,
        )
        self.assertOutput('', raw_output)

    def test_meter_list(self):
        """Test create, list filters, delete"""
        name1 = uuid.uuid4().hex
        raw_output = self.openstack(
            'network meter create --description Test1 --share ' + name1,
        )
        self.addCleanup(self.openstack, 'network meter delete ' + name1)

        self.assertEqual(
            'Test1',
            re.search(self.re_description, raw_output).group(1),
        )
        self.assertEqual(
            'True',
            re.search(self.re_shared, raw_output).group(1),
        )

        name2 = uuid.uuid4().hex
        raw_output = self.openstack(
            'network meter create --description Test2 --no-share ' + name2,
        )
        self.addCleanup(self.openstack, 'network meter delete ' + name2)

        self.assertEqual(
            'Test2',
            re.search(self.re_description, raw_output).group(1),
        )
        self.assertEqual(
            'False',
            re.search(self.re_shared, raw_output).group(1),
        )

        raw_output = self.openstack('network meter list')
        self.assertIsNotNone(re.search(name1 + "\s+\|\s+Test1", raw_output))
        self.assertIsNotNone(re.search(name2 + "\s+\|\s+Test2", raw_output))
