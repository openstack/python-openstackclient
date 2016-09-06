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

from openstackclient.tests.functional import base


class ServerGroupTests(base.TestCase):
    """Functional tests for servergroup."""

    NAME = uuid.uuid4().hex
    HEADERS = ['Name']
    FIELDS = ['name']

    @classmethod
    def setUpClass(cls):
        opts = cls.get_opts(cls.FIELDS)
        raw_output = cls.openstack('server group create --policy affinity ' +
                                   cls.NAME + opts)
        expected = cls.NAME + '\n'
        cls.assertOutput(expected, raw_output)

    @classmethod
    def tearDownClass(cls):
        raw_output = cls.openstack('server group delete ' + cls.NAME)
        cls.assertOutput('', raw_output)

    def test_server_group_list(self):
        opts = self.get_opts(self.HEADERS)
        raw_output = self.openstack('server group list' + opts)
        self.assertIn(self.NAME, raw_output)

    def test_server_group_show(self):
        opts = self.get_opts(self.FIELDS)
        raw_output = self.openstack('server group show ' + self.NAME + opts)
        self.assertEqual(self.NAME + "\n", raw_output)
