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


class VolumeTests(common.BaseVolumeTests):
    """Functional tests for volume. """

    NAME = uuid.uuid4().hex
    SNAPSHOT_NAME = uuid.uuid4().hex
    VOLUME_FROM_SNAPSHOT_NAME = uuid.uuid4().hex
    OTHER_NAME = uuid.uuid4().hex
    HEADERS = ['"Display Name"']
    FIELDS = ['name']

    @classmethod
    def setUpClass(cls):
        super(VolumeTests, cls).setUpClass()
        opts = cls.get_opts(cls.FIELDS)

        # Create test volume
        raw_output = cls.openstack('volume create --size 1 ' + cls.NAME + opts)
        expected = cls.NAME + '\n'
        cls.assertOutput(expected, raw_output)

    @classmethod
    def tearDownClass(cls):
        # Rename test volume
        raw_output = cls.openstack(
            'volume set --name ' + cls.OTHER_NAME + ' ' + cls.NAME)
        cls.assertOutput('', raw_output)

        # Set volume state
        cls.openstack('volume set --state error ' + cls.OTHER_NAME)
        opts = cls.get_opts(["status"])
        raw_output_status = cls.openstack(
            'volume show ' + cls.OTHER_NAME + opts)

        # Delete test volume
        raw_output = cls.openstack('volume delete ' + cls.OTHER_NAME)
        cls.assertOutput('', raw_output)
        cls.assertOutput('error\n', raw_output_status)

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
        discription = uuid.uuid4().hex
        self.openstack('volume set --description ' + discription + ' ' +
                       self.NAME)
        opts = self.get_opts(["description", "name"])
        raw_output = self.openstack('volume show ' + self.NAME + opts)
        self.assertEqual(discription + "\n" + self.NAME + "\n", raw_output)

    def test_volume_set_size(self):
        self.openstack('volume set --size 2 ' + self.NAME)
        opts = self.get_opts(["name", "size"])
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

    def test_volume_snapshot(self):
        opts = self.get_opts(self.FIELDS)

        # Create snapshot from test volume
        raw_output = self.openstack('snapshot create ' + self.NAME +
                                    ' --name ' + self.SNAPSHOT_NAME + opts)
        expected = self.SNAPSHOT_NAME + '\n'
        self.assertOutput(expected, raw_output)
        self.wait_for("snapshot", self.SNAPSHOT_NAME, "available")

        # Create volume from snapshot
        raw_output = self.openstack('volume create --size 2 --snapshot ' +
                                    self.SNAPSHOT_NAME + ' ' +
                                    self.VOLUME_FROM_SNAPSHOT_NAME + opts)
        expected = self.VOLUME_FROM_SNAPSHOT_NAME + '\n'
        self.assertOutput(expected, raw_output)
        self.wait_for("volume", self.VOLUME_FROM_SNAPSHOT_NAME, "available")

        # Delete volume that create from snapshot
        raw_output = self.openstack('volume delete ' +
                                    self.VOLUME_FROM_SNAPSHOT_NAME)
        self.assertOutput('', raw_output)

        # Delete test snapshot
        raw_output = self.openstack('snapshot delete ' + self.SNAPSHOT_NAME)
        self.assertOutput('', raw_output)
        self.wait_for("volume", self.NAME, "available")

    def wait_for(self, check_type, check_name, desired_status, wait=120,
                 interval=5, failures=['ERROR']):
        status = "notset"
        total_sleep = 0
        opts = self.get_opts(['status'])
        while total_sleep < wait:
            status = self.openstack(check_type + ' show ' + check_name + opts)
            status = status.rstrip()
            print('Checking {} {} Waiting for {} current status: {}'
                  .format(check_type, check_name, desired_status, status))
            if status == desired_status:
                break
            self.assertNotIn(status, failures)
            time.sleep(interval)
            total_sleep += interval
        self.assertEqual(desired_status, status)
