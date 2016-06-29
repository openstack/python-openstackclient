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

import time
import uuid

from openstackclient.tests.functional.volume.v2 import common


class VolumeTypeTests(common.BaseVolumeTests):
    """Functional tests for volume type. """

    NAME = uuid.uuid4().hex
    HEADERS = ['"Name"']
    FIELDS = ['name']

    @classmethod
    def setUpClass(cls):
        super(VolumeTypeTests, cls).setUpClass()
        opts = cls.get_opts(cls.FIELDS)
        raw_output = cls.openstack(
            'volume type create --private ' + cls.NAME + opts)
        expected = cls.NAME + '\n'
        cls.assertOutput(expected, raw_output)

    @classmethod
    def tearDownClass(cls):
        raw_output = cls.openstack('volume type delete ' + cls.NAME)
        cls.assertOutput('', raw_output)

    def test_volume_type_list(self):
        opts = self.get_opts(self.HEADERS)
        raw_output = self.openstack('volume type list' + opts)
        self.assertIn(self.NAME, raw_output)

    def test_volume_type_show(self):
        opts = self.get_opts(self.FIELDS)
        raw_output = self.openstack('volume type show ' + self.NAME + opts)
        self.assertEqual(self.NAME + "\n", raw_output)

    def test_volume_type_set_unset_properties(self):
        raw_output = self.openstack(
            'volume type set --property a=b --property c=d ' + self.NAME)
        self.assertEqual("", raw_output)

        opts = self.get_opts(["properties"])
        raw_output = self.openstack('volume type show ' + self.NAME + opts)
        self.assertEqual("a='b', c='d'\n", raw_output)

        raw_output = self.openstack('volume type unset --property a '
                                    + self.NAME)
        self.assertEqual("", raw_output)
        raw_output = self.openstack('volume type show ' + self.NAME + opts)
        self.assertEqual("c='d'\n", raw_output)

    def test_volume_type_set_unset_multiple_properties(self):
        raw_output = self.openstack(
            'volume type set --property a=b --property c=d ' + self.NAME)
        self.assertEqual("", raw_output)

        opts = self.get_opts(["properties"])
        raw_output = self.openstack('volume type show ' + self.NAME + opts)
        self.assertEqual("a='b', c='d'\n", raw_output)

        raw_output = self.openstack(
            'volume type unset --property a --property c ' + self.NAME)
        self.assertEqual("", raw_output)
        raw_output = self.openstack('volume type show ' + self.NAME + opts)
        self.assertEqual("\n", raw_output)

    def test_volume_type_set_unset_project(self):
        raw_output = self.openstack(
            'volume type set --project admin ' + self.NAME)
        self.assertEqual("", raw_output)

        raw_output = self.openstack(
            'volume type unset --project admin ' + self.NAME)
        self.assertEqual("", raw_output)

    def test_multi_delete(self):
        vol_type1 = uuid.uuid4().hex
        vol_type2 = uuid.uuid4().hex
        self.openstack('volume type create ' + vol_type1)
        time.sleep(5)
        self.openstack('volume type create ' + vol_type2)
        time.sleep(5)
        cmd = 'volume type delete %s %s' % (vol_type1, vol_type2)
        time.sleep(5)
        raw_output = self.openstack(cmd)
        self.assertOutput('', raw_output)
