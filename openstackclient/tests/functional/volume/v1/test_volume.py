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

import uuid

from openstackclient.tests.functional.volume.v1 import common


class VolumeTests(common.BaseVolumeTests):
    """Functional tests for volume. """

    NAME = uuid.uuid4().hex
    OTHER_NAME = uuid.uuid4().hex
    HEADERS = ['"Display Name"']
    FIELDS = ['display_name']

    @classmethod
    def setUpClass(cls):
        super(VolumeTests, cls).setUpClass()
        opts = cls.get_opts(cls.FIELDS)
        raw_output = cls.openstack('volume create --size 1 ' + cls.NAME + opts)
        expected = cls.NAME + '\n'
        cls.assertOutput(expected, raw_output)

    @classmethod
    def tearDownClass(cls):
        # Rename test
        raw_output = cls.openstack(
            'volume set --name ' + cls.OTHER_NAME + ' ' + cls.NAME)
        cls.assertOutput('', raw_output)
        # Delete test
        raw_output = cls.openstack('volume delete ' + cls.OTHER_NAME)
        cls.assertOutput('', raw_output)

    def test_volume_list(self):
        opts = self.get_opts(self.HEADERS)
        raw_output = self.openstack('volume list' + opts)
        self.assertIn(self.NAME, raw_output)

    def test_volume_show(self):
        opts = self.get_opts(self.FIELDS)
        raw_output = self.openstack('volume show ' + self.NAME + opts)
        self.assertEqual(self.NAME + "\n", raw_output)

    def test_volume_properties(self):
        raw_output = self.openstack(
            'volume set --property a=b --property c=d ' + self.NAME)
        self.assertEqual("", raw_output)
        opts = self.get_opts(["properties"])
        raw_output = self.openstack('volume show ' + self.NAME + opts)
        self.assertEqual("a='b', c='d'\n", raw_output)

        raw_output = self.openstack('volume unset --property a ' + self.NAME)
        self.assertEqual("", raw_output)
        raw_output = self.openstack('volume show ' + self.NAME + opts)
        self.assertEqual("c='d'\n", raw_output)

    def test_volume_set(self):
        self.openstack('volume set --description RAMAC ' + self.NAME)
        opts = self.get_opts(["display_description", "display_name"])
        raw_output = self.openstack('volume show ' + self.NAME + opts)
        self.assertEqual("RAMAC\n" + self.NAME + "\n", raw_output)

    def test_volume_set_size(self):
        self.openstack('volume set --size 2 ' + self.NAME)
        opts = self.get_opts(["display_name", "size"])
        raw_output = self.openstack('volume show ' + self.NAME + opts)
        self.assertEqual(self.NAME + "\n2\n", raw_output)

    def test_volume_set_bootable(self):
        self.openstack('volume set --bootable ' + self.NAME)
        opts = self.get_opts(["bootable"])
        raw_output = self.openstack('volume show ' + self.NAME + opts)
        self.assertEqual("true\n", raw_output)

        self.openstack('volume set --non-bootable ' + self.NAME)
        opts = self.get_opts(["bootable"])
        raw_output = self.openstack('volume show ' + self.NAME + opts)
        self.assertEqual("false\n", raw_output)
