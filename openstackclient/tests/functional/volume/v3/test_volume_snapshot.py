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
        # create a test volume used by all snapshot tests
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

    def test_volume_snapshot(self):
        # create volume snapshot
        name = uuid.uuid4().hex

        cmd_output = self.openstack(
            'volume snapshot create '
            + '--volume '
            + self.VOLLY
            + ' --description aaaa '
            + '--property Alpha=a '
            + name,
            parse_output=True,
        )
        snap_id = cmd_output['id']

        self.addCleanup(self.wait_for_delete, 'volume snapshot', snap_id)
        # delete volume snapshot
        self.addCleanup(
            self.openstack,
            'volume snapshot delete ' + snap_id,
        )
        self.wait_for_status('volume snapshot', snap_id, 'available')

        # show volume snapshot
        snapshot_info = self.openstack(
            'volume snapshot show ' + name,
            parse_output=True,
        )

        self.assertEqual(name, snapshot_info['name'])
        self.assertEqual('aaaa', snapshot_info["description"])
        self.assertEqual({'Alpha': 'a'}, snapshot_info["properties"])

        # list volume snapshot --name
        cmd_output = self.openstack(
            'volume snapshot list --name ' + name,
            parse_output=True,
        )
        names = [x['Name'] for x in cmd_output]
        self.assertIn(name, names)

        # list volume snapshot --volume
        cmd_output = self.openstack(
            'volume snapshot list ' + '--volume ' + self.VOLLY,
            parse_output=True,
        )
        names = [x["Name"] for x in cmd_output]
        self.assertIn(name, names)

        # set volume snapshot
        new_name = name + "_"
        raw_output = self.openstack(
            'volume snapshot set '
            + '--name '
            + new_name
            + ' --description bbbb '
            + '--property Alpha=c '
            + '--property Beta=b '
            + snap_id,
        )
        self.assertOutput('', raw_output)

        cmd_output = self.openstack(
            'volume snapshot show ' + new_name,
            parse_output=True,
        )
        self.assertEqual(
            new_name,
            cmd_output["name"],
        )
        self.assertEqual(
            'bbbb',
            cmd_output["description"],
        )
        self.assertEqual(
            {'Alpha': 'c', 'Beta': 'b'},
            cmd_output["properties"],
        )

        # unset volume snapshot
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

        # set volume snapshot --no-property, --state error
        raw_output = self.openstack(
            'volume snapshot set '
            + '--no-property '
            + '--state error '
            + new_name,
        )
        self.assertOutput('', raw_output)

        cmd_output = self.openstack(
            'volume snapshot show ' + new_name,
            parse_output=True,
        )
        self.assertEqual({}, cmd_output["properties"])

        # list volume snapshot --long --status
        cmd_output = self.openstack(
            'volume snapshot list ' + '--long ' + '--status error',
            parse_output=True,
        )
        names = [x["Name"] for x in cmd_output]
        self.assertIn(new_name, names)
