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

from openstackclient.tests.functional.volume.v3 import common


class VolumeSnapshotTests(common.BaseVolumeTests):
    """Functional tests for volume snapshot."""

    VOLLY = uuid.uuid4().hex

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # create a volume for all tests to create snapshot
        cmd_output = cls.openstack(
            'volume create ' + '--size 1 ' + cls.VOLLY,
            parse_output=True,
        )
        cls.wait_for_status('volume', cls.VOLLY, 'available')
        cls.VOLUME_ID = cmd_output['id']

    @classmethod
    def tearDownClass(cls):
        try:
            cls.wait_for_status('volume', cls.VOLLY, 'available')
            raw_output = cls.openstack('volume delete --force ' + cls.VOLLY)
            cls.assertOutput('', raw_output)
        finally:
            super().tearDownClass()

    def test_volume_snapshot_delete(self):
        """Test create, delete multiple"""
        name1 = uuid.uuid4().hex
        cmd_output = self.openstack(
            'volume snapshot create ' + name1 + ' --volume ' + self.VOLLY,
            parse_output=True,
        )
        self.assertEqual(
            name1,
            cmd_output["name"],
        )

        name2 = uuid.uuid4().hex
        cmd_output = self.openstack(
            'volume snapshot create ' + name2 + ' --volume ' + self.VOLLY,
            parse_output=True,
        )
        self.assertEqual(
            name2,
            cmd_output["name"],
        )

        self.wait_for_status('volume snapshot', name1, 'available')
        self.wait_for_status('volume snapshot', name2, 'available')

        del_output = self.openstack(
            'volume snapshot delete ' + name1 + ' ' + name2
        )
        self.assertOutput('', del_output)
        self.wait_for_delete('volume snapshot', name1)
        self.wait_for_delete('volume snapshot', name2)

    def test_volume_snapshot_list(self):
        """Test create, list filter"""
        name1 = uuid.uuid4().hex
        cmd_output = self.openstack(
            'volume snapshot create ' + name1 + ' --volume ' + self.VOLLY,
            parse_output=True,
        )
        self.addCleanup(self.wait_for_delete, 'volume snapshot', name1)
        self.addCleanup(self.openstack, 'volume snapshot delete ' + name1)
        self.assertEqual(
            name1,
            cmd_output["name"],
        )
        self.assertEqual(
            self.VOLUME_ID,
            cmd_output["volume_id"],
        )
        self.assertEqual(
            1,
            cmd_output["size"],
        )
        self.wait_for_status('volume snapshot', name1, 'available')

        name2 = uuid.uuid4().hex
        cmd_output = self.openstack(
            'volume snapshot create ' + name2 + ' --volume ' + self.VOLLY,
            parse_output=True,
        )
        self.addCleanup(self.wait_for_delete, 'volume snapshot', name2)
        self.addCleanup(self.openstack, 'volume snapshot delete ' + name2)
        self.assertEqual(
            name2,
            cmd_output["name"],
        )
        self.assertEqual(
            self.VOLUME_ID,
            cmd_output["volume_id"],
        )
        self.assertEqual(
            1,
            cmd_output["size"],
        )
        self.wait_for_status('volume snapshot', name2, 'available')
        raw_output = self.openstack(
            'volume snapshot set ' + '--state error ' + name2
        )
        self.assertOutput('', raw_output)

        # Test list --long, --status
        cmd_output = self.openstack(
            'volume snapshot list ' + '--long ' + '--status error',
            parse_output=True,
        )
        names = [x["Name"] for x in cmd_output]
        self.assertNotIn(name1, names)
        self.assertIn(name2, names)

        # Test list --volume
        cmd_output = self.openstack(
            'volume snapshot list ' + '--volume ' + self.VOLLY,
            parse_output=True,
        )
        names = [x["Name"] for x in cmd_output]
        self.assertIn(name1, names)
        self.assertIn(name2, names)

        # Test list --name
        cmd_output = self.openstack(
            'volume snapshot list ' + '--name ' + name1,
            parse_output=True,
        )
        names = [x["Name"] for x in cmd_output]
        self.assertIn(name1, names)
        self.assertNotIn(name2, names)

    def test_volume_snapshot_set(self):
        """Test create, set, unset, show, delete volume snapshot"""
        name = uuid.uuid4().hex
        new_name = name + "_"
        cmd_output = self.openstack(
            'volume snapshot create '
            + '--volume '
            + self.VOLLY
            + ' --description aaaa '
            + '--property Alpha=a '
            + name,
            parse_output=True,
        )
        self.addCleanup(self.wait_for_delete, 'volume snapshot', new_name)
        self.addCleanup(self.openstack, 'volume snapshot delete ' + new_name)
        self.assertEqual(
            name,
            cmd_output["name"],
        )
        self.assertEqual(
            1,
            cmd_output["size"],
        )
        self.assertEqual(
            'aaaa',
            cmd_output["description"],
        )
        self.assertEqual(
            {'Alpha': 'a'},
            cmd_output["properties"],
        )
        self.wait_for_status('volume snapshot', name, 'available')

        # Test volume snapshot set
        raw_output = self.openstack(
            'volume snapshot set '
            + '--name '
            + new_name
            + ' --description bbbb '
            + '--property Alpha=c '
            + '--property Beta=b '
            + name,
        )
        self.assertOutput('', raw_output)

        # Show snapshot set result
        cmd_output = self.openstack(
            'volume snapshot show ' + new_name,
            parse_output=True,
        )
        self.assertEqual(
            new_name,
            cmd_output["name"],
        )
        self.assertEqual(
            1,
            cmd_output["size"],
        )
        self.assertEqual(
            'bbbb',
            cmd_output["description"],
        )
        self.assertEqual(
            {'Alpha': 'c', 'Beta': 'b'},
            cmd_output["properties"],
        )

        # Test volume snapshot unset
        raw_output = self.openstack(
            'volume snapshot unset ' + '--property Alpha ' + new_name,
        )
        self.assertOutput('', raw_output)

        cmd_output = self.openstack(
            'volume snapshot show ' + new_name,
            parse_output=True,
        )
        self.assertEqual(
            {'Beta': 'b'},
            cmd_output["properties"],
        )

        # Test volume snapshot set --no-property
        raw_output = self.openstack(
            'volume snapshot set ' + '--no-property ' + new_name,
        )
        self.assertOutput('', raw_output)
        cmd_output = self.openstack(
            'volume snapshot show ' + new_name,
            parse_output=True,
        )
        self.assertNotIn(
            {'Beta': 'b'},
            cmd_output["properties"],
        )
