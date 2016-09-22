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

from openstackclient.tests.functional.volume.v1 import common


class SnapshotTests(common.BaseVolumeTests):
    """Functional tests for snapshot. """

    VOLLY = uuid.uuid4().hex
    NAME = uuid.uuid4().hex
    OTHER_NAME = uuid.uuid4().hex
    HEADERS = ['"Name"']

    @classmethod
    def wait_for_status(cls, command, status, tries):
        opts = cls.get_opts(['status'])
        for attempt in range(tries):
            time.sleep(1)
            raw_output = cls.openstack(command + opts)
            if (raw_output == status):
                return
        cls.assertOutput(status, raw_output)

    @classmethod
    def setUpClass(cls):
        super(SnapshotTests, cls).setUpClass()
        cls.openstack('volume create --size 1 ' + cls.VOLLY)
        cls.wait_for_status('volume show ' + cls.VOLLY, 'available\n', 3)
        opts = cls.get_opts(['status'])
        raw_output = cls.openstack('snapshot create --name ' + cls.NAME +
                                   ' ' + cls.VOLLY + opts)
        cls.assertOutput('creating\n', raw_output)
        cls.wait_for_status('snapshot show ' + cls.NAME, 'available\n', 3)

    @classmethod
    def tearDownClass(cls):
        # Rename test
        raw_output = cls.openstack(
            'snapshot set --name ' + cls.OTHER_NAME + ' ' + cls.NAME)
        cls.assertOutput('', raw_output)
        # Delete test
        raw_output_snapshot = cls.openstack(
            'snapshot delete ' + cls.OTHER_NAME)
        cls.wait_for_status('volume show ' + cls.VOLLY, 'available\n', 6)
        raw_output_volume = cls.openstack('volume delete --force ' + cls.VOLLY)
        cls.assertOutput('', raw_output_snapshot)
        cls.assertOutput('', raw_output_volume)

    def test_snapshot_list(self):
        opts = self.get_opts(self.HEADERS)
        raw_output = self.openstack('snapshot list' + opts)
        self.assertIn(self.NAME, raw_output)

    def test_snapshot_set_unset_properties(self):
        raw_output = self.openstack(
            'snapshot set --property a=b --property c=d ' + self.NAME)
        self.assertEqual("", raw_output)
        opts = self.get_opts(["properties"])
        raw_output = self.openstack('snapshot show ' + self.NAME + opts)
        self.assertEqual("a='b', c='d'\n", raw_output)

        raw_output = self.openstack('snapshot unset --property a ' + self.NAME)
        self.assertEqual("", raw_output)
        raw_output = self.openstack('snapshot show ' + self.NAME + opts)
        self.assertEqual("c='d'\n", raw_output)

    def test_snapshot_set_description(self):
        raw_output = self.openstack(
            'snapshot set --description backup ' + self.NAME)
        self.assertEqual("", raw_output)
        opts = self.get_opts(["display_description", "display_name"])
        raw_output = self.openstack('snapshot show ' + self.NAME + opts)
        self.assertEqual("backup\n" + self.NAME + "\n", raw_output)
