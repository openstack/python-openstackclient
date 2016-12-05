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

from tempest.lib.common.utils import data_utils

from openstackclient.tests.functional import base
from openstackclient.tests.functional.volume.v2 import test_volume
from tempest.lib import exceptions


class ServerTests(base.TestCase):
    """Functional tests for openstack server commands."""

    @classmethod
    def get_flavor(cls):
        # NOTE(rtheis): Get cirros256 or m1.tiny flavors since functional
        # tests may create other flavors.
        flavors = cls.openstack('flavor list -c Name -f value').split('\n')
        server_flavor = None
        for flavor in flavors:
            if flavor in ['m1.tiny', 'cirros256']:
                server_flavor = flavor
                break
        return server_flavor

    @classmethod
    def get_image(cls):
        # NOTE(rtheis): Get cirros image since functional tests may
        # create other images.
        images = cls.openstack('image list -c Name -f value').split('\n')
        server_image = None
        for image in images:
            if image.startswith('cirros-') and image.endswith('-uec'):
                server_image = image
                break
        return server_image

    @classmethod
    def get_network(cls):
        try:
            # NOTE(rtheis): Get private network since functional tests may
            # create other networks.
            raw_output = cls.openstack('network show private -c id -f value')
        except exceptions.CommandFailed:
            return ''
        return ' --nic net-id=' + raw_output.strip('\n')

    def server_create(self, name=None):
        """Create server. Add cleanup."""
        name = name or data_utils.rand_uuid()
        opts = self.get_opts(self.FIELDS)
        raw_output = self.openstack('--debug server create --flavor ' +
                                    self.flavor_name +
                                    ' --image ' + self.image_name +
                                    self.network_arg + ' ' +
                                    name + opts)
        if not raw_output:
            self.fail('Server has not been created!')
        self.addCleanup(self.server_delete, name)

    def server_list(self, params=[]):
        """List servers."""
        opts = self.get_opts(params)
        return self.openstack('server list' + opts)

    def server_delete(self, name):
        """Delete server by name."""
        self.openstack('server delete ' + name)

    def setUp(self):
        """Set necessary variables and create server."""
        super(ServerTests, self).setUp()
        self.flavor_name = self.get_flavor()
        self.image_name = self.get_image()
        self.network_arg = self.get_network()

        self.NAME = data_utils.rand_name('TestServer')
        self.OTHER_NAME = data_utils.rand_name('TestServer')
        self.HEADERS = ['"Name"']
        self.FIELDS = ['name']
        self.IP_POOL = 'public'
        self.server_create(self.NAME)

    def test_server_rename(self):
        """Test server rename command.

        Test steps:
        1) Boot server in setUp
        2) Rename server
        3) Check output
        4) Rename server back to original name
        """
        raw_output = self.openstack('server set --name ' + self.OTHER_NAME +
                                    ' ' + self.NAME)
        self.assertOutput("", raw_output)
        self.assertNotIn(self.NAME, self.server_list(['Name']))
        self.assertIn(self.OTHER_NAME, self.server_list(['Name']))
        self.openstack('server set --name ' + self.NAME + ' ' +
                       self.OTHER_NAME)

    def test_server_list(self):
        """Test server list command.

        Test steps:
        1) Boot server in setUp
        2) List servers
        3) Check output
        """
        opts = self.get_opts(self.HEADERS)
        raw_output = self.openstack('server list' + opts)
        self.assertIn(self.NAME, raw_output)

    def test_server_show(self):
        """Test server create, server delete commands"""
        name1 = data_utils.rand_name('TestServer')
        cmd_output = json.loads(self.openstack(
            'server create -f json ' +
            '--flavor ' + self.flavor_name + ' ' +
            '--image ' + self.image_name + ' ' +
            self.network_arg + ' ' +
            name1
        ))
        self.assertIsNotNone(cmd_output["id"])
        self.addCleanup(self.openstack, 'server delete ' + name1)
        self.assertEqual(
            name1,
            cmd_output["name"],
        )

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

    def test_server_metadata(self):
        """Test command to set server metadata.

        Test steps:
        1) Boot server in setUp
        2) Set properties for server
        3) Check server properties in server show output
        4) Unset properties for server
        5) Check server properties in server show output
        """
        self.wait_for_status("ACTIVE")
        # metadata
        raw_output = self.openstack(
            'server set --property a=b --property c=d ' + self.NAME)
        opts = self.get_opts(["name", "properties"])
        raw_output = self.openstack('server show ' + self.NAME + opts)
        self.assertEqual(self.NAME + "\na='b', c='d'\n", raw_output)

        raw_output = self.openstack(
            'server unset --property a ' + self.NAME)
        opts = self.get_opts(["name", "properties"])
        raw_output = self.openstack('server show ' + self.NAME + opts)
        self.assertEqual(self.NAME + "\nc='d'\n", raw_output)

    def test_server_suspend_resume(self):
        """Test server suspend and resume commands.

        Test steps:
        1) Boot server in setUp
        2) Suspend server
        3) Check for SUSPENDED server status
        4) Resume server
        5) Check for ACTIVE server status
        """
        self.wait_for_status("ACTIVE")
        # suspend
        raw_output = self.openstack('server suspend ' + self.NAME)
        self.assertEqual("", raw_output)
        self.wait_for_status("SUSPENDED")
        # resume
        raw_output = self.openstack('server resume ' + self.NAME)
        self.assertEqual("", raw_output)
        self.wait_for_status("ACTIVE")

    def test_server_lock_unlock(self):
        """Test server lock and unlock commands.

        Test steps:
        1) Boot server in setUp
        2) Lock server
        3) Check output
        4) Unlock server
        5) Check output
        """
        self.wait_for_status("ACTIVE")
        # lock
        raw_output = self.openstack('server lock ' + self.NAME)
        self.assertEqual("", raw_output)
        # unlock
        raw_output = self.openstack('server unlock ' + self.NAME)
        self.assertEqual("", raw_output)

    def test_server_pause_unpause(self):
        """Test server pause and unpause commands.

        Test steps:
        1) Boot server in setUp
        2) Pause server
        3) Check for PAUSED server status
        4) Unpause server
        5) Check for ACTIVE server status
        """
        self.wait_for_status("ACTIVE")
        # pause
        raw_output = self.openstack('server pause ' + self.NAME)
        self.assertEqual("", raw_output)
        self.wait_for_status("PAUSED")
        # unpause
        raw_output = self.openstack('server unpause ' + self.NAME)
        self.assertEqual("", raw_output)
        self.wait_for_status("ACTIVE")

    def test_server_rescue_unrescue(self):
        """Test server rescue and unrescue commands.

        Test steps:
        1) Boot server in setUp
        2) Rescue server
        3) Check for RESCUE server status
        4) Unrescue server
        5) Check for ACTIVE server status
        """
        self.wait_for_status("ACTIVE")
        # rescue
        opts = self.get_opts(["adminPass"])
        raw_output = self.openstack('server rescue ' + self.NAME + opts)
        self.assertNotEqual("", raw_output)
        self.wait_for_status("RESCUE")
        # unrescue
        raw_output = self.openstack('server unrescue ' + self.NAME)
        self.assertEqual("", raw_output)
        self.wait_for_status("ACTIVE")

    def test_server_attach_detach_floating_ip(self):
        """Test commands to attach and detach floating IP for server.

        Test steps:
        1) Boot server in setUp
        2) Create floating IP
        3) Add floating IP to server
        4) Check for floating IP in server show output
        5) Remove floating IP from server
        6) Check that floating IP is  not in server show output
        7) Delete floating IP
        8) Check output
        """
        self.wait_for_status("ACTIVE")
        # attach ip
        opts = self.get_opts(["id", "floating_ip_address"])
        raw_output = self.openstack('floating ip create ' +
                                    self.IP_POOL +
                                    opts)
        ip, ipid, rol = tuple(raw_output.split('\n'))
        self.assertNotEqual("", ipid)
        self.assertNotEqual("", ip)
        raw_output = self.openstack('server add floating ip ' + self.NAME +
                                    ' ' + ip)
        self.assertEqual("", raw_output)
        raw_output = self.openstack('server show ' + self.NAME)
        self.assertIn(ip, raw_output)

        # detach ip
        raw_output = self.openstack('server remove floating ip ' + self.NAME +
                                    ' ' + ip)
        self.assertEqual("", raw_output)
        raw_output = self.openstack('server show ' + self.NAME)
        self.assertNotIn(ip, raw_output)
        raw_output = self.openstack('floating ip delete ' + ipid)
        self.assertEqual("", raw_output)

    def test_server_reboot(self):
        """Test server reboot command.

        Test steps:
        1) Boot server in setUp
        2) Reboot server
        3) Check for ACTIVE server status
        """
        self.wait_for_status("ACTIVE")
        # reboot
        raw_output = self.openstack('server reboot ' + self.NAME)
        self.assertEqual("", raw_output)
        self.wait_for_status("ACTIVE")

    def test_server_boot_from_volume(self):
        """Test server create from volume, server delete

        Test steps:
        1) Create volume from image
        2) Create empty volume
        3) Create server from new volumes
        4) Check for ACTIVE new server status
        5) Check volumes attached to server
        """
        # server_image = self.get_image()
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
        volume_name = data_utils.rand_name('volume', self.image_name)
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
        empty_volume_name = data_utils.rand_name('TestVolume')
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
        server_name = data_utils.rand_name('TestServer')
        server = json.loads(self.openstack(
            'server create -f json ' +
            '--flavor ' + self.flavor_name + ' ' +
            '--volume ' + volume_name + ' ' +
            '--block-device-mapping vdb=' + empty_volume_name + ' ' +
            self.network_arg + ' ' +
            server_name
        ))
        self.assertIsNotNone(server["id"])
        self.addCleanup(self.openstack, 'server delete --wait ' + server_name)
        self.assertEqual(
            server_name,
            server['name'],
        )
        volume_wait_for("server", server_name, "ACTIVE")

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

    def wait_for_status(self, expected_status='ACTIVE', wait=900, interval=30):
        """Wait until server reaches expected status."""
        # TODO(thowe): Add a server wait command to osc
        failures = ['ERROR']
        total_sleep = 0
        opts = self.get_opts(['status'])
        while total_sleep < wait:
            status = self.openstack('server show ' + self.NAME + opts)
            status = status.rstrip()
            print('Waiting for {} current status: {}'.format(expected_status,
                                                             status))
            if status == expected_status:
                break
            self.assertNotIn(status, failures)
            time.sleep(interval)
            total_sleep += interval

        status = self.openstack('server show ' + self.NAME + opts)
        status = status.rstrip()
        self.assertEqual(status, expected_status)
        # give it a little bit more time
        time.sleep(5)
