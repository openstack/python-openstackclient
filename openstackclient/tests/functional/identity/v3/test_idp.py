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

from openstackclient.tests.functional.identity.v3 import common


class IdentityProviderTests(common.IdentityTests):
    # Introduce functional test case for command 'Identity Provider'

    def test_idp_create(self):
        self._create_dummy_idp()

    def test_idp_delete(self):
        identity_provider = self._create_dummy_idp(add_clean_up=False)
        raw_output = self.openstack(
            f'identity provider delete {identity_provider}'
        )
        self.assertEqual(0, len(raw_output))

    def test_idp_multi_delete(self):
        idp_1 = self._create_dummy_idp(add_clean_up=False)
        idp_2 = self._create_dummy_idp(add_clean_up=False)
        raw_output = self.openstack(
            f'identity provider delete {idp_1} {idp_2}'
        )
        self.assertEqual(0, len(raw_output))

    def test_idp_show(self):
        identity_provider = self._create_dummy_idp(add_clean_up=True)
        raw_output = self.openstack(
            f'identity provider show {identity_provider}'
        )
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, self.IDENTITY_PROVIDER_FIELDS)

    def test_idp_list(self):
        self._create_dummy_idp(add_clean_up=True)
        raw_output = self.openstack('identity provider list')
        items = self.parse_listing(raw_output)
        self.assert_table_structure(items, self.IDENTITY_PROVIDER_LIST_HEADERS)

    def test_idp_set(self):
        identity_provider = self._create_dummy_idp(add_clean_up=True)
        new_remoteid = data_utils.rand_name('newRemoteId')
        raw_output = self.openstack(
            f'identity provider set '
            f'{identity_provider} '
            f'--remote-id {new_remoteid}'
        )
        self.assertEqual(0, len(raw_output))
        raw_output = self.openstack(
            f'identity provider show {identity_provider}'
        )
        updated_value = self.parse_show_as_object(raw_output)
        self.assertIn(new_remoteid, updated_value['remote_ids'])
