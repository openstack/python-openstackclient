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

from openstackclient.tests.functional.identity.v2 import common


class TokenTests(common.IdentityTests):
    def test_token_issue(self):
        self._create_dummy_token()

    def test_token_revoke(self):
        token_id = self._create_dummy_token(add_clean_up=False)
        raw_output = self.openstack(f'token revoke {token_id}')
        self.assertEqual(0, len(raw_output))
