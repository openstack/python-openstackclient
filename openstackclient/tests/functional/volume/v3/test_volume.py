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


class VolumeTests(common.BaseVolumeTests):
    """Functional tests for volume."""

    def test_volume_delete(self):
        """Test create, delete multiple"""
        name1 = uuid.uuid4().hex
        cmd_output = self.openstack(
            'volume create --size 1 ' + name1,
            parse_output=True,
        )
        self.assertEqual(
            1,
            cmd_output["size"],
        )

        name2 = uuid.uuid4().hex
        cmd_output = self.openstack(
            'volume create --size 2 ' + name2,
            parse_output=True,
        )
        self.assertEqual(
            2,
            cmd_output["size"],
        )

        self.wait_for_status("volume", name1, "available")
        self.wait_for_status("volume", name2, "available")
        del_output = self.openstack('volume delete ' + name1 + ' ' + name2)
        self.assertOutput('', del_output)

    def test_volume_list(self):
        """Test create, list filter"""
        name1 = uuid.uuid4().hex
        cmd_output = self.openstack(
            'volume create --size 1 ' + name1,
            parse_output=True,
        )
        self.addCleanup(self.openstack, 'volume delete ' + name1)
        self.assertEqual(
            1,
            cmd_output["size"],
        )
        self.wait_for_status("volume", name1, "available")

        name2 = uuid.uuid4().hex
        cmd_output = self.openstack(
            'volume create --size 2 ' + name2,
            parse_output=True,
        )
        self.addCleanup(self.openstack, 'volume delete ' + name2)
        self.assertEqual(
            2,
            cmd_output["size"],
        )
        self.wait_for_status("volume", name2, "available")
        raw_output = self.openstack('volume set ' + '--state error ' + name2)
        self.assertOutput('', raw_output)

        # Test list --long
        cmd_output = self.openstack(
            'volume list --long',
            parse_output=True,
        )
        names = [x["Name"] for x in cmd_output]
        self.assertIn(name1, names)
        self.assertIn(name2, names)

        # Test list --status
        cmd_output = self.openstack(
            'volume list --status error',
            parse_output=True,
        )
        names = [x["Name"] for x in cmd_output]
        self.assertNotIn(name1, names)
        self.assertIn(name2, names)

        # TODO(qiangjiahui): Add project option to filter tests when we can
        # specify volume with project

    def test_volume_set_and_unset(self):
        """Tests create volume, set, unset, show, delete"""
        name = uuid.uuid4().hex
        new_name = name + "_"
        cmd_output = self.openstack(
            'volume create '
            + '--size 1 '
            + '--description aaaa '
            + '--property Alpha=a '
            + name,
            parse_output=True,
        )
        self.addCleanup(self.openstack, 'volume delete ' + new_name)
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
        self.assertEqual(
            'false',
            cmd_output["bootable"],
        )
        self.wait_for_status("volume", name, "available")

        # Test volume set
        raw_output = self.openstack(
            'volume set '
            + '--name '
            + new_name
            + ' --size 2 '
            + '--description bbbb '
            + '--no-property '
            + '--property Beta=b '
            + '--property Gamma=c '
            + '--image-property a=b '
            + '--image-property c=d '
            + '--bootable '
            + name,
        )
        self.assertOutput('', raw_output)
        self.wait_for_status("volume", new_name, "available")

        cmd_output = self.openstack(
            'volume show ' + new_name,
            parse_output=True,
        )
        self.assertEqual(
            new_name,
            cmd_output["name"],
        )
        self.assertEqual(
            2,
            cmd_output["size"],
        )
        self.assertEqual(
            'bbbb',
            cmd_output["description"],
        )
        self.assertEqual(
            {'Beta': 'b', 'Gamma': 'c'},
            cmd_output["properties"],
        )
        self.assertEqual(
            {'a': 'b', 'c': 'd'},
            cmd_output["volume_image_metadata"],
        )
        self.assertEqual(
            'true',
            cmd_output["bootable"],
        )

        # Test volume unset
        raw_output = self.openstack(
            'volume unset '
            + '--property Beta '
            + '--image-property a '
            + new_name,
        )
        self.assertOutput('', raw_output)

        cmd_output = self.openstack(
            'volume show ' + new_name,
            parse_output=True,
        )
        self.assertEqual(
            {'Gamma': 'c'},
            cmd_output["properties"],
        )
        self.assertEqual(
            {'c': 'd'},
            cmd_output["volume_image_metadata"],
        )

    def test_volume_snapshot(self):
        """Tests volume create from snapshot"""

        volume_name = uuid.uuid4().hex
        snapshot_name = uuid.uuid4().hex
        # Make a snapshot
        cmd_output = self.openstack(
            'volume create --size 1 ' + volume_name,
            parse_output=True,
        )
        self.wait_for_status("volume", volume_name, "available")
        self.assertEqual(
            volume_name,
            cmd_output["name"],
        )
        cmd_output = self.openstack(
            'volume snapshot create '
            + snapshot_name
            + ' --volume '
            + volume_name,
            parse_output=True,
        )
        self.wait_for_status("volume snapshot", snapshot_name, "available")

        name = uuid.uuid4().hex
        # Create volume from snapshot
        cmd_output = self.openstack(
            'volume create ' + '--snapshot ' + snapshot_name + ' ' + name,
            parse_output=True,
        )
        self.addCleanup(self.openstack, 'volume delete ' + name)
        self.addCleanup(self.openstack, 'volume delete ' + volume_name)
        self.assertEqual(
            name,
            cmd_output["name"],
        )
        self.wait_for_status("volume", name, "available")

        # Delete snapshot
        raw_output = self.openstack('volume snapshot delete ' + snapshot_name)
        self.assertOutput('', raw_output)
        # Deleting snapshot may take time. If volume snapshot still exists when
        # a parent volume delete is requested, the volume deletion will fail.
        self.wait_for_delete('volume snapshot', snapshot_name)

    def test_volume_list_backward_compatibility(self):
        """Test backward compatibility of list command"""
        name1 = uuid.uuid4().hex
        cmd_output = self.openstack(
            'volume create --size 1 ' + name1,
            parse_output=True,
        )
        self.addCleanup(self.openstack, 'volume delete ' + name1)
        self.assertEqual(
            1,
            cmd_output["size"],
        )
        self.wait_for_status("volume", name1, "available")

        # Test list -c "Display Name"
        cmd_output = self.openstack(
            'volume list -c "Display Name"',
            parse_output=True,
        )
        for each_volume in cmd_output:
            self.assertIn('Display Name', each_volume)

        # Test list -c "Name"
        cmd_output = self.openstack(
            'volume list -c "Name"',
            parse_output=True,
        )
        for each_volume in cmd_output:
            self.assertIn('Name', each_volume)
