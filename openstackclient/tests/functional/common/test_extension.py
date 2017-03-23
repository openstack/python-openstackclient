# Copyright (c) 2017, Intel Corporation.
# All Rights Reserved.
#
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

import json

from openstackclient.tests.functional import base


class TestExtension(base.TestCase):
    """Functional tests for extension."""

    def test_extension_list(self):
        """Test extension list."""
        json_output = json.loads(self.openstack(
            'extension list -f json ' + '--network')
        )
        self.assertEqual(
            'Default Subnetpools',
            json_output[0]['Name'],
        )

    def test_extension_show(self):
        """Test extension show."""
        name = 'agent'
        json_output = json.loads(self.openstack(
            'extension show -f json ' + name)
        )
        self.assertEqual(
            name,
            json_output.get('Alias'))
