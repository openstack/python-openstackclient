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

import testtools

from functional.common import exceptions
from functional.common import test


class ServerTests(test.TestCase):
    """Functional tests for server. """

    NAME = uuid.uuid4().hex
    OTHER_NAME = uuid.uuid4().hex
    HEADERS = ['"Name"']
    FIELDS = ['name']
    IP_POOL = 'public'

    @classmethod
    def get_flavor(cls):
        raw_output = cls.openstack('flavor list -f value -c ID')
        ray = raw_output.split('\n')
        idx = len(ray)/2
        return ray[idx]

    @classmethod
    def get_image(cls):
        raw_output = cls.openstack('image list -f value -c ID')
        ray = raw_output.split('\n')
        idx = len(ray)/2
        return ray[idx]

    @classmethod
    def get_network(cls):
        try:
            raw_output = cls.openstack('network list -f value -c ID')
        except exceptions.CommandFailed:
            return ''
        ray = raw_output.split('\n')
        idx = len(ray)/2
        return ' --nic net-id=' + ray[idx]

    @classmethod
    def setUpClass(cls):
        opts = cls.get_show_opts(cls.FIELDS)
        flavor = cls.get_flavor()
        image = cls.get_image()
        network = cls.get_network()
        raw_output = cls.openstack('server create --flavor ' + flavor +
                                   ' --image ' + image + network + ' ' +
                                   cls.NAME + opts)
        expected = cls.NAME + '\n'
        cls.assertOutput(expected, raw_output)

    @classmethod
    def tearDownClass(cls):
        # Rename test
        raw_output = cls.openstack('server set --name ' + cls.OTHER_NAME +
                                   ' ' + cls.NAME)
        cls.assertOutput("", raw_output)
        # Delete test
        raw_output = cls.openstack('server delete ' + cls.OTHER_NAME)
        cls.assertOutput('', raw_output)

    def test_server_list(self):
        opts = self.get_list_opts(self.HEADERS)
        raw_output = self.openstack('server list' + opts)
        self.assertIn(self.NAME, raw_output)

    def test_server_show(self):
        opts = self.get_show_opts(self.FIELDS)
        raw_output = self.openstack('server show ' + self.NAME + opts)
        self.assertEqual(self.NAME + "\n", raw_output)

    def wait_for(self, desired, wait=120, interval=5, failures=['ERROR']):
        # TODO(thowe): Add a server wait command to osc
        status = "notset"
        wait = 120
        interval = 5
        total_sleep = 0
        opts = self.get_show_opts(['status'])
        while total_sleep < wait:
            status = self.openstack('server show ' + self.NAME + opts)
            status = status.rstrip()
            print('Waiting for {} current status: {}'.format(desired, status))
            if status == desired:
                break
            self.assertNotIn(status, failures)
            time.sleep(interval)
            total_sleep += interval
        self.assertEqual(desired, status)

    @testtools.skip('skipping due to bug 1483422')
    def test_server_up_test(self):
        self.wait_for("ACTIVE")
        # give it a little bit more time
        time.sleep(5)
        # metadata
        raw_output = self.openstack(
            'server set --property a=b --property c=d ' + self.NAME)
        opts = self.get_show_opts(["name", "properties"])
        raw_output = self.openstack('server show ' + self.NAME + opts)
        self.assertEqual(self.NAME + "\na='b', c='d'\n", raw_output)
        # suspend
        raw_output = self.openstack('server suspend ' + self.NAME)
        self.assertEqual("", raw_output)
        self.wait_for("SUSPENDED")
        # resume
        raw_output = self.openstack('server resume ' + self.NAME)
        self.assertEqual("", raw_output)
        self.wait_for("ACTIVE")
        # lock
        raw_output = self.openstack('server lock ' + self.NAME)
        self.assertEqual("", raw_output)
        # unlock
        raw_output = self.openstack('server unlock ' + self.NAME)
        self.assertEqual("", raw_output)
        # pause
        raw_output = self.openstack('server pause ' + self.NAME)
        self.assertEqual("", raw_output)
        self.wait_for("PAUSED")
        # unpause
        raw_output = self.openstack('server unpause ' + self.NAME)
        self.assertEqual("", raw_output)
        self.wait_for("ACTIVE")
        # rescue
        opts = self.get_show_opts(["adminPass"])
        raw_output = self.openstack('server rescue ' + self.NAME + opts)
        self.assertNotEqual("", raw_output)
        self.wait_for("RESCUE")
        # unrescue
        raw_output = self.openstack('server unrescue ' + self.NAME)
        self.assertEqual("", raw_output)
        self.wait_for("ACTIVE")
        # attach ip
        opts = self.get_show_opts(["id", "ip"])
        raw_output = self.openstack('ip floating create ' + self.IP_POOL +
                                    opts)
        ipid, ip, rol = tuple(raw_output.split('\n'))
        self.assertNotEqual("", ipid)
        self.assertNotEqual("", ip)
        raw_output = self.openstack('ip floating add ' + ip + ' ' + self.NAME)
        self.assertEqual("", raw_output)
        raw_output = self.openstack('server show ' + self.NAME)
        self.assertIn(ip, raw_output)
        # detach ip
        raw_output = self.openstack('ip floating remove ' + ip + ' ' +
                                    self.NAME)
        self.assertEqual("", raw_output)
        raw_output = self.openstack('server show ' + self.NAME)
        self.assertNotIn(ip, raw_output)
        raw_output = self.openstack('ip floating delete ' + ipid)
        self.assertEqual("", raw_output)
        # reboot
        raw_output = self.openstack('server reboot ' + self.NAME)
        self.assertEqual("", raw_output)
        self.wait_for("ACTIVE")
