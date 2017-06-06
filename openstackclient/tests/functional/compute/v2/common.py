#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

import json
import time
import uuid

from tempest.lib import exceptions

from openstackclient.tests.functional import base


class ComputeTestCase(base.TestCase):
    """Common functional test bits for Compute commands"""

    flavor_name = None
    image_name = None
    network_arg = None

    def setUp(self):
        """Select common resources"""
        super(ComputeTestCase, self).setUp()
        self.flavor_name = self.get_flavor()
        self.image_name = self.get_image()
        self.network_arg = self.get_network()

    @classmethod
    def get_flavor(cls):
        # NOTE(rtheis): Get cirros256 or m1.tiny flavors since functional
        #               tests may create other flavors.
        flavors = json.loads(cls.openstack(
            "flavor list -f json "
        ))
        server_flavor = None
        for flavor in flavors:
            if flavor['Name'] in ['m1.tiny', 'cirros256']:
                server_flavor = flavor['Name']
                break
        return server_flavor

    @classmethod
    def get_image(cls):
        # NOTE(rtheis): Get first Cirros image since functional tests may
        #               create other images.  Image may be named '-uec' or
        #               '-disk'.
        images = json.loads(cls.openstack(
            "image list -f json "
        ))
        server_image = None
        for image in images:
            if (image['Name'].startswith('cirros-') and
                    (image['Name'].endswith('-uec') or
                     image['Name'].endswith('-disk'))):
                server_image = image['Name']
                break
        return server_image

    @classmethod
    def get_network(cls):
        try:
            # NOTE(rtheis): Get private network since functional tests may
            #               create other networks.
            cmd_output = json.loads(cls.openstack(
                'network show private -f json'
            ))
        except exceptions.CommandFailed:
            return ''
        return '--nic net-id=' + cmd_output['id']

    def server_create(self, name=None, cleanup=True):
        """Create server, with cleanup"""
        if not self.flavor_name:
            self.flavor_name = self.get_flavor()
        if not self.image_name:
            self.image_name = self.get_image()
        if not self.network_arg:
            self.network_arg = self.get_network()
        name = name or uuid.uuid4().hex
        cmd_output = json.loads(self.openstack(
            'server create -f json ' +
            '--flavor ' + self.flavor_name + ' ' +
            '--image ' + self.image_name + ' ' +
            self.network_arg + ' ' +
            '--wait ' +
            name
        ))
        self.assertIsNotNone(cmd_output["id"])
        self.assertEqual(
            name,
            cmd_output["name"],
        )
        if cleanup:
            self.addCleanup(self.server_delete, name)
        return cmd_output

    def server_delete(self, name):
        """Delete server by name"""
        raw_output = self.openstack('server delete ' + name)
        self.assertOutput('', raw_output)

    def wait_for_status(
            self,
            name,
            expected_status='ACTIVE',
            wait=900,
            interval=10,
    ):
        """Wait until server reaches expected status"""
        # TODO(thowe): Add a server wait command to osc
        failures = ['ERROR']
        total_sleep = 0
        while total_sleep < wait:
            cmd_output = json.loads(self.openstack(
                'server show -f json ' +
                name
            ))
            status = cmd_output['status']
            if status == expected_status:
                print('Server {} now has status {}'.format(
                    name, status))
                break
            print('Server {}: Waiting for {}, current status: {}'.format(
                name, expected_status, status))
            self.assertNotIn(status, failures)
            time.sleep(interval)
            total_sleep += interval

        cmd_output = json.loads(self.openstack(
            'server show -f json ' +
            name
        ))
        status = cmd_output['status']
        self.assertEqual(status, expected_status)
        # give it a little bit more time
        time.sleep(5)
