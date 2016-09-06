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


class AggregateTests(base.TestCase):
    """Functional tests for aggregate."""

    NAME = uuid.uuid4().hex
    HEADERS = ['Name']
    FIELDS = ['name']

    @classmethod
    def setUpClass(cls):
        opts = cls.get_opts(cls.FIELDS)
        # Use the default 'nova' availability zone for the aggregate.
        raw_output = cls.openstack(
            'aggregate create --zone nova ' + cls.NAME + opts
        )
        expected = cls.NAME + '\n'
        cls.assertOutput(expected, raw_output)

    @classmethod
    def tearDownClass(cls):
        raw_output = cls.openstack('aggregate delete ' + cls.NAME)
        cls.assertOutput('', raw_output)

    def test_aggregate_list(self):
        opts = self.get_opts(self.HEADERS)
        raw_output = self.openstack('aggregate list' + opts)
        self.assertIn(self.NAME, raw_output)

    def test_aggregate_show(self):
        opts = self.get_opts(self.FIELDS)
        raw_output = self.openstack('aggregate show ' + self.NAME + opts)
        self.assertEqual(self.NAME + "\n", raw_output)

    def test_aggregate_properties(self):
        opts = self.get_opts(['properties'])

        raw_output = self.openstack(
            'aggregate set --property a=b --property c=d ' + self.NAME
        )
        self.assertEqual('', raw_output)

        raw_output = self.openstack('aggregate show ' + self.NAME + opts)
        self.assertIn("a='b', c='d'\n", raw_output)

        raw_output = self.openstack(
            'aggregate unset --property a ' + self.NAME
        )
        self.assertEqual('', raw_output)

        raw_output = self.openstack('aggregate show ' + self.NAME + opts)
        self.assertIn("c='d'\n", raw_output)
