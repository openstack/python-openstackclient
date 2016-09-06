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
#

"""API Utilities Library Tests"""

import copy

from openstackclient.api import api
from openstackclient.api import utils as api_utils
from openstackclient.tests.unit.api import fakes as api_fakes


class TestBaseAPIFilter(api_fakes.TestSession):
    """The filters can be tested independently"""

    def setUp(self):
        super(TestBaseAPIFilter, self).setUp()
        self.api = api.BaseAPI(
            session=self.sess,
            endpoint=self.BASE_URL,
        )

        self.input_list = [
            api_fakes.RESP_ITEM_1,
            api_fakes.RESP_ITEM_2,
            api_fakes.RESP_ITEM_3,
        ]

    def test_simple_filter_none(self):
        output = api_utils.simple_filter(
        )
        self.assertIsNone(output)

    def test_simple_filter_no_attr(self):
        output = api_utils.simple_filter(
            copy.deepcopy(self.input_list),
        )
        self.assertEqual(self.input_list, output)

    def test_simple_filter_attr_only(self):
        output = api_utils.simple_filter(
            copy.deepcopy(self.input_list),
            attr='status',
        )
        self.assertEqual(self.input_list, output)

    def test_simple_filter_attr_value(self):
        output = api_utils.simple_filter(
            copy.deepcopy(self.input_list),
            attr='status',
            value='',
        )
        self.assertEqual([], output)

        output = api_utils.simple_filter(
            copy.deepcopy(self.input_list),
            attr='status',
            value='UP',
        )
        self.assertEqual(
            [api_fakes.RESP_ITEM_1, api_fakes.RESP_ITEM_3],
            output,
        )

        output = api_utils.simple_filter(
            copy.deepcopy(self.input_list),
            attr='fred',
            value='UP',
        )
        self.assertEqual([], output)

    def test_simple_filter_prop_attr_only(self):
        output = api_utils.simple_filter(
            copy.deepcopy(self.input_list),
            attr='b',
            property_field='props',
        )
        self.assertEqual(self.input_list, output)

        output = api_utils.simple_filter(
            copy.deepcopy(self.input_list),
            attr='status',
            property_field='props',
        )
        self.assertEqual(self.input_list, output)

    def test_simple_filter_prop_attr_value(self):
        output = api_utils.simple_filter(
            copy.deepcopy(self.input_list),
            attr='b',
            value=2,
            property_field='props',
        )
        self.assertEqual(
            [api_fakes.RESP_ITEM_1, api_fakes.RESP_ITEM_2],
            output,
        )

        output = api_utils.simple_filter(
            copy.deepcopy(self.input_list),
            attr='b',
            value=9,
            property_field='props',
        )
        self.assertEqual([], output)
