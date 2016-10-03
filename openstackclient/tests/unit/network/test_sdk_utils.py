#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.

from openstackclient.network import sdk_utils
from openstackclient.tests.unit import utils as tests_utils


class TestSDKUtils(tests_utils.TestCase):

    def setUp(self):
        super(TestSDKUtils, self).setUp()

    def _test_get_osc_show_columns_for_sdk_resource(
            self, sdk_resource, column_map,
            expected_display_columns, expected_attr_columns):
        display_columns, attr_columns = \
            sdk_utils.get_osc_show_columns_for_sdk_resource(
                sdk_resource, column_map)
        self.assertEqual(expected_display_columns, display_columns)
        self.assertEqual(expected_attr_columns, attr_columns)

    def test_get_osc_show_columns_for_sdk_resource_empty(self):
        self._test_get_osc_show_columns_for_sdk_resource(
            {}, {}, tuple(), tuple())

    def test_get_osc_show_columns_for_sdk_resource_empty_map(self):
        self._test_get_osc_show_columns_for_sdk_resource(
            {'foo': 'foo1'}, {},
            ('foo',), ('foo',))

    def test_get_osc_show_columns_for_sdk_resource_empty_data(self):
        self._test_get_osc_show_columns_for_sdk_resource(
            {}, {'foo': 'foo_map'},
            ('foo_map',), ('foo_map',))

    def test_get_osc_show_columns_for_sdk_resource_map(self):
        self._test_get_osc_show_columns_for_sdk_resource(
            {'foo': 'foo1'}, {'foo': 'foo_map'},
            ('foo_map',), ('foo',))

    def test_get_osc_show_columns_for_sdk_resource_map_dup(self):
        self._test_get_osc_show_columns_for_sdk_resource(
            {'foo': 'foo1', 'foo_map': 'foo1'}, {'foo': 'foo_map'},
            ('foo_map',), ('foo',))

    def test_get_osc_show_columns_for_sdk_resource_map_full(self):
        self._test_get_osc_show_columns_for_sdk_resource(
            {'foo': 'foo1', 'bar': 'bar1'},
            {'foo': 'foo_map', 'new': 'bar'},
            ('bar', 'foo_map'), ('bar', 'foo'))
