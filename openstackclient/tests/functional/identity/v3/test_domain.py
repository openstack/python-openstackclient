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

from tempest.lib.common.utils import data_utils
from tempest.lib import exceptions

from openstackclient.tests.functional.identity.v3 import common


class DomainTests(common.IdentityTests):

    def test_domain_create(self):
        domain_name = data_utils.rand_name('TestDomain')
        raw_output = self.openstack('domain create %s' % domain_name)
        # disable domain first before deleting it
        self.addCleanup(self.openstack,
                        'domain delete %s' % domain_name)
        self.addCleanup(self.openstack,
                        'domain set --disable %s' % domain_name)
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.DOMAIN_FIELDS)

    def test_domain_list(self):
        self._create_dummy_domain()
        raw_output = self.openstack('domain list')
        items = self.parse_listing(raw_output)
        self.assert_table_structure(items, common.BASIC_LIST_HEADERS)

    def test_domain_delete(self):
        domain_name = self._create_dummy_domain(add_clean_up=False)
        # cannot delete enabled domain, disable it first
        raw_output = self.openstack('domain set --disable %s' % domain_name)
        self.assertEqual(0, len(raw_output))
        raw_output = self.openstack('domain delete %s' % domain_name)
        self.assertEqual(0, len(raw_output))

    def test_domain_multi_delete(self):
        domain_1 = self._create_dummy_domain(add_clean_up=False)
        domain_2 = self._create_dummy_domain(add_clean_up=False)
        # cannot delete enabled domain, disable it first
        raw_output = self.openstack('domain set --disable %s' % domain_1)
        self.assertEqual(0, len(raw_output))
        raw_output = self.openstack('domain set --disable %s' % domain_2)
        self.assertEqual(0, len(raw_output))
        raw_output = self.openstack(
            'domain delete %s %s' % (domain_1, domain_2))
        self.assertEqual(0, len(raw_output))

    def test_domain_delete_failure(self):
        domain_name = self._create_dummy_domain()
        # cannot delete enabled domain
        self.assertRaises(exceptions.CommandFailed,
                          self.openstack,
                          'domain delete %s' % domain_name)

    def test_domain_show(self):
        domain_name = self._create_dummy_domain()
        raw_output = self.openstack('domain show %s' % domain_name)
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.DOMAIN_FIELDS)
