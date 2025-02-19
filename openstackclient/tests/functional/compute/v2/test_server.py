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

import itertools
import json
import time
import uuid

from tempest.lib import exceptions

from openstackclient.compute.v2 import server as v2_server
from openstackclient.tests.functional.compute.v2 import common
from openstackclient.tests.functional.volume.v2 import common as volume_common


class ServerTests(common.ComputeTestCase):
    """Functional tests for openstack server commands"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.haz_network = cls.is_service_enabled('network')

    def test_server_list(self):
        """Test server list"""
        cmd_output = self.server_create()
        name1 = cmd_output['name']
        cmd_output = self.server_create()
        name2 = cmd_output['name']
        self.wait_for_status(name1, "ACTIVE")
        self.wait_for_status(name2, "ACTIVE")

        cmd_output = self.openstack(
            'server list',
            parse_output=True,
        )
        col_name = [x["Name"] for x in cmd_output]
        self.assertIn(name1, col_name)
        self.assertIn(name2, col_name)

        # Test list --status PAUSED
        raw_output = self.openstack('server pause ' + name2)
        self.assertEqual("", raw_output)
        self.wait_for_status(name2, "PAUSED")
        cmd_output = self.openstack(
            'server list ' + '--status ACTIVE',
            parse_output=True,
        )
        col_name = [x["Name"] for x in cmd_output]
        self.assertIn(name1, col_name)
        self.assertNotIn(name2, col_name)
        cmd_output = self.openstack(
            'server list ' + '--status PAUSED',
            parse_output=True,
        )
        col_name = [x["Name"] for x in cmd_output]
        self.assertNotIn(name1, col_name)
        self.assertIn(name2, col_name)

    def test_server_list_with_marker_and_deleted(self):
        """Test server list with deleted and marker"""
        cmd_output = self.server_create(cleanup=False)
        name1 = cmd_output['name']
        cmd_output = self.server_create(cleanup=False)
        name2 = cmd_output['name']
        id2 = cmd_output['id']
        self.wait_for_status(name1, "ACTIVE")
        self.wait_for_status(name2, "ACTIVE")

        # Test list --marker with ID
        cmd_output = self.openstack(
            'server list --marker ' + id2,
            parse_output=True,
        )
        col_name = [x["Name"] for x in cmd_output]
        self.assertIn(name1, col_name)

        # Test list --marker with Name
        cmd_output = self.openstack(
            'server list --marker ' + name2,
            parse_output=True,
        )
        col_name = [x["Name"] for x in cmd_output]
        self.assertIn(name1, col_name)

        self.openstack('server delete --wait ' + name1)
        self.openstack('server delete --wait ' + name2)

        # Test list --deleted --marker with ID
        cmd_output = self.openstack(
            'server list --deleted --marker ' + id2,
            parse_output=True,
        )
        col_name = [x["Name"] for x in cmd_output]
        self.assertIn(name1, col_name)

        # Test list --deleted --marker with Name
        try:
            cmd_output = self.openstack(
                'server list --deleted --marker ' + name2,
                parse_output=True,
            )
        except exceptions.CommandFailed as e:
            self.assertIn(
                f'marker [{name2}] not found', e.stderr.decode('utf-8')
            )

    def test_server_list_with_changes_before(self):
        """Test server list.

        Getting the servers list with updated_at time equal or
        before than changes-before.
        """
        cmd_output = self.server_create()
        server_name1 = cmd_output['name']

        cmd_output = self.server_create()
        server_name2 = cmd_output['name']
        updated_at2 = cmd_output['updated']

        cmd_output = self.server_create()
        server_name3 = cmd_output['name']

        cmd_output = self.openstack(
            '--os-compute-api-version 2.66 ' + 'server list '
            '--changes-before ' + updated_at2,
            parse_output=True,
        )

        col_updated = [server["Name"] for server in cmd_output]
        self.assertIn(server_name1, col_updated)
        self.assertIn(server_name2, col_updated)
        self.assertNotIn(server_name3, col_updated)

    def test_server_list_with_changes_since(self):
        """Test server list.

        Getting the servers list with updated_at time equal or
        later than changes-since.
        """
        cmd_output = self.server_create()
        server_name1 = cmd_output['name']
        cmd_output = self.server_create()
        server_name2 = cmd_output['name']
        updated_at2 = cmd_output['updated']
        cmd_output = self.server_create()
        server_name3 = cmd_output['name']

        cmd_output = self.openstack(
            'server list --changes-since ' + updated_at2,
            parse_output=True,
        )

        col_updated = [server["Name"] for server in cmd_output]
        self.assertNotIn(server_name1, col_updated)
        self.assertIn(server_name2, col_updated)
        self.assertIn(server_name3, col_updated)

    def test_server_list_with_changes_before_and_changes_since(self):
        """Test server list.

        Getting the servers list with updated_at time equal or before than
        changes-before and equal or later than changes-since.
        """
        cmd_output = self.server_create()
        server_name1 = cmd_output['name']
        cmd_output = self.server_create()
        server_name2 = cmd_output['name']
        updated_at2 = cmd_output['updated']
        cmd_output = self.server_create()
        server_name3 = cmd_output['name']
        updated_at3 = cmd_output['updated']

        cmd_output = self.openstack(
            '--os-compute-api-version 2.66 '
            + 'server list '
            + '--changes-since '
            + updated_at2
            + ' --changes-before '
            + updated_at3,
            parse_output=True,
        )

        col_updated = [server["Name"] for server in cmd_output]
        self.assertNotIn(server_name1, col_updated)
        self.assertIn(server_name2, col_updated)
        self.assertIn(server_name3, col_updated)

    def test_server_set(self):
        """Test server create, delete, set, show"""
        cmd_output = self.server_create()
        name = cmd_output['name']
        # self.wait_for_status(name, "ACTIVE")

        # Have a look at some other fields
        flavor = self.openstack(
            'flavor show ' + self.flavor_name,
            parse_output=True,
        )
        self.assertEqual(
            self.flavor_name,
            flavor['name'],
        )
        # assume the v2.47+ output format
        self.assertIsInstance(cmd_output['flavor'], dict)
        self.assertIn('name', cmd_output['flavor'])
        self.assertEqual(flavor['name'], cmd_output['flavor']['name'])
        image = self.openstack(
            'image show ' + self.image_name,
            parse_output=True,
        )
        self.assertEqual(
            self.image_name,
            image['name'],
        )
        self.assertEqual(
            '{} ({})'.format(image['name'], image['id']),
            cmd_output["image"],
        )

        # Test properties set
        raw_output = self.openstack(
            'server set ' + '--property a=b --property c=d ' + name
        )
        self.assertOutput('', raw_output)

        cmd_output = self.openstack(
            'server show ' + name,
            parse_output=True,
        )
        # Really, shouldn't this be a list?
        self.assertEqual(
            {'a': 'b', 'c': 'd'},
            cmd_output['properties'],
        )

        raw_output = self.openstack('server unset ' + '--property a ' + name)
        cmd_output = self.openstack(
            'server show ' + name,
            parse_output=True,
        )
        self.assertEqual(
            {'c': 'd'},
            cmd_output['properties'],
        )

        # Test set --name
        new_name = uuid.uuid4().hex
        raw_output = self.openstack(
            'server set ' + '--name ' + new_name + ' ' + name
        )
        self.assertOutput("", raw_output)
        cmd_output = self.openstack(
            'server show ' + new_name,
            parse_output=True,
        )
        self.assertEqual(
            new_name,
            cmd_output["name"],
        )
        # Put it back so we clean up properly
        raw_output = self.openstack(
            'server set ' + '--name ' + name + ' ' + new_name
        )
        self.assertOutput("", raw_output)

    def test_server_show(self):
        """Test server show"""
        cmd_output = self.server_create()
        name = cmd_output['name']

        # Simple show
        cmd_output = json.loads(self.openstack(f'server show -f json {name}'))
        self.assertEqual(
            name,
            cmd_output["name"],
        )

        # Show diagnostics
        cmd_output = json.loads(
            self.openstack(f'server show -f json {name} --diagnostics')
        )
        self.assertIn('driver', cmd_output)

        # Show topology
        cmd_output = json.loads(
            self.openstack(
                f'server show -f json {name} --topology '
                f'--os-compute-api-version 2.78'
            )
        )
        self.assertIn('topology', cmd_output)

    def test_server_actions(self):
        """Test server action pairs

        suspend/resume
        pause/unpause
        rescue/unrescue
        lock/unlock
        """
        cmd_output = self.server_create()
        name = cmd_output['name']

        # suspend
        raw_output = self.openstack('server suspend ' + name)
        self.assertEqual("", raw_output)
        self.wait_for_status(name, "SUSPENDED")

        # resume
        raw_output = self.openstack('server resume ' + name)
        self.assertEqual("", raw_output)
        self.wait_for_status(name, "ACTIVE")

        # pause
        raw_output = self.openstack('server pause ' + name)
        self.assertEqual("", raw_output)
        self.wait_for_status(name, "PAUSED")

        # unpause
        raw_output = self.openstack('server unpause ' + name)
        self.assertEqual("", raw_output)
        self.wait_for_status(name, "ACTIVE")

        # rescue
        raw_output = self.openstack('server rescue ' + name)
        self.assertEqual("", raw_output)
        self.wait_for_status(name, "RESCUE")

        # unrescue
        raw_output = self.openstack('server unrescue ' + name)
        self.assertEqual("", raw_output)
        self.wait_for_status(name, "ACTIVE")

        # rescue with image
        raw_output = self.openstack(
            'server rescue --image ' + self.image_name + ' ' + name
        )
        self.assertEqual("", raw_output)
        self.wait_for_status(name, "RESCUE")

        # unrescue
        raw_output = self.openstack('server unrescue ' + name)
        self.assertEqual("", raw_output)
        self.wait_for_status(name, "ACTIVE")

        # lock
        raw_output = self.openstack('server lock ' + name)
        self.assertEqual("", raw_output)
        # NOTE(dtroyer): No way to verify this status???

        # unlock
        raw_output = self.openstack('server unlock ' + name)
        self.assertEqual("", raw_output)
        # NOTE(dtroyer): No way to verify this status???

    def test_server_attach_detach_floating_ip(self):
        """Test floating ip create/delete; server add/remove floating ip"""
        if not self.haz_network:
            # NOTE(dtroyer): As of Ocata release Nova forces nova-network to
            #                run in a cells v1 configuration.  Floating IP
            #                and network functions currently do not work in
            #                the gate jobs so we have to skip this.  It is
            #                known to work tested against a Mitaka nova-net
            #                DevStack without cells.
            self.skipTest("No Network service present")

        def _chain_addresses(addresses):
            # Flatten a dict of lists mapping network names to IP addresses,
            # returning only the IP addresses
            #
            # >>> _chain_addresses({'private': ['10.1.0.32', '172.24.5.41']})
            # ['10.1.0.32', '172.24.5.41']
            return itertools.chain(*[*addresses.values()])

        cmd_output = self.server_create()
        name = cmd_output['name']
        self.wait_for_status(name, "ACTIVE")

        # attach ip
        cmd_output = self.openstack(
            'floating ip create ' + 'public',
            parse_output=True,
        )

        # Look for Neutron value first, then nova-net
        floating_ip = cmd_output.get(
            'floating_ip_address',
            cmd_output.get(
                'ip',
                None,
            ),
        )
        self.assertNotEqual('', cmd_output['id'])
        self.assertNotEqual('', floating_ip)
        self.addCleanup(
            self.openstack, 'floating ip delete ' + str(cmd_output['id'])
        )

        raw_output = self.openstack(
            'server add floating ip ' + name + ' ' + floating_ip
        )
        self.assertEqual("", raw_output)

        # Loop a few times since this is timing-sensitive
        # Just hard-code it for now, since there is no pause and it is
        # racy we shouldn't have to wait too long, a minute seems reasonable
        wait_time = 0
        while wait_time < 60:
            cmd_output = self.openstack(
                'server show ' + name,
                parse_output=True,
            )
            if floating_ip not in _chain_addresses(cmd_output['addresses']):
                # Hang out for a bit and try again
                print('retrying floating IP check')
                wait_time += 10
                time.sleep(10)
            else:
                break

        self.assertIn(
            floating_ip,
            _chain_addresses(cmd_output['addresses']),
        )

        # detach ip
        raw_output = self.openstack(
            'server remove floating ip ' + name + ' ' + floating_ip
        )
        self.assertEqual("", raw_output)

        # Loop a few times since this is timing-sensitive
        # Just hard-code it for now, since there is no pause and it is
        # racy we shouldn't have to wait too long, a minute seems reasonable
        wait_time = 0
        while wait_time < 60:
            cmd_output = self.openstack(
                'server show ' + name,
                parse_output=True,
            )
            if floating_ip in _chain_addresses(cmd_output['addresses']):
                # Hang out for a bit and try again
                print('retrying floating IP check')
                wait_time += 10
                time.sleep(10)
            else:
                break

        cmd_output = self.openstack(
            'server show ' + name,
            parse_output=True,
        )
        self.assertNotIn(
            floating_ip,
            _chain_addresses(cmd_output['addresses']),
        )

    def test_server_reboot(self):
        """Test server reboot"""
        cmd_output = self.server_create()
        name = cmd_output['name']

        # reboot
        raw_output = self.openstack('server reboot ' + name)
        self.assertEqual("", raw_output)
        self.wait_for_status(name, "ACTIVE")

    def test_server_boot_from_volume(self):
        """Test server create from volume, server delete"""
        # get volume status wait function
        volume_wait_for = volume_common.BaseVolumeTests.wait_for_status

        # get image size
        cmd_output = self.openstack(
            'image show ' + self.image_name,
            parse_output=True,
        )
        try:
            image_size = cmd_output['min_disk']
            if image_size < 1:
                image_size = 1
        except ValueError:
            image_size = 1

        # create volume from image
        volume_name = uuid.uuid4().hex
        cmd_output = self.openstack(
            'volume create '
            + '--image '
            + self.image_name
            + ' '
            + '--size '
            + str(image_size)
            + ' '
            + volume_name,
            parse_output=True,
        )
        self.assertIsNotNone(cmd_output["id"])
        self.addCleanup(self.openstack, 'volume delete ' + volume_name)
        self.assertEqual(
            volume_name,
            cmd_output['name'],
        )
        volume_wait_for("volume", volume_name, "available")

        # create empty volume
        empty_volume_name = uuid.uuid4().hex
        cmd_output = self.openstack(
            'volume create '
            + '--size '
            + str(image_size)
            + ' '
            + empty_volume_name,
            parse_output=True,
        )
        self.assertIsNotNone(cmd_output["id"])
        self.addCleanup(self.openstack, 'volume delete ' + empty_volume_name)
        self.assertEqual(
            empty_volume_name,
            cmd_output['name'],
        )
        volume_wait_for("volume", empty_volume_name, "available")

        # create server
        server_name = uuid.uuid4().hex
        server = self.openstack(
            'server create '
            + '--flavor '
            + self.flavor_name
            + ' '
            + '--volume '
            + volume_name
            + ' '
            + '--block-device-mapping vdb='
            + empty_volume_name
            + ' '
            + self.network_arg
            + ' '
            + '--wait '
            + server_name,
            parse_output=True,
        )
        self.assertIsNotNone(server["id"])
        self.addCleanup(self.openstack, 'server delete --wait ' + server_name)
        self.assertEqual(
            server_name,
            server['name'],
        )

        # check that image indicates server "booted from volume"
        self.assertEqual(
            v2_server.IMAGE_STRING_FOR_BFV,
            server['image'],
        )
        # check server list too
        servers = self.openstack(
            'server list',
            parse_output=True,
        )
        self.assertEqual(v2_server.IMAGE_STRING_FOR_BFV, servers[0]['Image'])

        # check volumes
        cmd_output = self.openstack(
            'volume show ' + volume_name,
            parse_output=True,
        )
        attachments = cmd_output['attachments']
        self.assertEqual(
            1,
            len(attachments),
        )
        self.assertEqual(
            server['id'],
            attachments[0]['server_id'],
        )
        self.assertEqual(
            "in-use",
            cmd_output['status'],
        )

        # NOTE(dtroyer): Prior to https://review.opendev.org/#/c/407111
        #                --block-device-mapping was ignored if --volume
        #                present on the command line.  Now we should see the
        #                attachment.
        cmd_output = self.openstack(
            'volume show ' + empty_volume_name,
            parse_output=True,
        )
        attachments = cmd_output['attachments']
        self.assertEqual(
            1,
            len(attachments),
        )
        self.assertEqual(
            server['id'],
            attachments[0]['server_id'],
        )
        self.assertEqual(
            "in-use",
            cmd_output['status'],
        )

    def _test_server_boot_with_bdm_volume(self, use_legacy):
        """Test server create from volume, server delete"""
        # get volume status wait function
        volume_wait_for = volume_common.BaseVolumeTests.wait_for_status

        # create source empty volume
        volume_name = uuid.uuid4().hex
        cmd_output = self.openstack(
            'volume create ' + '--size 1 ' + volume_name,
            parse_output=True,
        )
        volume_id = cmd_output["id"]
        self.assertIsNotNone(volume_id)
        self.addCleanup(self.openstack, 'volume delete ' + volume_name)
        self.assertEqual(volume_name, cmd_output['name'])
        volume_wait_for("volume", volume_name, "available")

        if use_legacy:
            bdm_arg = f'--block-device-mapping vdb={volume_name}'
        else:
            bdm_arg = (
                f'--block-device '
                f'device_name=vdb,source_type=volume,boot_index=1,'
                f'uuid={volume_id}'
            )

        # create server
        server_name = uuid.uuid4().hex
        server = self.openstack(
            'server create '
            + '--flavor '
            + self.flavor_name
            + ' '
            + '--image '
            + self.image_name
            + ' '
            + bdm_arg
            + ' '
            + self.network_arg
            + ' '
            + '--wait '
            + server_name,
            parse_output=True,
        )
        self.assertIsNotNone(server["id"])
        self.addCleanup(self.openstack, 'server delete --wait ' + server_name)
        self.assertEqual(
            server_name,
            server['name'],
        )

        # check server volumes_attached, format is
        # {"volumes_attached": "id='2518bc76-bf0b-476e-ad6b-571973745bb5'",}
        cmd_output = self.openstack(
            'server show ' + server_name,
            parse_output=True,
        )
        volumes_attached = cmd_output['volumes_attached']
        self.assertIsNotNone(volumes_attached)

        # check volumes
        cmd_output = self.openstack(
            'volume show ' + volume_name,
            parse_output=True,
        )
        attachments = cmd_output['attachments']
        self.assertEqual(
            1,
            len(attachments),
        )
        self.assertEqual(
            server['id'],
            attachments[0]['server_id'],
        )
        self.assertEqual(
            "in-use",
            cmd_output['status'],
        )

    def test_server_boot_with_bdm_volume(self):
        """Test server create from image with bdm volume, server delete"""
        self._test_server_boot_with_bdm_volume(use_legacy=False)

    # TODO(stephenfin): Remove when we drop support for the
    # '--block-device-mapping' option
    def test_server_boot_with_bdm_volume_legacy(self):
        """Test server create from image with bdm volume, server delete"""
        self._test_server_boot_with_bdm_volume(use_legacy=True)

    def _test_server_boot_with_bdm_snapshot(self, use_legacy):
        """Test server create from image with bdm snapshot, server delete"""
        # get volume status wait function
        volume_wait_for = volume_common.BaseVolumeTests.wait_for_status
        volume_wait_for_delete = volume_common.BaseVolumeTests.wait_for_delete

        # create source empty volume
        empty_volume_name = uuid.uuid4().hex
        cmd_output = self.openstack(
            'volume create ' + '--size 1 ' + empty_volume_name,
            parse_output=True,
        )
        self.assertIsNotNone(cmd_output["id"])
        self.addCleanup(self.openstack, 'volume delete ' + empty_volume_name)
        self.assertEqual(empty_volume_name, cmd_output['name'])
        volume_wait_for("volume", empty_volume_name, "available")

        # create snapshot of source empty volume
        empty_snapshot_name = uuid.uuid4().hex
        cmd_output = self.openstack(
            'volume snapshot create '
            + '--volume '
            + empty_volume_name
            + ' '
            + empty_snapshot_name,
            parse_output=True,
        )
        empty_snapshot_id = cmd_output["id"]
        self.assertIsNotNone(empty_snapshot_id)
        # Deleting volume snapshot take time, so we need to wait until the
        # snapshot goes. Entries registered by self.addCleanup will be called
        # in the reverse order, so we need to register wait_for_delete first.
        self.addCleanup(
            volume_wait_for_delete, 'volume snapshot', empty_snapshot_name
        )
        self.addCleanup(
            self.openstack, 'volume snapshot delete ' + empty_snapshot_name
        )
        self.assertEqual(
            empty_snapshot_name,
            cmd_output['name'],
        )
        volume_wait_for("volume snapshot", empty_snapshot_name, "available")

        if use_legacy:
            bdm_arg = (
                f'--block-device-mapping '
                f'vdb={empty_snapshot_name}:snapshot:1:true'
            )
        else:
            bdm_arg = (
                f'--block-device '
                f'device_name=vdb,uuid={empty_snapshot_id},'
                f'source_type=snapshot,volume_size=1,'
                f'delete_on_termination=true,boot_index=1'
            )

        # create server with bdm snapshot
        server_name = uuid.uuid4().hex
        server = self.openstack(
            'server create '
            + '--flavor '
            + self.flavor_name
            + ' '
            + '--image '
            + self.image_name
            + ' '
            + bdm_arg
            + ' '
            + self.network_arg
            + ' '
            + '--wait '
            + server_name,
            parse_output=True,
        )
        self.assertIsNotNone(server["id"])
        self.assertEqual(
            server_name,
            server['name'],
        )
        self.wait_for_status(server_name, 'ACTIVE')

        # check server volumes_attached, format is
        # {"volumes_attached": "id='2518bc76-bf0b-476e-ad6b-571973745bb5'",}
        cmd_output = self.openstack(
            'server show ' + server_name,
            parse_output=True,
        )
        volumes_attached = cmd_output['volumes_attached']
        self.assertIsNotNone(volumes_attached)
        attached_volume_id = volumes_attached[0]["id"]

        # check the volume that attached on server
        cmd_output = self.openstack(
            'volume show ' + attached_volume_id,
            parse_output=True,
        )
        attachments = cmd_output['attachments']
        self.assertEqual(
            1,
            len(attachments),
        )
        self.assertEqual(
            server['id'],
            attachments[0]['server_id'],
        )
        self.assertEqual(
            "in-use",
            cmd_output['status'],
        )

        # delete server, then check the attached volume had been deleted,
        # <delete-on-terminate>=true
        self.openstack('server delete --wait ' + server_name)
        cmd_output = self.openstack(
            'volume list',
            parse_output=True,
        )
        target_volume = [
            each_volume
            for each_volume in cmd_output
            if each_volume['ID'] == attached_volume_id
        ]
        if target_volume:
            # check the attached volume is 'deleting' status
            self.assertEqual('deleting', target_volume[0]['Status'])
        else:
            # the attached volume had been deleted
            pass

    def test_server_boot_with_bdm_snapshot(self):
        """Test server create from image with bdm snapshot, server delete"""
        self._test_server_boot_with_bdm_snapshot(use_legacy=False)

    # TODO(stephenfin): Remove when we drop support for the
    # '--block-device-mapping' option
    def test_server_boot_with_bdm_snapshot_legacy(self):
        """Test server create from image with bdm snapshot, server delete"""
        self._test_server_boot_with_bdm_snapshot(use_legacy=True)

    def _test_server_boot_with_bdm_image(self, use_legacy):
        # Tests creating a server where the root disk is backed by the given
        # --image but a --block-device-mapping with type=image is provided so
        # that the compute service creates a volume from that image and
        # attaches it as a non-root volume on the server. The block device is
        # marked as delete_on_termination=True so it will be automatically
        # deleted when the server is deleted.

        if use_legacy:
            # This means create a 1GB volume from the specified image, attach
            # it to the server at /dev/vdb and delete the volume when the
            # server is deleted.
            bdm_arg = (
                f'--block-device-mapping vdb={self.image_name}:image:1:true '
            )
        else:
            # get image ID
            cmd_output = self.openstack(
                'image show ' + self.image_name,
                parse_output=True,
            )
            image_id = cmd_output['id']

            # This means create a 1GB volume from the specified image, attach
            # it to the server at /dev/vdb and delete the volume when the
            # server is deleted.
            bdm_arg = (
                f'--block-device '
                f'device_name=vdb,uuid={image_id},'
                f'source_type=image,volume_size=1,'
                f'delete_on_termination=true,boot_index=1'
            )

        # create server with bdm type=image
        # NOTE(mriedem): This test is a bit unrealistic in that specifying the
        # same image in the block device as the --image option does not really
        # make sense, but we just want to make sure everything is processed
        # as expected where nova creates a volume from the image and attaches
        # that volume to the server.
        server_name = uuid.uuid4().hex
        server = self.openstack(
            'server create '
            + '--flavor '
            + self.flavor_name
            + ' '
            + '--image '
            + self.image_name
            + ' '
            + bdm_arg
            + ' '
            + self.network_arg
            + ' '
            + '--wait '
            + server_name,
            parse_output=True,
        )
        self.assertIsNotNone(server["id"])
        self.assertEqual(
            server_name,
            server['name'],
        )
        self.wait_for_status(server_name, 'ACTIVE')

        # check server volumes_attached, format is
        # {"volumes_attached": "id='2518bc76-bf0b-476e-ad6b-571973745bb5'",}
        cmd_output = self.openstack(
            'server show ' + server_name,
            parse_output=True,
        )
        volumes_attached = cmd_output['volumes_attached']
        self.assertIsNotNone(volumes_attached)
        attached_volume_id = volumes_attached[0]["id"]

        # check the volume that attached on server
        cmd_output = self.openstack(
            'volume show ' + attached_volume_id,
            parse_output=True,
        )
        attachments = cmd_output['attachments']
        self.assertEqual(
            1,
            len(attachments),
        )
        self.assertEqual(
            server['id'],
            attachments[0]['server_id'],
        )
        self.assertEqual(
            "in-use",
            cmd_output['status'],
        )
        # TODO(mriedem): If we can parse the volume_image_metadata field from
        # the volume show output we could assert the image_name is what we
        # specified. volume_image_metadata is something like this:
        # {u'container_format': u'bare', u'min_ram': u'0',
        # u'disk_format': u'qcow2', u'image_name': u'cirros-0.4.0-x86_64-disk',
        # u'image_id': u'05496c83-e2df-4c2f-9e48-453b6e49160d',
        # u'checksum': u'443b7623e27ecf03dc9e01ee93f67afe', u'min_disk': u'0',
        # u'size': u'12716032'}

        # delete server, then check the attached volume has been deleted
        self.openstack('server delete --wait ' + server_name)
        cmd_output = self.openstack(
            'volume list',
            parse_output=True,
        )
        target_volume = [
            each_volume
            for each_volume in cmd_output
            if each_volume['ID'] == attached_volume_id
        ]
        if target_volume:
            # check the attached volume is 'deleting' status
            self.assertEqual('deleting', target_volume[0]['Status'])
        else:
            # the attached volume had been deleted
            pass

    def test_server_boot_with_bdm_image(self):
        self._test_server_boot_with_bdm_image(use_legacy=False)

    # TODO(stephenfin): Remove when we drop support for the
    # '--block-device-mapping' option
    def test_server_boot_with_bdm_image_legacy(self):
        self._test_server_boot_with_bdm_image(use_legacy=True)

    def test_boot_from_volume(self):
        # Tests creating a server using --image and --boot-from-volume where
        # the compute service will create a root volume of the specified size
        # using the provided image, attach it as the root disk for the server
        # and not delete the volume when the server is deleted.
        server_name = uuid.uuid4().hex
        server = self.openstack(
            'server create '
            + '--flavor '
            + self.flavor_name
            + ' '
            + '--image '
            + self.image_name
            + ' '
            + '--boot-from-volume 1 '
            + self.network_arg  # create a 1GB volume from the image
            + ' '
            + '--wait '
            + server_name,
            parse_output=True,
        )
        self.assertIsNotNone(server["id"])
        self.assertEqual(
            server_name,
            server['name'],
        )
        self.wait_for_status(server_name, 'ACTIVE')

        # check server volumes_attached, format is
        # {"volumes_attached": "id='2518bc76-bf0b-476e-ad6b-571973745bb5'",}
        cmd_output = self.openstack(
            'server show ' + server_name,
            parse_output=True,
        )
        volumes_attached = cmd_output['volumes_attached']
        self.assertIsNotNone(volumes_attached)
        attached_volume_id = volumes_attached[0]["id"]
        for vol in volumes_attached:
            self.assertIsNotNone(vol['id'])
            # Don't leak the volume when the test exits.
            self.addCleanup(self.openstack, 'volume delete ' + vol['id'])

        # Since the server is volume-backed the GET /servers/{server_id}
        # response will have image='N/A (booted from volume)'.
        self.assertEqual(v2_server.IMAGE_STRING_FOR_BFV, cmd_output['image'])

        # check the volume that attached on server
        cmd_output = self.openstack(
            'volume show ' + volumes_attached[0]["id"],
            parse_output=True,
        )
        # The volume size should be what we specified on the command line.
        self.assertEqual(1, int(cmd_output['size']))
        attachments = cmd_output['attachments']
        self.assertEqual(
            1,
            len(attachments),
        )
        self.assertEqual(
            server['id'],
            attachments[0]['server_id'],
        )
        self.assertEqual(
            "in-use",
            cmd_output['status'],
        )
        # TODO(mriedem): If we can parse the volume_image_metadata field from
        # the volume show output we could assert the image_name is what we
        # specified. volume_image_metadata is something like this:
        # {u'container_format': u'bare', u'min_ram': u'0',
        # u'disk_format': u'qcow2', u'image_name': u'cirros-0.4.0-x86_64-disk',
        # u'image_id': u'05496c83-e2df-4c2f-9e48-453b6e49160d',
        # u'checksum': u'443b7623e27ecf03dc9e01ee93f67afe', u'min_disk': u'0',
        # u'size': u'12716032'}

        # delete server, then check the attached volume was not deleted
        self.openstack('server delete --wait ' + server_name)
        cmd_output = self.openstack(
            'volume show ' + attached_volume_id,
            parse_output=True,
        )
        # check the volume is in 'available' status
        self.assertEqual('available', cmd_output['status'])

    def test_server_create_with_none_network(self):
        """Test server create with none network option."""
        server_name = uuid.uuid4().hex
        server = self.openstack(
            # auto/none enable in nova micro version (v2.37+)
            '--os-compute-api-version 2.37 '
            + 'server create '
            + '--flavor '
            + self.flavor_name
            + ' '
            + '--image '
            + self.image_name
            + ' '
            + '--nic none '
            + server_name,
            parse_output=True,
        )
        self.assertIsNotNone(server["id"])
        self.addCleanup(self.openstack, 'server delete --wait ' + server_name)
        self.assertEqual(server_name, server['name'])
        self.wait_for_status(server_name, "ACTIVE")
        server = self.openstack(
            'server show ' + server_name,
            parse_output=True,
        )
        self.assertEqual({}, server['addresses'])

    def test_server_create_with_security_group(self):
        """Test server create with security group ID and name"""
        if not self.haz_network:
            # NOTE(dtroyer): As of Ocata release Nova forces nova-network to
            #                run in a cells v1 configuration.  Security group
            #                and network functions currently do not work in
            #                the gate jobs so we have to skip this.  It is
            #                known to work tested against a Mitaka nova-net
            #                DevStack without cells.
            self.skipTest("No Network service present")
        # Create two security group, use name and ID to create server
        sg_name1 = uuid.uuid4().hex
        security_group1 = self.openstack(
            'security group create ' + sg_name1,
            parse_output=True,
        )
        self.addCleanup(self.openstack, 'security group delete ' + sg_name1)
        sg_name2 = uuid.uuid4().hex
        security_group2 = self.openstack(
            'security group create ' + sg_name2,
            parse_output=True,
        )
        self.addCleanup(self.openstack, 'security group delete ' + sg_name2)

        server_name = uuid.uuid4().hex
        server = self.openstack(
            'server create '
            + '--flavor '
            + self.flavor_name
            + ' '
            + '--image '
            + self.image_name
            + ' '
            +
            # Security group id is integer in nova-network, convert to string
            '--security-group '
            + str(security_group1['id'])
            + ' '
            + '--security-group '
            + security_group2['name']
            + ' '
            + self.network_arg
            + ' '
            + server_name,
            parse_output=True,
        )
        self.addCleanup(self.openstack, 'server delete --wait ' + server_name)

        self.assertIsNotNone(server['id'])
        self.assertEqual(server_name, server['name'])
        sec_grp = ""
        for sec in server['security_groups']:
            sec_grp += sec['name']
        self.assertIn(str(security_group1['id']), sec_grp)
        self.assertIn(str(security_group2['id']), sec_grp)
        self.wait_for_status(server_name, 'ACTIVE')
        server = self.openstack(
            'server show ' + server_name,
            parse_output=True,
        )
        # check if security group exists in list
        sec_grp = ""
        for sec in server['security_groups']:
            sec_grp += sec['name']
        self.assertIn(sg_name1, sec_grp)
        self.assertIn(sg_name2, sec_grp)

    def test_server_create_with_empty_network_option_latest(self):
        """Test server create with empty network option in nova 2.latest."""
        server_name = uuid.uuid4().hex
        try:
            self.openstack(
                # auto/none enable in nova micro version (v2.37+)
                '--os-compute-api-version 2.37 '
                + 'server create '
                + '--flavor '
                + self.flavor_name
                + ' '
                + '--image '
                + self.image_name
                + ' '
                + server_name
            )
        except exceptions.CommandFailed as e:
            # If we got here, it shouldn't be because a nics value wasn't
            # provided to the server; it is likely due to something else in
            # the functional tests like there being multiple available
            # networks and the test didn't specify a specific network.
            self.assertNotIn(
                'nics are required after microversion 2.36', e.stderr
            )

    def test_server_add_remove_network(self):
        name = uuid.uuid4().hex
        cmd_output = self.openstack(
            'server create '
            + '--network private '
            + '--flavor '
            + self.flavor_name
            + ' '
            + '--image '
            + self.image_name
            + ' '
            + '--wait '
            + name,
            parse_output=True,
        )

        self.assertIsNotNone(cmd_output['id'])
        self.assertEqual(name, cmd_output['name'])
        self.addCleanup(self.openstack, 'server delete --wait ' + name)

        # add network and check 'public' is in server show
        self.openstack('server add network ' + name + ' public')

        wait_time = 0
        while wait_time < 60:
            cmd_output = self.openstack(
                'server show ' + name,
                parse_output=True,
            )
            if 'public' not in cmd_output['addresses']:
                # Hang out for a bit and try again
                print('retrying add network check')
                wait_time += 10
                time.sleep(10)
            else:
                break
        addresses = cmd_output['addresses']
        self.assertIn('public', addresses)

        # remove network and check 'public' is not in server show
        self.openstack('server remove network ' + name + ' public')

        wait_time = 0
        while wait_time < 60:
            cmd_output = self.openstack(
                'server show ' + name,
                parse_output=True,
            )
            if 'public' in cmd_output['addresses']:
                # Hang out for a bit and try again
                print('retrying remove network check')
                wait_time += 10
                time.sleep(10)
            else:
                break

        addresses = cmd_output['addresses']
        self.assertNotIn('public', addresses)

    def test_server_add_remove_port(self):
        name = uuid.uuid4().hex
        cmd_output = self.openstack(
            'server create '
            + '--network private '
            + '--flavor '
            + self.flavor_name
            + ' '
            + '--image '
            + self.image_name
            + ' '
            + '--wait '
            + name,
            parse_output=True,
        )

        self.assertIsNotNone(cmd_output['id'])
        self.assertEqual(name, cmd_output['name'])
        self.addCleanup(self.openstack, 'server delete --wait ' + name)

        # create port, record one of its ip address
        port_name = uuid.uuid4().hex

        cmd_output = self.openstack(
            'port list',
            parse_output=True,
        )
        self.assertNotIn(port_name, cmd_output)

        cmd_output = self.openstack(
            'port create ' + '--network private ' + port_name,
            parse_output=True,
        )
        self.assertIsNotNone(cmd_output['id'])
        ip_address = cmd_output['fixed_ips'][0]['ip_address']
        self.addCleanup(self.openstack, 'port delete ' + port_name)

        # add port to server, assert the ip address of the port appears
        self.openstack('server add port ' + name + ' ' + port_name)

        wait_time = 0
        while wait_time < 60:
            cmd_output = self.openstack(
                'server show ' + name,
                parse_output=True,
            )
            if ip_address not in cmd_output['addresses']['private']:
                # Hang out for a bit and try again
                print('retrying add port check')
                wait_time += 10
                time.sleep(10)
            else:
                break
        addresses = cmd_output['addresses']['private']
        self.assertIn(ip_address, addresses)

        # remove port, assert the ip address of the port doesn't appear
        self.openstack('server remove port ' + name + ' ' + port_name)

        wait_time = 0
        while wait_time < 60:
            cmd_output = self.openstack(
                'server show ' + name,
                parse_output=True,
            )
            if ip_address in cmd_output['addresses']['private']:
                # Hang out for a bit and try again
                print('retrying remove port check')
                wait_time += 10
                time.sleep(10)
            else:
                break
        addresses = cmd_output['addresses']['private']
        self.assertNotIn(ip_address, addresses)

    def test_server_add_fixed_ip(self):
        name = uuid.uuid4().hex
        cmd_output = self.openstack(
            'server create '
            + '--network private '
            + '--flavor '
            + self.flavor_name
            + ' '
            + '--image '
            + self.image_name
            + ' '
            + '--wait '
            + name,
            parse_output=True,
        )

        self.assertIsNotNone(cmd_output['id'])
        self.assertEqual(name, cmd_output['name'])
        self.addCleanup(self.openstack, 'server delete --wait ' + name)

        # create port, record its ip address to use in later call,
        # then delete - this is to figure out what should be a free ip
        # in the subnet
        port_name = uuid.uuid4().hex

        cmd_output = self.openstack(
            'port list',
            parse_output=True,
        )
        self.assertNotIn(port_name, cmd_output)

        cmd_output = self.openstack(
            'port create ' + '--network private ' + port_name,
            parse_output=True,
        )
        self.assertIsNotNone(cmd_output['id'])
        ip_address = cmd_output['fixed_ips'][0]['ip_address']
        self.openstack('port delete ' + port_name)

        # add fixed ip to server, assert the ip address appears
        self.openstack(
            'server add fixed ip --fixed-ip-address '
            + ip_address
            + ' '
            + name
            + ' private'
        )

        wait_time = 0
        while wait_time < 60:
            cmd_output = self.openstack(
                'server show ' + name,
                parse_output=True,
            )
            if ip_address not in cmd_output['addresses']['private']:
                # Hang out for a bit and try again
                print('retrying add fixed ip check')
                wait_time += 10
                time.sleep(10)
            else:
                break
        addresses = cmd_output['addresses']['private']
        self.assertIn(ip_address, addresses)

    def test_server_add_remove_security_group(self):
        name = uuid.uuid4().hex
        cmd_output = self.openstack(
            'server create '
            + '--network private '
            + '--flavor '
            + self.flavor_name
            + ' '
            + '--image '
            + self.image_name
            + ' '
            + '--wait '
            + name,
            parse_output=True,
        )

        self.assertIsNotNone(cmd_output['id'])
        self.assertEqual(name, cmd_output['name'])
        self.addCleanup(self.openstack, 'server delete --wait ' + name)

        # create security group
        security_group_name = uuid.uuid4().hex

        cmd_output = self.openstack(
            'security group list',
            parse_output=True,
        )
        self.assertNotIn(security_group_name, cmd_output)

        cmd_output = self.openstack(
            'security group create ' + security_group_name,
            parse_output=True,
        )
        self.assertIsNotNone(cmd_output['id'])
        self.addCleanup(
            self.openstack, 'security group delete ' + security_group_name
        )

        # add security group to server, assert the name of the security group
        # appears
        self.openstack(
            'server add security group ' + name + ' ' + security_group_name
        )

        wait_time = 0
        while wait_time < 60:
            cmd_output = self.openstack(
                'server show ' + name,
                parse_output=True,
            )
            if security_group_name not in [
                x['name'] for x in cmd_output['security_groups']
            ]:
                # Hang out for a bit and try again
                print('retrying add security group check')
                wait_time += 10
                time.sleep(10)
            else:
                break
        security_groups = [x['name'] for x in cmd_output['security_groups']]
        self.assertIn(security_group_name, security_groups)

        # remove security group, assert the name of the security group doesn't
        # appear
        self.openstack(
            'server remove security group ' + name + ' ' + security_group_name
        )

        wait_time = 0
        while wait_time < 60:
            cmd_output = self.openstack(
                'server show ' + name,
                parse_output=True,
            )
            if security_group_name not in [
                x['name'] for x in cmd_output['security_groups']
            ]:
                # Hang out for a bit and try again
                print('retrying remove security group check')
                wait_time += 10
                time.sleep(10)
            else:
                break
        security_groups = [x['name'] for x in cmd_output['security_groups']]
        self.assertNotIn(security_group_name, security_groups)

    def test_server_add_remove_volume(self):
        volume_wait_for = volume_common.BaseVolumeTests.wait_for_status

        server_name = uuid.uuid4().hex
        cmd_output = self.openstack(
            'server create '
            + '--network private '
            + '--flavor '
            + self.flavor_name
            + ' '
            + '--image '
            + self.image_name
            + ' '
            + '--wait '
            + server_name,
            parse_output=True,
        )

        self.assertIsNotNone(cmd_output['id'])
        self.assertEqual(server_name, cmd_output['name'])
        self.addCleanup(self.openstack, 'server delete --wait ' + server_name)
        server_id = cmd_output['id']

        volume_name = uuid.uuid4().hex
        cmd_output = self.openstack(
            'volume create ' + '--size 1 ' + volume_name,
            parse_output=True,
        )

        self.assertIsNotNone(cmd_output['id'])
        self.assertEqual(volume_name, cmd_output['name'])
        volume_wait_for('volume', volume_name, 'available')
        self.addCleanup(self.openstack, 'volume delete ' + volume_name)
        volume_id = cmd_output['id']

        cmd_output = self.openstack(
            'server add volume '
            + server_name
            + ' '
            + volume_name
            + ' '
            + '--tag bar',
            parse_output=True,
        )

        self.assertEqual(server_id, cmd_output['Server ID'])
        self.assertEqual(volume_id, cmd_output['Volume ID'])

        cmd_output = self.openstack(
            'server volume list ' + server_name,
            parse_output=True,
        )

        self.assertEqual(server_id, cmd_output[0]['Server ID'])
        self.assertEqual(volume_id, cmd_output[0]['Volume ID'])

        volume_wait_for('volume', volume_name, 'in-use')

        cmd_output = self.openstack(
            'server event list ' + server_name,
            parse_output=True,
        )
        self.assertEqual(2, len(cmd_output))
        self.assertIn('attach_volume', {x['Action'] for x in cmd_output})

        self.openstack(
            'server remove volume ' + server_name + ' ' + volume_name
        )
        volume_wait_for('volume', volume_name, 'available')

        cmd_output = self.openstack(
            'server event list ' + server_name,
            parse_output=True,
        )
        self.assertEqual(3, len(cmd_output))
        self.assertIn('detach_volume', {x['Action'] for x in cmd_output})

        raw_output = self.openstack('server volume list ' + server_name)
        self.assertEqual('\n', raw_output)

    def test_server_stop_start(self):
        """Test server stop, start"""
        server_name = uuid.uuid4().hex
        cmd_output = self.openstack(
            'server create '
            + '--network private '
            + '--flavor '
            + self.flavor_name
            + ' '
            + '--image '
            + self.image_name
            + ' '
            + '--wait '
            + server_name,
            parse_output=True,
        )

        self.assertIsNotNone(cmd_output['id'])
        self.assertEqual(server_name, cmd_output['name'])
        self.addCleanup(self.openstack, 'server delete --wait ' + server_name)
        server_id = cmd_output['id']

        cmd_output = self.openstack(
            'server stop ' + server_name,
        )
        self.assertEqual("", cmd_output)

        # This is our test that the request succeeded. If it doesn't transition
        # to SHUTOFF then it didn't work.
        self.wait_for_status(server_id, "SHUTOFF")

        cmd_output = self.openstack(
            'server start ' + server_name,
        )
        self.assertEqual("", cmd_output)

        # As above, this is our test that the request succeeded. If it doesn't
        # transition to ACTIVE then it didn't work.
        self.wait_for_status(server_id, "ACTIVE")

    def test_server_migration_list(self):
        # Verify that the command does not raise an exception when we list
        # migrations, including when we specify a query.
        self.openstack('server migration list')
        self.openstack('server migration list --limit 1')
