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
import time
import uuid

from openstackclient.tests.functional.volume.v1 import common


class VolumeSnapshotTests(common.BaseVolumeTests):
    """Functional tests for volume snapshot. """

    VOLLY = uuid.uuid4().hex

    @classmethod
    def wait_for_status(cls, command, status, tries):
        opts = cls.get_opts(['status'])
        for attempt in range(tries):
            time.sleep(1)
            raw_output = cls.openstack(command + opts)
            if (raw_output.rstrip() == status):
                return
        cls.assertOutput(status, raw_output)

    @classmethod
    def setUpClass(cls):
        super(VolumeSnapshotTests, cls).setUpClass()
        # create a volume for all tests to create snapshot
        cmd_output = json.loads(cls.openstack(
            'volume create -f json ' +
            '--size 1 ' +
            cls.VOLLY
        ))
        cls.wait_for_status('volume show ' + cls.VOLLY, 'available', 6)
        cls.VOLUME_ID = cmd_output['id']

    @classmethod
    def tearDownClass(cls):
        cls.wait_for_status('volume show ' + cls.VOLLY, 'available', 6)
        raw_output = cls.openstack('volume delete --force ' + cls.VOLLY)
        cls.assertOutput('', raw_output)

    def test_volume_snapshot__delete(self):
        """Test create, delete multiple"""
        name1 = uuid.uuid4().hex
        cmd_output = json.loads(self.openstack(
            'volume snapshot create -f json ' +
            name1 +
            ' --volume ' + self.VOLLY
        ))
        self.assertEqual(
            name1,
            cmd_output["display_name"],
        )

        name2 = uuid.uuid4().hex
        cmd_output = json.loads(self.openstack(
            'volume snapshot create -f json ' +
            name2 +
            ' --volume ' + self.VOLLY
        ))
        self.assertEqual(
            name2,
            cmd_output["display_name"],
        )

        self.wait_for_status(
            'volume snapshot show ' + name1, 'available', 6)
        self.wait_for_status(
            'volume snapshot show ' + name2, 'available', 6)

        del_output = self.openstack(
            'volume snapshot delete ' + name1 + ' ' + name2)
        self.assertOutput('', del_output)

    def test_volume_snapshot_list(self):
        """Test create, list filter"""
        name1 = uuid.uuid4().hex
        cmd_output = json.loads(self.openstack(
            'volume snapshot create -f json ' +
            name1 +
            ' --volume ' + self.VOLLY
        ))
        self.addCleanup(self.openstack, 'volume snapshot delete ' + name1)
        self.assertEqual(
            name1,
            cmd_output["display_name"],
        )
        self.assertEqual(
            self.VOLUME_ID,
            cmd_output["volume_id"],
        )
        self.assertEqual(
            1,
            cmd_output["size"],
        )
        self.wait_for_status(
            'volume snapshot show ' + name1, 'available', 6)

        name2 = uuid.uuid4().hex
        cmd_output = json.loads(self.openstack(
            'volume snapshot create -f json ' +
            name2 +
            ' --volume ' + self.VOLLY
        ))
        self.addCleanup(self.openstack, 'volume snapshot delete ' + name2)
        self.assertEqual(
            name2,
            cmd_output["display_name"],
        )
        self.assertEqual(
            self.VOLUME_ID,
            cmd_output["volume_id"],
        )
        self.assertEqual(
            1,
            cmd_output["size"],
        )
        self.wait_for_status(
            'volume snapshot show ' + name2, 'available', 6)

        # Test list --long, --status
        cmd_output = json.loads(self.openstack(
            'volume snapshot list -f json ' +
            '--long ' +
            '--status error'
        ))
        names = [x["Name"] for x in cmd_output]
        self.assertNotIn(name1, names)
        self.assertNotIn(name2, names)

        # Test list --volume
        cmd_output = json.loads(self.openstack(
            'volume snapshot list -f json ' +
            '--volume ' + self.VOLLY
        ))
        names = [x["Name"] for x in cmd_output]
        self.assertIn(name1, names)
        self.assertIn(name2, names)

        # Test list --name
        cmd_output = json.loads(self.openstack(
            'volume snapshot list -f json ' +
            '--name ' + name1
        ))
        names = [x["Name"] for x in cmd_output]
        self.assertIn(name1, names)
        self.assertNotIn(name2, names)

    def test_snapshot_set(self):
        """Test create, set, unset, show, delete volume snapshot"""
        name = uuid.uuid4().hex
        new_name = name + "_"
        cmd_output = json.loads(self.openstack(
            'volume snapshot create -f json ' +
            '--volume ' + self.VOLLY +
            ' --description aaaa ' +
            name
        ))
        self.addCleanup(self.openstack, 'volume snapshot delete ' + new_name)
        self.assertEqual(
            name,
            cmd_output["display_name"],
        )
        self.assertEqual(
            1,
            cmd_output["size"],
        )
        self.assertEqual(
            'aaaa',
            cmd_output["display_description"],
        )
        self.wait_for_status(
            'volume snapshot show ' + name, 'available', 6)

        # Test volume snapshot set
        raw_output = self.openstack(
            'volume snapshot set ' +
            '--name ' + new_name +
            ' --description bbbb ' +
            '--property Alpha=a ' +
            '--property Beta=b ' +
            name,
        )
        self.assertOutput('', raw_output)

        # Show snapshot set result
        cmd_output = json.loads(self.openstack(
            'volume snapshot show -f json ' +
            new_name
        ))
        self.assertEqual(
            new_name,
            cmd_output["display_name"],
        )
        self.assertEqual(
            1,
            cmd_output["size"],
        )
        self.assertEqual(
            'bbbb',
            cmd_output["display_description"],
        )
        self.assertEqual(
            "Alpha='a', Beta='b'",
            cmd_output["properties"],
        )

        # Test volume unset
        raw_output = self.openstack(
            'volume snapshot unset ' +
            '--property Alpha ' +
            new_name,
        )
        self.assertOutput('', raw_output)

        cmd_output = json.loads(self.openstack(
            'volume snapshot show -f json ' +
            new_name
        ))
        self.assertEqual(
            "Beta='b'",
            cmd_output["properties"],
        )

        # Test volume snapshot set --no-property
        raw_output = self.openstack(
            'volume snapshot set ' +
            '--no-property ' +
            new_name,
        )
        self.assertOutput('', raw_output)
        cmd_output = json.loads(self.openstack(
            'volume snapshot show -f json ' +
            new_name
        ))
        self.assertNotIn(
            "Beta='b'",
            cmd_output["properties"],
        )
