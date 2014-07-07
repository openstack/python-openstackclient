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

from openstackclient.common import exceptions
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
        self.mock_client.list_resources = self.list_resources
        self.matrix = {'id': ID}

    def test_name(self):
        self.list_resources.return_value = {RESOURCES: [self.matrix]}

        result = common.find(self.mock_client, RESOURCE, RESOURCES, NAME)

        self.assertEqual(ID, result)
        self.list_resources.assert_called_with(fields='id', name=NAME)

    def test_id(self):
        self.list_resources.side_effect = [{RESOURCES: []},
                                           {RESOURCES: [self.matrix]}]

        result = common.find(self.mock_client, RESOURCE, RESOURCES, NAME)

        self.assertEqual(ID, result)
        self.list_resources.assert_called_with(fields='id', id=NAME)

    def test_nameo(self):
        self.list_resources.return_value = {RESOURCES: [self.matrix]}

        result = common.find(self.mock_client, RESOURCE, RESOURCES, NAME,
                             name_attr='nameo')

        self.assertEqual(ID, result)
        self.list_resources.assert_called_with(fields='id', nameo=NAME)

    def test_dups(self):
        dup = {'id': 'Larry'}
        self.list_resources.return_value = {RESOURCES: [self.matrix, dup]}

        self.assertRaises(exceptions.CommandError, common.find,
                          self.mock_client, RESOURCE, RESOURCES, NAME)

    def test_nada(self):
        self.list_resources.side_effect = [{RESOURCES: []},
                                           {RESOURCES: []}]

        self.assertRaises(exceptions.CommandError, common.find,
                          self.mock_client, RESOURCE, RESOURCES, NAME)
