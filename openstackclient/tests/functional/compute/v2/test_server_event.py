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

from openstackclient.tests.functional.compute.v2 import common


class ServerEventTests(common.ComputeTestCase):
    """Functional tests for server event"""

    def setUp(self):
        super().setUp()

        # NOTE(dtroyer): As long as these tests are read-only we can get away
        #                with using the same server instance for all of them.
        cmd_output = self.server_create()
        self.server_id = cmd_output.get('id')
        self.server_name = cmd_output['name']

    def test_server_event_list_and_show(self):
        """Test list, show server event"""
        # Test 'server event list' for creating
        cmd_output = self.openstack(
            'server event list ' + self.server_name,
            parse_output=True,
        )
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
        cmd_output = self.openstack(
            'server event show ' + self.server_name + ' ' + request_id,
            parse_output=True,
        )
        self.assertEqual(request_id, cmd_output.get('request_id'))
        self.assertEqual('create', cmd_output.get('action'))
        self.assertIsNotNone(cmd_output.get('events'))
        self.assertIsInstance(cmd_output.get('events'), list)

        # Reboot server, trigger reboot event
        self.openstack('server reboot --wait ' + self.server_name)
        # Test 'server event list --long' for rebooting
        cmd_output = self.openstack(
            'server event list --long ' + self.server_name,
            parse_output=True,
        )
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
        cmd_output = self.openstack(
            'server event show ' + self.server_name + ' ' + request_id,
            parse_output=True,
        )
        self.assertEqual(request_id, cmd_output.get('request_id'))
        self.assertEqual('reboot', cmd_output.get('action'))
        self.assertIsNotNone(cmd_output.get('events'))
        self.assertIsInstance(cmd_output.get('events'), list)

    def test_server_event_list_and_show_deleted_server(self):
        # Need to create a new server that will not attempt cleanup because we
        # are going to delete it during the test and cleanup would fail with
        # 404.
        cmd_output = self.server_create(cleanup=False)
        server_id = cmd_output['id']
        # Delete the server
        self.openstack('server delete --wait ' + server_id)
        # And verify we can get the event list after it's deleted
        # Test 'server event list' for deleting
        cmd_output = self.openstack(
            '--os-compute-api-version 2.21 server event list ' + server_id,
            parse_output=True,
        )
        request_id = None
        for each_event in cmd_output:
            self.assertNotIn('Message', each_event)
            self.assertNotIn('Project ID', each_event)
            self.assertNotIn('User ID', each_event)
            if each_event.get('Action') == 'delete':
                self.assertEqual(server_id, each_event.get('Server ID'))
                request_id = each_event.get('Request ID')
                break
        self.assertIsNotNone(request_id)
        # Test 'server event show' for deleting
        cmd_output = self.openstack(
            '--os-compute-api-version 2.21 '
            'server event show ' + server_id + ' ' + request_id,
            parse_output=True,
        )
        self.assertEqual(request_id, cmd_output.get('request_id'))
        self.assertEqual('delete', cmd_output.get('action'))
        self.assertIsNotNone(cmd_output.get('events'))
        self.assertIsInstance(cmd_output.get('events'), list)
