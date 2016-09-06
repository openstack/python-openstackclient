# Licensed under the Apache License, Version 2.0 (the "License"); you may
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

from openstackclient.tests.functional.identity.v2 import common


class EC2CredentialsTests(common.IdentityTests):

    def test_ec2_credentials_create(self):
        self._create_dummy_ec2_credentials()

    def test_ec2_credentials_delete(self):
        access_key = self._create_dummy_ec2_credentials(add_clean_up=False)
        raw_output = self.openstack(
            'ec2 credentials delete %s' % access_key,
        )
        self.assertEqual(0, len(raw_output))

    def test_ec2_credentials_multi_delete(self):
        access_key_1 = self._create_dummy_ec2_credentials(add_clean_up=False)
        access_key_2 = self._create_dummy_ec2_credentials(add_clean_up=False)
        raw_output = self.openstack(
            'ec2 credentials delete ' + access_key_1 + ' ' + access_key_2
        )
        self.assertEqual(0, len(raw_output))

    def test_ec2_credentials_list(self):
        self._create_dummy_ec2_credentials()
        raw_output = self.openstack('ec2 credentials list')
        items = self.parse_listing(raw_output)
        self.assert_table_structure(items, self.EC2_CREDENTIALS_LIST_HEADERS)

    def test_ec2_credentials_show(self):
        access_key = self._create_dummy_ec2_credentials()
        show_output = self.openstack(
            'ec2 credentials show %s' % access_key,
        )
        items = self.parse_show(show_output)
        self.assert_show_fields(items, self.EC2_CREDENTIALS_FIELDS)
