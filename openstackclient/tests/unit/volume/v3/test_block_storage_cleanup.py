# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import uuid

from osc_lib import exceptions

from openstackclient.tests.unit.volume.v3 import fakes as volume_fakes
from openstackclient.volume.v3 import block_storage_cleanup

FAKE_CLEANING = [
    {
        'id': 1,
        'host': 'devstack@fakedriver-1',
        'binary': 'cinder-volume',
        'cluster_name': 'fake_cluster',
    }
]
FAKE_UNAVAILABLE = [
    {
        'id': 2,
        'host': 'devstack@fakedriver-2',
        'binary': 'cinder-scheduler',
        'cluster_name': 'new_cluster',
    }
]
FAKE_CLEANUP_RESPONSE = {
    'cleaning': FAKE_CLEANING,
    'unavailable': FAKE_UNAVAILABLE,
}


class TestBlockStorageCleanup(volume_fakes.TestVolume):
    def setUp(self):
        super().setUp()

        self.volume_client.cleanup_service_workers.return_value = (
            FAKE_CLEANUP_RESPONSE
        )

        self.cmd = block_storage_cleanup.BlockStorageCleanup(self.app, None)

    def test_cleanup(self):
        self.set_volume_api_version('3.24')

        arglist = []
        verifylist = [
            ('cluster', None),
            ('host', None),
            ('binary', None),
            ('is_up', None),
            ('disabled', None),
            ('resource_id', None),
            ('resource_type', None),
            ('service_id', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        expected_columns = ('ID', 'Cluster Name', 'Host', 'Binary', 'Status')
        expected_data = (
            (
                1,
                'fake_cluster',
                'devstack@fakedriver-1',
                'cinder-volume',
                'Cleaning',
            ),
            (
                2,
                'new_cluster',
                'devstack@fakedriver-2',
                'cinder-scheduler',
                'Unavailable',
            ),
        )
        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(expected_columns, columns)
        self.assertEqual(expected_data, tuple(data))

        self.volume_client.cleanup_service_workers.assert_called_once_with()

    def test_block_storage_cleanup_pre_324(self):
        arglist = []
        verifylist = [
            ('cluster', None),
            ('host', None),
            ('binary', None),
            ('is_up', None),
            ('disabled', None),
            ('resource_id', None),
            ('resource_type', None),
            ('service_id', None),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        exc = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-volume-api-version 3.24 or greater is required', str(exc)
        )

    def test_cleanup_with_args(self):
        self.set_volume_api_version('3.24')

        fake_cluster = 'fake-cluster'
        fake_host = 'fake-host'
        fake_binary = 'fake-service'
        fake_resource_id = str(uuid.uuid4())
        fake_resource_type = 'Volume'
        fake_service_id = 1
        arglist = [
            '--cluster',
            fake_cluster,
            '--host',
            fake_host,
            '--binary',
            fake_binary,
            '--down',
            '--enabled',
            '--resource-id',
            fake_resource_id,
            '--resource-type',
            fake_resource_type,
            '--service-id',
            str(fake_service_id),
        ]
        verifylist = [
            ('cluster', fake_cluster),
            ('host', fake_host),
            ('binary', fake_binary),
            ('is_up', False),
            ('disabled', False),
            ('resource_id', fake_resource_id),
            ('resource_type', fake_resource_type),
            ('service_id', fake_service_id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        expected_columns = ('ID', 'Cluster Name', 'Host', 'Binary', 'Status')
        expected_data = (
            (
                1,
                'fake_cluster',
                'devstack@fakedriver-1',
                'cinder-volume',
                'Cleaning',
            ),
            (
                2,
                'new_cluster',
                'devstack@fakedriver-2',
                'cinder-scheduler',
                'Unavailable',
            ),
        )
        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(expected_columns, columns)
        self.assertEqual(expected_data, tuple(data))

        self.volume_client.cleanup_service_workers.assert_called_once_with(
            cluster_name=fake_cluster,
            host=fake_host,
            binary=fake_binary,
            is_up=False,
            disabled=False,
            resource_id=fake_resource_id,
            resource_type=fake_resource_type,
            service_id=fake_service_id,
        )
