#   Copyright 2017 Huawei, Inc. All rights reserved.
#
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

import json
import uuid

from openstackclient.tests.functional import base
from openstackclient.tests.functional.compute.v2 import test_server


class ServerEventTests(base.TestCase):
    """Functional tests for server event."""

    def setUp(self):
        super(ServerEventTests, self).setUp()
        _flavor = test_server.ServerTests.get_flavor()
        _image = test_server.ServerTests.get_image()
        _network = test_server.ServerTests.get_network()
        self.server_name = uuid.uuid4().hex
        cmd_output = json.loads(self.openstack(
            'server create -f json ' +
            '--flavor ' + _flavor + ' ' +
            '--image ' + _image + ' ' +
            _network + ' ' +
            '--wait ' +
            self.server_name
        ))
        if not cmd_output:
            self.fail('Server has not been created!')
        self.addCleanup(self.openstack, 'server delete ' + self.server_name)
        self.assertEqual(self.server_name, cmd_output['name'])
        self.server_id = cmd_output.get('id')

    def test_server_event_list_and_show(self):
        """Test list, show server event"""
        # Test 'server event list' for creating
        cmd_output = json.loads(self.openstack(
            'server event list -f json ' + self.server_name
        ))
        request_id = None
        for each_event in cmd_output:
            self.assertNotIn('Message', each_event)
            self.assertNotIn('Project ID', each_event)
            self.assertNotIn('User ID', each_event)
            if each_event.get('Action') == 'create':
                self.assertEqual(self.server_id, each_event.get('Server ID'))
                request_id = each_event.get('Request ID')
                break
        self.assertIsNotNone(request_id)
        # Test 'server event show' for creating
        cmd_output = json.loads(self.openstack(
            'server event show -f json ' + self.server_name + ' ' + request_id
        ))
        self.assertEqual(self.server_id, cmd_output.get('instance_uuid'))
        self.assertEqual(request_id, cmd_output.get('request_id'))
        self.assertEqual('create', cmd_output.get('action'))
        self.assertIsNotNone(cmd_output.get('events'))
        self.assertIsInstance(cmd_output.get('events'), list)

        # Reboot server, trigger reboot event
        self.openstack('server reboot --wait ' + self.server_name)
        # Test 'server event list --long' for rebooting
        cmd_output = json.loads(self.openstack(
            'server event list --long -f json ' + self.server_name
        ))
        request_id = None
        for each_event in cmd_output:
            self.assertIn('Message', each_event)
            self.assertIn('Project ID', each_event)
            self.assertIn('User ID', each_event)
            if each_event.get('Action') == 'reboot':
                request_id = each_event.get('Request ID')
                self.assertEqual(self.server_id, each_event.get('Server ID'))
                break
        self.assertIsNotNone(request_id)
        # Test 'server event show' for rebooting
        cmd_output = json.loads(self.openstack(
            'server event show -f json ' + self.server_name + ' ' + request_id
        ))

        self.assertEqual(self.server_id, cmd_output.get('instance_uuid'))
        self.assertEqual(request_id, cmd_output.get('request_id'))
        self.assertEqual('reboot', cmd_output.get('action'))
        self.assertIsNotNone(cmd_output.get('events'))
        self.assertIsInstance(cmd_output.get('events'), list)
