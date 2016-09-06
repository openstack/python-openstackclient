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

from openstackclient.tests.functional.volume.v1 import common


class QosTests(common.BaseVolumeTests):
    """Functional tests for volume qos. """

    NAME = uuid.uuid4().hex
    HEADERS = ['Name']
    FIELDS = ['id', 'name']
    ID = None

    @classmethod
    def setUpClass(cls):
        super(QosTests, cls).setUpClass()
        opts = cls.get_opts(cls.FIELDS)
        raw_output = cls.openstack('volume qos create ' + cls.NAME + opts)
        cls.ID, name, rol = raw_output.split('\n')
        cls.assertOutput(cls.NAME, name)

    @classmethod
    def tearDownClass(cls):
        raw_output = cls.openstack('volume qos delete ' + cls.ID)
        cls.assertOutput('', raw_output)

    def test_volume_qos_list(self):
        opts = self.get_opts(self.HEADERS)
        raw_output = self.openstack('volume qos list' + opts)
        self.assertIn(self.NAME, raw_output)

    def test_volume_qos_show(self):
        opts = self.get_opts(self.FIELDS)
        raw_output = self.openstack('volume qos show ' + self.ID + opts)
        self.assertEqual(self.ID + "\n" + self.NAME + "\n", raw_output)

    def test_volume_qos_metadata(self):
        raw_output = self.openstack(
            'volume qos set --property a=b --property c=d ' + self.ID)
        self.assertEqual("", raw_output)
        opts = self.get_opts(['name', 'specs'])
        raw_output = self.openstack('volume qos show ' + self.ID + opts)
        self.assertEqual(self.NAME + "\na='b', c='d'\n", raw_output)
