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
import uuid

from openstackclient.tests.functional.volume.v1 import common


class VolumeTests(common.BaseVolumeTests):
    """Functional tests for volume. """

    def test_volume_create_and_delete(self):
        """Test create, delete multiple"""
        name1 = uuid.uuid4().hex
        cmd_output = json.loads(self.openstack(
            'volume create -f json ' +
            '--size 1 ' +
            name1
        ))
        self.assertEqual(
            1,
            cmd_output["size"],
        )

        name2 = uuid.uuid4().hex
        cmd_output = json.loads(self.openstack(
            'volume create -f json ' +
            '--size 2 ' +
            name2
        ))
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
        cmd_output = json.loads(self.openstack(
            'volume create -f json ' +
            '--size 1 ' +
            name1
        ))
        self.addCleanup(self.openstack, 'volume delete ' + name1)
        self.assertEqual(
            1,
            cmd_output["size"],
        )
        self.wait_for_status("volume", name1, "available")

        name2 = uuid.uuid4().hex
        cmd_output = json.loads(self.openstack(
            'volume create -f json ' +
            '--size 2 ' +
            name2
        ))
        self.addCleanup(self.openstack, 'volume delete ' + name2)
        self.assertEqual(
            2,
            cmd_output["size"],
        )
        self.wait_for_status("volume", name2, "available")

        # Test list
        cmd_output = json.loads(self.openstack(
            'volume list -f json '
        ))
        names = [x["Name"] for x in cmd_output]
        self.assertIn(name1, names)
        self.assertIn(name2, names)

        # Test list --long
        cmd_output = json.loads(self.openstack(
            'volume list -f json --long'
        ))
        bootable = [x["Bootable"] for x in cmd_output]
        self.assertIn('false', bootable)

        # Test list --name
        cmd_output = json.loads(self.openstack(
            'volume list -f json ' +
            '--name ' + name1
        ))
        names = [x["Name"] for x in cmd_output]
        self.assertIn(name1, names)
        self.assertNotIn(name2, names)

    def test_volume_set_and_unset(self):
        """Tests create volume, set, unset, show, delete"""
        name = uuid.uuid4().hex
        cmd_output = json.loads(self.openstack(
            'volume create -f json ' +
            '--size 1 ' +
            '--description aaaa ' +
            '--property Alpha=a ' +
            name
        ))
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
            cmd_output["display_description"],
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
        new_name = uuid.uuid4().hex
        self.addCleanup(self.openstack, 'volume delete ' + new_name)
        raw_output = self.openstack(
            'volume set ' +
            '--name ' + new_name +
            ' --size 2 ' +
            '--description bbbb ' +
            '--no-property ' +
            '--property Beta=b ' +
            '--property Gamma=c ' +
            '--bootable ' +
            name,
        )
        self.assertOutput('', raw_output)

        cmd_output = json.loads(self.openstack(
            'volume show -f json ' +
            new_name
        ))
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
            cmd_output["display_description"],
        )
        self.assertEqual(
            {'Beta': 'b', 'Gamma': 'c'},
            cmd_output["properties"],
        )
        self.assertEqual(
            'true',
            cmd_output["bootable"],
        )

        # Test volume unset
        raw_output = self.openstack(
            'volume unset ' +
            '--property Beta ' +
            new_name,
        )
        self.assertOutput('', raw_output)

        cmd_output = json.loads(self.openstack(
            'volume show -f json ' +
            new_name
        ))
        self.assertEqual(
            {'Gamma': 'c'},
            cmd_output["properties"],
        )

    def test_volume_create_and_list_and_show_backward_compatibility(self):
        """Test backward compatibility of create, list, show"""
        name1 = uuid.uuid4().hex
        json_output = json.loads(self.openstack(
            'volume create -f json ' +
            '-c display_name -c id ' +
            '--size 1 ' +
            name1
        ))
        self.assertIn('display_name', json_output)
        self.assertEqual(name1, json_output['display_name'])
        self.assertIn('id', json_output)
        volume_id = json_output['id']
        self.assertIsNotNone(volume_id)
        self.assertNotIn('name', json_output)
        self.addCleanup(self.openstack, 'volume delete ' + volume_id)

        self.wait_for_status("volume", name1, "available")

        json_output = json.loads(self.openstack(
            'volume list -f json ' +
            '-c "Display Name"'
        ))
        for each_volume in json_output:
            self.assertIn('Display Name', each_volume)

        json_output = json.loads(self.openstack(
            'volume list -f json ' +
            '-c "Name"'
        ))
        for each_volume in json_output:
            self.assertIn('Name', each_volume)

        json_output = json.loads(self.openstack(
            'volume show -f json ' +
            '-c display_name -c id ' +
            name1
        ))
        self.assertIn('display_name', json_output)
        self.assertEqual(name1, json_output['display_name'])
        self.assertIn('id', json_output)
        self.assertNotIn('name', json_output)
