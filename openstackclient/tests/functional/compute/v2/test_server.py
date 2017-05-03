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

from tempest.lib import exceptions

from openstackclient.tests.functional import base
from openstackclient.tests.functional.compute.v2 import common
from openstackclient.tests.functional.volume.v2 import test_volume


class ServerTests(common.ComputeTestCase):
    """Functional tests for openstack server commands"""

    @classmethod
    def setUpClass(cls):
        cls.haz_network = base.is_service_enabled('network')

    def test_server_list(self):
        """Test server list, set"""
        cmd_output = self.server_create()
        name1 = cmd_output['name']
        cmd_output = self.server_create()
        name2 = cmd_output['name']
        self.wait_for_status(name1, "ACTIVE")
        self.wait_for_status(name2, "ACTIVE")

        cmd_output = json.loads(self.openstack(
            'server list -f json'
        ))
        col_name = [x["Name"] for x in cmd_output]
        self.assertIn(name1, col_name)
        self.assertIn(name2, col_name)

        # Test list --status PAUSED
        raw_output = self.openstack('server pause ' + name2)
        self.assertEqual("", raw_output)
        self.wait_for_status(name2, "PAUSED")
        cmd_output = json.loads(self.openstack(
            'server list -f json ' +
            '--status ACTIVE'
        ))
        col_name = [x["Name"] for x in cmd_output]
        self.assertIn(name1, col_name)
        self.assertNotIn(name2, col_name)
        cmd_output = json.loads(self.openstack(
            'server list -f json ' +
            '--status PAUSED'
        ))
        col_name = [x["Name"] for x in cmd_output]
        self.assertNotIn(name1, col_name)
        self.assertIn(name2, col_name)

    def test_server_set(self):
        """Test server create, delete, set, show"""
        cmd_output = self.server_create()
        name = cmd_output['name']
        # self.wait_for_status(name, "ACTIVE")

        # Have a look at some other fields
        flavor = json.loads(self.openstack(
            'flavor show -f json ' +
            self.flavor_name
        ))
        self.assertEqual(
            self.flavor_name,
            flavor['name'],
        )
        self.assertEqual(
            '%s (%s)' % (flavor['name'], flavor['id']),
            cmd_output["flavor"],
        )
        image = json.loads(self.openstack(
            'image show -f json ' +
            self.image_name
        ))
        self.assertEqual(
            self.image_name,
            image['name'],
        )
        self.assertEqual(
            '%s (%s)' % (image['name'], image['id']),
            cmd_output["image"],
        )

        # Test properties set
        raw_output = self.openstack(
            'server set ' +
            '--property a=b --property c=d ' +
            name
        )
        self.assertOutput('', raw_output)

        cmd_output = json.loads(self.openstack(
            'server show -f json ' +
            name
        ))
        # Really, shouldn't this be a list?
        self.assertEqual(
            "a='b', c='d'",
            cmd_output['properties'],
        )

        raw_output = self.openstack(
            'server unset ' +
            '--property a ' +
            name
        )
        cmd_output = json.loads(self.openstack(
            'server show -f json ' +
            name
        ))
        self.assertEqual(
            "c='d'",
            cmd_output['properties'],
        )

        # Test set --name
        new_name = uuid.uuid4().hex
        raw_output = self.openstack(
            'server set ' +
            '--name ' + new_name + ' ' +
            name
        )
        self.assertOutput("", raw_output)
        cmd_output = json.loads(self.openstack(
            'server show -f json ' +
            new_name
        ))
        self.assertEqual(
            new_name,
            cmd_output["name"],
        )
        # Put it back so we clean up properly
        raw_output = self.openstack(
            'server set ' +
            '--name ' + name + ' ' +
            new_name
        )
        self.assertOutput("", raw_output)

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
        self.assertNotEqual("", raw_output)
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

        cmd_output = self.server_create()
        name = cmd_output['name']
        self.wait_for_status(name, "ACTIVE")

        # attach ip
        cmd_output = json.loads(self.openstack(
            'floating ip create -f json ' +
            'public'
        ))

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
            self.openstack,
            'floating ip delete ' + str(cmd_output['id'])
        )

        raw_output = self.openstack(
            'server add floating ip ' +
            name + ' ' +
            floating_ip
        )
        self.assertEqual("", raw_output)
        cmd_output = json.loads(self.openstack(
            'server show -f json ' +
            name
        ))
        self.assertIn(
            floating_ip,
            cmd_output['addresses'],
        )

        # detach ip
        raw_output = self.openstack(
            'server remove floating ip ' +
            name + ' ' +
            floating_ip
        )
        self.assertEqual("", raw_output)

        cmd_output = json.loads(self.openstack(
            'server show -f json ' +
            name
        ))
        self.assertNotIn(
            floating_ip,
            cmd_output['addresses'],
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
        volume_wait_for = test_volume.VolumeTests(
            methodName='wait_for',
        ).wait_for

        # get image size
        cmd_output = json.loads(self.openstack(
            'image show -f json ' +
            self.image_name
        ))
        try:
            image_size = cmd_output['min_disk']
            if image_size < 1:
                image_size = 1
        except ValueError:
            image_size = 1

        # create volume from image
        volume_name = uuid.uuid4().hex
        cmd_output = json.loads(self.openstack(
            'volume create -f json ' +
            '--image ' + self.image_name + ' ' +
            '--size ' + str(image_size) + ' ' +
            volume_name
        ))
        self.assertIsNotNone(cmd_output["id"])
        self.addCleanup(self.openstack, 'volume delete ' + volume_name)
        self.assertEqual(
            volume_name,
            cmd_output['name'],
        )
        volume_wait_for("volume", volume_name, "available")

        # create empty volume
        empty_volume_name = uuid.uuid4().hex
        cmd_output = json.loads(self.openstack(
            'volume create -f json ' +
            '--size ' + str(image_size) + ' ' +
            empty_volume_name
        ))
        self.assertIsNotNone(cmd_output["id"])
        self.addCleanup(self.openstack, 'volume delete ' + empty_volume_name)
        self.assertEqual(
            empty_volume_name,
            cmd_output['name'],
        )
        volume_wait_for("volume", empty_volume_name, "available")

        # create server
        server_name = uuid.uuid4().hex
        server = json.loads(self.openstack(
            'server create -f json ' +
            '--flavor ' + self.flavor_name + ' ' +
            '--volume ' + volume_name + ' ' +
            '--block-device-mapping vdb=' + empty_volume_name + ' ' +
            self.network_arg + ' ' +
            '--wait ' +
            server_name
        ))
        self.assertIsNotNone(server["id"])
        self.addCleanup(self.openstack, 'server delete --wait ' + server_name)
        self.assertEqual(
            server_name,
            server['name'],
        )

        # check volumes
        cmd_output = json.loads(self.openstack(
            'volume show -f json ' +
            volume_name
        ))
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

        # NOTE(dtroyer): Prior to https://review.openstack.org/#/c/407111
        #                --block-device-mapping was ignored if --volume
        #                present on the command line.  Now we should see the
        #                attachment.
        cmd_output = json.loads(self.openstack(
            'volume show -f json ' +
            empty_volume_name
        ))
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

    def test_server_create_with_none_network(self):
        """Test server create with none network option."""
        server_name = uuid.uuid4().hex
        server = json.loads(self.openstack(
            # auto/none enable in nova micro version (v2.37+)
            '--os-compute-api-version 2.37 ' +
            'server create -f json ' +
            '--flavor ' + self.flavor_name + ' ' +
            '--image ' + self.image_name + ' ' +
            '--nic none ' +
            server_name
        ))
        self.assertIsNotNone(server["id"])
        self.addCleanup(self.openstack, 'server delete --wait ' + server_name)
        self.assertEqual(server_name, server['name'])
        self.wait_for_status(server_name, "ACTIVE")
        server = json.loads(self.openstack(
            'server show -f json ' + server_name
        ))
        self.assertIsNotNone(server['addresses'])
        self.assertEqual('', server['addresses'])

    def test_server_create_with_empty_network_option_latest(self):
        """Test server create with empty network option in nova 2.latest."""
        server_name = uuid.uuid4().hex
        try:
            self.openstack(
                # auto/none enable in nova micro version (v2.37+)
                '--os-compute-api-version 2.37 ' +
                'server create -f json ' +
                '--flavor ' + self.flavor_name + ' ' +
                '--image ' + self.image_name + ' ' +
                server_name
            )
        except exceptions.CommandFailed as e:
            self.assertIn('nics are required after microversion 2.36',
                          e.stderr)
        else:
            self.fail('CommandFailed should be raised.')
