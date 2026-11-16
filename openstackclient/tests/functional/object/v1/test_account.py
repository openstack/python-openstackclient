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

from openstackclient.tests.functional.object.v1 import common


class AccountTests(common.ObjectStoreTests):
    """Functional tests for Object Store account commands."""

    def test_account(self):
        data = self.openstack('object store account show', parse_output=True)
        self.assertTrue(data['Account'])
        for field in ('Containers', 'Objects', 'Bytes'):
            self.assertGreaterEqual(int(data[field]), 0)

        # Account metadata is shared: only modify our uniquely named keys.
        key = 'osc-test-' + uuid.uuid4().hex
        other = key + '-other'
        self.addCleanup(
            self.openstack,
            f'object store account unset --property {key} --property {other}',
        )
        self.assertEqual(
            '',
            self.openstack(
                f'object store account set --property {key}=one '
                f'--property {other}=two'
            ),
        )
        data = self.openstack('object store account show', parse_output=True)
        properties = self.get_properties(data)
        self.assertEqual('one', properties[key])
        self.assertEqual('two', properties[other])

        self.openstack(f'object store account set --property {key}=updated')
        data = self.openstack('object store account show', parse_output=True)
        properties = self.get_properties(data)
        self.assertEqual('updated', properties[key])
        self.assertEqual('two', properties[other])

        self.assertEqual(
            '',
            self.openstack(
                f'object store account unset --property {key} '
                f'--property {other}'
            ),
        )
        data = self.openstack('object store account show', parse_output=True)
        properties = self.get_properties(data)
        self.assertNotIn(key, properties)
        self.assertNotIn(other, properties)
