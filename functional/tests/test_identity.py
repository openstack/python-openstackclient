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

from functional.common import exceptions
from functional.common import test


class IdentityV2Tests(test.TestCase):
    """Functional tests for Identity V2 commands. """

    def test_user_list(self):
        field_names = ['ID', 'Name']
        raw_output = self.openstack('user list')
        items = self.parse_listing(raw_output)
        self.assert_table_structure(items, field_names)

    def test_user_get(self):
        field_names = ['email', 'enabled', 'id', 'name',
                       'project_id', 'username']
        raw_output = self.openstack('user show admin')
        items = self.parse_show(raw_output)
        self.assert_show_fields(items, field_names)

    def test_bad_user_command(self):
        self.assertRaises(exceptions.CommandFailed,
                          self.openstack, 'user unlist')
