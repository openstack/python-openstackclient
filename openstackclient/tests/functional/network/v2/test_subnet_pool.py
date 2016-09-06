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


class SubnetPoolTests(base.TestCase):
    """Functional tests for subnet pool. """
    NAME = uuid.uuid4().hex
    CREATE_POOL_PREFIX = '10.100.0.0/24'
    SET_POOL_PREFIX = '10.100.0.0/16'
    HEADERS = ['Name']
    FIELDS = ['name']

    @classmethod
    def setUpClass(cls):
        opts = cls.get_opts(cls.FIELDS)
        raw_output = cls.openstack('subnet pool create --pool-prefix ' +
                                   cls.CREATE_POOL_PREFIX + ' ' +
                                   cls.NAME + opts)
        cls.assertOutput(cls.NAME + '\n', raw_output)

    @classmethod
    def tearDownClass(cls):
        raw_output = cls.openstack('subnet pool delete ' + cls.NAME)
        cls.assertOutput('', raw_output)

    def test_subnet_list(self):
        opts = self.get_opts(self.HEADERS)
        raw_output = self.openstack('subnet pool list' + opts)
        self.assertIn(self.NAME, raw_output)

    def test_subnet_set(self):
        self.openstack('subnet pool set --pool-prefix ' +
                       self.SET_POOL_PREFIX + ' ' + self.NAME)
        opts = self.get_opts(['prefixes', 'name'])
        raw_output = self.openstack('subnet pool show ' + self.NAME + opts)
        self.assertEqual(self.NAME + '\n' + self.SET_POOL_PREFIX + '\n',
                         raw_output)

    def test_subnet_show(self):
        opts = self.get_opts(self.FIELDS)
        raw_output = self.openstack('subnet pool show ' + self.NAME + opts)
        self.assertEqual(self.NAME + '\n', raw_output)
