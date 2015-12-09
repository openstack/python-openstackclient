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

import mock

from openstackclient.network import common
from openstackclient.tests import utils

RESOURCE = 'resource'
RESOURCES = 'resources'
NAME = 'matrix'
ID = 'Fishburne'


class TestFind(utils.TestCase):
    def setUp(self):
        super(TestFind, self).setUp()
        self.mock_client = mock.Mock()
        self.list_resources = mock.Mock()
        self.mock_client.find_resource = self.list_resources
        self.resource = mock.Mock()
        self.resource.id = ID

    def test_name(self):
        self.list_resources.return_value = self.resource

        result = common.find(self.mock_client, RESOURCE, RESOURCES, NAME)

        self.assertEqual(ID, result)
        self.list_resources.assert_called_with(NAME, ignore_missing=False)

    def test_id(self):
        self.list_resources.return_value = self.resource

        result = common.find(self.mock_client, RESOURCE, RESOURCES, NAME)

        self.assertEqual(ID, result)
        self.list_resources.assert_called_with(NAME, ignore_missing=False)

    def test_nameo(self):
        self.list_resources.return_value = self.resource

        result = common.find(self.mock_client, RESOURCE, RESOURCES, NAME,
                             name_attr='nameo')

        self.assertEqual(ID, result)
        self.list_resources.assert_called_with(NAME, ignore_missing=False)
