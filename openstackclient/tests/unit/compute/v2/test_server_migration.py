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

from osc_lib import exceptions
from osc_lib import utils as common_utils

from openstackclient.compute.v2 import server_migration
from openstackclient.tests.unit.compute.v2 import fakes as compute_fakes
from openstackclient.tests.unit.identity.v3 import fakes as identity_fakes


class TestListMigration(compute_fakes.TestComputev2):
    """Test fetch all migrations."""

    MIGRATION_COLUMNS = [
        'Source Node',
        'Dest Node',
        'Source Compute',
        'Dest Compute',
        'Dest Host',
        'Status',
        'Server UUID',
        'Old Flavor',
        'New Flavor',
        'Created At',
        'Updated At',
    ]

    MIGRATION_FIELDS = [
        'source_node',
        'dest_node',
        'source_compute',
        'dest_compute',
        'dest_host',
        'status',
        'server_id',
        'old_flavor_id',
        'new_flavor_id',
        'created_at',
        'updated_at',
    ]

    def setUp(self):
        super().setUp()

        self.server = compute_fakes.create_one_sdk_server()
        self.compute_client.find_server.return_value = self.server

        self.migrations = compute_fakes.create_migrations(count=3)
        self.compute_client.migrations.return_value = self.migrations

        self.data = (
            common_utils.get_item_properties(s, self.MIGRATION_FIELDS)
            for s in self.migrations
        )

        # Get the command object to test
        self.cmd = server_migration.ListMigration(self.app, None)

    def test_server_migration_list_no_options(self):
        arglist = []
        verifylist = []

        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {}

        self.compute_client.migrations.assert_called_with(**kwargs)

        self.assertEqual(self.MIGRATION_COLUMNS, columns)
        self.assertEqual(tuple(self.data), tuple(data))

    def test_server_migration_list(self):
        arglist = [
            '--server',
            'server1',
            '--host',
            'host1',
            '--status',
            'migrating',
            '--type',
            'cold-migration',
        ]
        verifylist = [
            ('server', 'server1'),
            ('host', 'host1'),
            ('status', 'migrating'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'status': 'migrating',
            'host': 'host1',
            'instance_uuid': self.server.id,
            'migration_type': 'migration',
        }

        self.compute_client.find_server.assert_called_with(
            'server1', ignore_missing=False
        )
        self.compute_client.migrations.assert_called_with(**kwargs)

        self.assertEqual(self.MIGRATION_COLUMNS, columns)
        self.assertEqual(tuple(self.data), tuple(data))


class TestListMigrationV223(TestListMigration):
    """Test fetch all migrations."""

    MIGRATION_COLUMNS = [
        'Id',
        'Source Node',
        'Dest Node',
        'Source Compute',
        'Dest Compute',
        'Dest Host',
        'Status',
        'Server UUID',
        'Old Flavor',
        'New Flavor',
        'Type',
        'Created At',
        'Updated At',
    ]

    # These are the Migration object fields.
    MIGRATION_FIELDS = [
        'id',
        'source_node',
        'dest_node',
        'source_compute',
        'dest_compute',
        'dest_host',
        'status',
        'server_id',
        'old_flavor_id',
        'new_flavor_id',
        'migration_type',
        'created_at',
        'updated_at',
    ]

    def setUp(self):
        super().setUp()

        self.set_compute_api_version('2.23')

    def test_server_migration_list(self):
        arglist = ['--status', 'migrating']
        verifylist = [('status', 'migrating')]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'status': 'migrating',
        }

        self.compute_client.migrations.assert_called_with(**kwargs)

        self.assertEqual(self.MIGRATION_COLUMNS, columns)
        self.assertEqual(tuple(self.data), tuple(data))


class TestListMigrationV259(TestListMigration):
    """Test fetch all migrations."""

    MIGRATION_COLUMNS = [
        'Id',
        'UUID',
        'Source Node',
        'Dest Node',
        'Source Compute',
        'Dest Compute',
        'Dest Host',
        'Status',
        'Server UUID',
        'Old Flavor',
        'New Flavor',
        'Type',
        'Created At',
        'Updated At',
    ]

    # These are the Migration object fields.
    MIGRATION_FIELDS = [
        'id',
        'uuid',
        'source_node',
        'dest_node',
        'source_compute',
        'dest_compute',
        'dest_host',
        'status',
        'server_id',
        'old_flavor_id',
        'new_flavor_id',
        'migration_type',
        'created_at',
        'updated_at',
    ]

    def setUp(self):
        super().setUp()

        self.set_compute_api_version('2.59')

    def test_server_migration_list(self):
        arglist = [
            '--status',
            'migrating',
            '--limit',
            '1',
            '--marker',
            'test_kp',
            '--changes-since',
            '2019-08-09T08:03:25Z',
        ]
        verifylist = [
            ('status', 'migrating'),
            ('limit', 1),
            ('marker', 'test_kp'),
            ('changes_since', '2019-08-09T08:03:25Z'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'status': 'migrating',
            'limit': 1,
            'paginated': False,
            'marker': 'test_kp',
            'changes_since': '2019-08-09T08:03:25Z',
        }

        self.compute_client.migrations.assert_called_with(**kwargs)

        self.assertEqual(self.MIGRATION_COLUMNS, columns)
        self.assertEqual(tuple(self.data), tuple(data))

    def test_server_migration_list_with_limit_pre_v259(self):
        self.set_compute_api_version('2.58')

        arglist = ['--status', 'migrating', '--limit', '1']
        verifylist = [('status', 'migrating'), ('limit', 1)]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        ex = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-compute-api-version 2.59 or greater is required', str(ex)
        )

    def test_server_migration_list_with_marker_pre_v259(self):
        self.set_compute_api_version('2.58')

        arglist = ['--status', 'migrating', '--marker', 'test_kp']
        verifylist = [('status', 'migrating'), ('marker', 'test_kp')]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        ex = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-compute-api-version 2.59 or greater is required', str(ex)
        )

    def test_server_migration_list_with_changes_since_pre_v259(self):
        self.set_compute_api_version('2.58')

        arglist = [
            '--status',
            'migrating',
            '--changes-since',
            '2019-08-09T08:03:25Z',
        ]
        verifylist = [
            ('status', 'migrating'),
            ('changes_since', '2019-08-09T08:03:25Z'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        ex = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-compute-api-version 2.59 or greater is required', str(ex)
        )


class TestListMigrationV266(TestListMigration):
    """Test fetch all migrations by changes-before."""

    MIGRATION_COLUMNS = [
        'Id',
        'UUID',
        'Source Node',
        'Dest Node',
        'Source Compute',
        'Dest Compute',
        'Dest Host',
        'Status',
        'Server UUID',
        'Old Flavor',
        'New Flavor',
        'Type',
        'Created At',
        'Updated At',
    ]

    # These are the Migration object fields.
    MIGRATION_FIELDS = [
        'id',
        'uuid',
        'source_node',
        'dest_node',
        'source_compute',
        'dest_compute',
        'dest_host',
        'status',
        'server_id',
        'old_flavor_id',
        'new_flavor_id',
        'migration_type',
        'created_at',
        'updated_at',
    ]

    def setUp(self):
        super().setUp()

        self.set_compute_api_version('2.66')

    def test_server_migration_list_with_changes_before(self):
        arglist = [
            '--status',
            'migrating',
            '--limit',
            '1',
            '--marker',
            'test_kp',
            '--changes-since',
            '2019-08-07T08:03:25Z',
            '--changes-before',
            '2019-08-09T08:03:25Z',
        ]
        verifylist = [
            ('status', 'migrating'),
            ('limit', 1),
            ('marker', 'test_kp'),
            ('changes_since', '2019-08-07T08:03:25Z'),
            ('changes_before', '2019-08-09T08:03:25Z'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'status': 'migrating',
            'limit': 1,
            'paginated': False,
            'marker': 'test_kp',
            'changes_since': '2019-08-07T08:03:25Z',
            'changes_before': '2019-08-09T08:03:25Z',
        }

        self.compute_client.migrations.assert_called_with(**kwargs)

        self.assertEqual(self.MIGRATION_COLUMNS, columns)
        self.assertEqual(tuple(self.data), tuple(data))

    def test_server_migration_list_with_changes_before_pre_v266(self):
        self.set_compute_api_version('2.65')

        arglist = [
            '--status',
            'migrating',
            '--changes-before',
            '2019-08-09T08:03:25Z',
        ]
        verifylist = [
            ('status', 'migrating'),
            ('changes_before', '2019-08-09T08:03:25Z'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        ex = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-compute-api-version 2.66 or greater is required', str(ex)
        )


class TestListMigrationV280(TestListMigration):
    """Test fetch all migrations by user-id and/or project-id."""

    MIGRATION_COLUMNS = [
        'Id',
        'UUID',
        'Source Node',
        'Dest Node',
        'Source Compute',
        'Dest Compute',
        'Dest Host',
        'Status',
        'Server UUID',
        'Old Flavor',
        'New Flavor',
        'Type',
        'Created At',
        'Updated At',
    ]

    # These are the Migration object fields.
    MIGRATION_FIELDS = [
        'id',
        'uuid',
        'source_node',
        'dest_node',
        'source_compute',
        'dest_compute',
        'dest_host',
        'status',
        'server_id',
        'old_flavor_id',
        'new_flavor_id',
        'migration_type',
        'created_at',
        'updated_at',
    ]

    project = identity_fakes.FakeProject.create_one_project()
    user = identity_fakes.FakeUser.create_one_user()

    def setUp(self):
        super().setUp()

        self.projects_mock = self.identity_client.projects
        self.projects_mock.reset_mock()

        self.users_mock = self.identity_client.users
        self.users_mock.reset_mock()

        self.projects_mock.get.return_value = self.project
        self.users_mock.get.return_value = self.user

        self.set_compute_api_version('2.80')

    def test_server_migration_list_with_project(self):
        arglist = [
            '--status',
            'migrating',
            '--limit',
            '1',
            '--marker',
            'test_kp',
            '--changes-since',
            '2019-08-07T08:03:25Z',
            '--changes-before',
            '2019-08-09T08:03:25Z',
            '--project',
            self.project.id,
        ]
        verifylist = [
            ('status', 'migrating'),
            ('limit', 1),
            ('marker', 'test_kp'),
            ('changes_since', '2019-08-07T08:03:25Z'),
            ('changes_before', '2019-08-09T08:03:25Z'),
            ('project', self.project.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'status': 'migrating',
            'limit': 1,
            'paginated': False,
            'marker': 'test_kp',
            'project_id': self.project.id,
            'changes_since': '2019-08-07T08:03:25Z',
            'changes_before': "2019-08-09T08:03:25Z",
        }

        self.compute_client.migrations.assert_called_with(**kwargs)

        self.MIGRATION_COLUMNS.insert(
            len(self.MIGRATION_COLUMNS) - 2, "Project"
        )
        self.MIGRATION_FIELDS.insert(
            len(self.MIGRATION_FIELDS) - 2, "project_id"
        )
        self.assertEqual(self.MIGRATION_COLUMNS, columns)
        self.assertEqual(tuple(self.data), tuple(data))
        # Clean up global variables MIGRATION_COLUMNS
        self.MIGRATION_COLUMNS.remove('Project')
        # Clean up global variables MIGRATION_FIELDS
        self.MIGRATION_FIELDS.remove('project_id')

    def test_get_migrations_with_project_pre_v280(self):
        self.set_compute_api_version('2.79')

        arglist = [
            '--status',
            'migrating',
            '--changes-before',
            '2019-08-09T08:03:25Z',
            '--project',
            '0c2accde-644a-45fa-8c10-e76debc7fbc3',
        ]
        verifylist = [
            ('status', 'migrating'),
            ('changes_before', '2019-08-09T08:03:25Z'),
            ('project', '0c2accde-644a-45fa-8c10-e76debc7fbc3'),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        ex = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-compute-api-version 2.80 or greater is required', str(ex)
        )

    def test_server_migration_list_with_user(self):
        arglist = [
            '--status',
            'migrating',
            '--limit',
            '1',
            '--marker',
            'test_kp',
            '--changes-since',
            '2019-08-07T08:03:25Z',
            '--changes-before',
            '2019-08-09T08:03:25Z',
            '--user',
            self.user.id,
        ]
        verifylist = [
            ('status', 'migrating'),
            ('limit', 1),
            ('marker', 'test_kp'),
            ('changes_since', '2019-08-07T08:03:25Z'),
            ('changes_before', '2019-08-09T08:03:25Z'),
            ('user', self.user.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'status': 'migrating',
            'limit': 1,
            'paginated': False,
            'marker': 'test_kp',
            'user_id': self.user.id,
            'changes_since': '2019-08-07T08:03:25Z',
            'changes_before': "2019-08-09T08:03:25Z",
        }

        self.compute_client.migrations.assert_called_with(**kwargs)

        self.MIGRATION_COLUMNS.insert(len(self.MIGRATION_COLUMNS) - 2, "User")
        self.MIGRATION_FIELDS.insert(len(self.MIGRATION_FIELDS) - 2, "user_id")
        self.assertEqual(self.MIGRATION_COLUMNS, columns)
        self.assertEqual(tuple(self.data), tuple(data))
        # Clean up global variables MIGRATION_COLUMNS
        self.MIGRATION_COLUMNS.remove('User')
        # Clean up global variables MIGRATION_FIELDS
        self.MIGRATION_FIELDS.remove('user_id')

    def test_get_migrations_with_user_pre_v280(self):
        self.set_compute_api_version('2.79')

        arglist = [
            '--status',
            'migrating',
            '--changes-before',
            '2019-08-09T08:03:25Z',
            '--user',
            self.user.id,
        ]
        verifylist = [
            ('status', 'migrating'),
            ('changes_before', '2019-08-09T08:03:25Z'),
            ('user', self.user.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        ex = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-compute-api-version 2.80 or greater is required', str(ex)
        )

    def test_server_migration_list_with_project_and_user(self):
        arglist = [
            '--status',
            'migrating',
            '--limit',
            '1',
            '--changes-since',
            '2019-08-07T08:03:25Z',
            '--changes-before',
            '2019-08-09T08:03:25Z',
            '--project',
            self.project.id,
            '--user',
            self.user.id,
        ]
        verifylist = [
            ('status', 'migrating'),
            ('limit', 1),
            ('changes_since', '2019-08-07T08:03:25Z'),
            ('changes_before', '2019-08-09T08:03:25Z'),
            ('project', self.project.id),
            ('user', self.user.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        columns, data = self.cmd.take_action(parsed_args)

        # Set expected values
        kwargs = {
            'status': 'migrating',
            'limit': 1,
            'paginated': False,
            'project_id': self.project.id,
            'user_id': self.user.id,
            'changes_since': '2019-08-07T08:03:25Z',
            'changes_before': "2019-08-09T08:03:25Z",
        }

        self.compute_client.migrations.assert_called_with(**kwargs)

        self.MIGRATION_COLUMNS.insert(
            len(self.MIGRATION_COLUMNS) - 2, "Project"
        )
        self.MIGRATION_FIELDS.insert(
            len(self.MIGRATION_FIELDS) - 2, "project_id"
        )
        self.MIGRATION_COLUMNS.insert(len(self.MIGRATION_COLUMNS) - 2, "User")
        self.MIGRATION_FIELDS.insert(len(self.MIGRATION_FIELDS) - 2, "user_id")
        self.assertEqual(self.MIGRATION_COLUMNS, columns)
        self.assertEqual(tuple(self.data), tuple(data))
        # Clean up global variables MIGRATION_COLUMNS
        self.MIGRATION_COLUMNS.remove('Project')
        self.MIGRATION_FIELDS.remove('project_id')
        self.MIGRATION_COLUMNS.remove('User')
        self.MIGRATION_FIELDS.remove('user_id')

    def test_get_migrations_with_project_and_user_pre_v280(self):
        self.set_compute_api_version('2.79')

        arglist = [
            '--status',
            'migrating',
            '--changes-before',
            '2019-08-09T08:03:25Z',
            '--project',
            self.project.id,
            '--user',
            self.user.id,
        ]
        verifylist = [
            ('status', 'migrating'),
            ('changes_before', '2019-08-09T08:03:25Z'),
            ('project', self.project.id),
            ('user', self.user.id),
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)
        ex = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-compute-api-version 2.80 or greater is required', str(ex)
        )


class TestServerMigrationShow(compute_fakes.TestComputev2):
    def setUp(self):
        super().setUp()

        self.server = compute_fakes.create_one_sdk_server()
        self.compute_client.find_server.return_value = self.server

        self.server_migration = compute_fakes.create_one_server_migration()
        self.compute_client.get_server_migration.return_value = (
            self.server_migration
        )
        self.compute_client.server_migrations.return_value = iter(
            [self.server_migration]
        )

        self.columns = (
            'ID',
            'Server UUID',
            'Status',
            'Source Compute',
            'Source Node',
            'Dest Compute',
            'Dest Host',
            'Dest Node',
            'Memory Total Bytes',
            'Memory Processed Bytes',
            'Memory Remaining Bytes',
            'Disk Total Bytes',
            'Disk Processed Bytes',
            'Disk Remaining Bytes',
            'Created At',
            'Updated At',
        )

        self.data = (
            self.server_migration.id,
            self.server_migration.server_id,
            self.server_migration.status,
            self.server_migration.source_compute,
            self.server_migration.source_node,
            self.server_migration.dest_compute,
            self.server_migration.dest_host,
            self.server_migration.dest_node,
            self.server_migration.memory_total_bytes,
            self.server_migration.memory_processed_bytes,
            self.server_migration.memory_remaining_bytes,
            self.server_migration.disk_total_bytes,
            self.server_migration.disk_processed_bytes,
            self.server_migration.disk_remaining_bytes,
            self.server_migration.created_at,
            self.server_migration.updated_at,
        )

        # Get the command object to test
        self.cmd = server_migration.ShowMigration(self.app, None)

    def _test_server_migration_show(self):
        arglist = [
            self.server.id,
            '2',  # arbitrary migration ID
        ]
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

        self.compute_client.find_server.assert_called_with(
            self.server.id, ignore_missing=False
        )
        self.compute_client.get_server_migration.assert_called_with(
            self.server.id, '2', ignore_missing=False
        )

    def test_server_migration_show(self):
        self.set_compute_api_version('2.24')

        self._test_server_migration_show()

    def test_server_migration_show_v259(self):
        self.set_compute_api_version('2.59')

        self.columns += ('UUID',)
        self.data += (self.server_migration.uuid,)

        self._test_server_migration_show()

    def test_server_migration_show_v280(self):
        self.set_compute_api_version('2.80')

        self.columns += ('UUID', 'User ID', 'Project ID')
        self.data += (
            self.server_migration.uuid,
            self.server_migration.user_id,
            self.server_migration.project_id,
        )

        self._test_server_migration_show()

    def test_server_migration_show_pre_v224(self):
        self.set_compute_api_version('2.23')

        arglist = [
            self.server.id,
            '2',  # arbitrary migration ID
        ]
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        ex = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-compute-api-version 2.24 or greater is required', str(ex)
        )

    def test_server_migration_show_by_uuid(self):
        self.set_compute_api_version('2.59')

        self.compute_client.server_migrations.return_value = iter(
            [self.server_migration]
        )

        self.columns += ('UUID',)
        self.data += (self.server_migration.uuid,)

        arglist = [
            self.server.id,
            self.server_migration.uuid,  # arbitrary migration UUID
        ]
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        columns, data = self.cmd.take_action(parsed_args)

        self.assertEqual(self.columns, columns)
        self.assertEqual(self.data, data)

        self.compute_client.find_server.assert_called_with(
            self.server.id, ignore_missing=False
        )
        self.compute_client.server_migrations.assert_called_with(
            self.server.id
        )
        self.compute_client.get_server_migration.assert_not_called()

    def test_server_migration_show_by_uuid_no_matches(self):
        self.set_compute_api_version('2.59')

        self.compute_client.server_migrations.return_value = iter([])

        arglist = [
            self.server.id,
            '69f95745-bfe3-4302-90f7-5b0022cba1ce',  # arbitrary migration UUID
        ]
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        ex = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            'In-progress live migration 69f95745-bfe3-4302-90f7-5b0022cba1ce',
            str(ex),
        )

    def test_server_migration_show_by_uuid_pre_v259(self):
        self.set_compute_api_version('2.58')

        arglist = [
            self.server.id,
            '69f95745-bfe3-4302-90f7-5b0022cba1ce',  # arbitrary migration UUID
        ]
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        ex = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-compute-api-version 2.59 or greater is required', str(ex)
        )

    def test_server_migration_show_invalid_id(self):
        self.set_compute_api_version('2.24')

        arglist = [
            self.server.id,
            'foo',  # invalid migration ID
        ]
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        ex = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            'The <migration> argument must be an ID or UUID', str(ex)
        )


class TestServerMigrationAbort(compute_fakes.TestComputev2):
    def setUp(self):
        super().setUp()

        self.server = compute_fakes.create_one_sdk_server()

        # Return value for utils.find_resource for server.
        self.compute_client.find_server.return_value = self.server

        # Get the command object to test
        self.cmd = server_migration.AbortMigration(self.app, None)

    def test_migration_abort(self):
        self.set_compute_api_version('2.24')

        arglist = [
            self.server.id,
            '2',  # arbitrary migration ID
        ]
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.compute_client.find_server.assert_called_with(
            self.server.id, ignore_missing=False
        )
        self.compute_client.abort_server_migration.assert_called_with(
            '2', self.server.id, ignore_missing=False
        )
        self.assertIsNone(result)

    def test_migration_abort_pre_v224(self):
        self.set_compute_api_version('2.23')

        arglist = [
            self.server.id,
            '2',  # arbitrary migration ID
        ]
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        ex = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-compute-api-version 2.24 or greater is required', str(ex)
        )

    def test_server_migration_abort_by_uuid(self):
        self.set_compute_api_version('2.59')

        self.server_migration = compute_fakes.create_one_server_migration()
        self.compute_client.server_migrations.return_value = iter(
            [self.server_migration]
        )

        arglist = [
            self.server.id,
            self.server_migration.uuid,  # arbitrary migration UUID
        ]
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.compute_client.find_server.assert_called_with(
            self.server.id, ignore_missing=False
        )
        self.compute_client.server_migrations.assert_called_with(
            self.server.id
        )
        self.compute_client.abort_server_migration.assert_called_with(
            self.server_migration.id, self.server.id, ignore_missing=False
        )
        self.assertIsNone(result)

    def test_server_migration_abort_by_uuid_no_matches(self):
        self.set_compute_api_version('2.59')

        self.compute_client.server_migrations.return_value = iter([])

        arglist = [
            self.server.id,
            '69f95745-bfe3-4302-90f7-5b0022cba1ce',  # arbitrary migration UUID
        ]
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        ex = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            'In-progress live migration 69f95745-bfe3-4302-90f7-5b0022cba1ce',
            str(ex),
        )

    def test_server_migration_abort_by_uuid_pre_v259(self):
        self.set_compute_api_version('2.58')

        arglist = [
            self.server.id,
            '69f95745-bfe3-4302-90f7-5b0022cba1ce',  # arbitrary migration UUID
        ]
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        ex = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-compute-api-version 2.59 or greater is required', str(ex)
        )


class TestServerMigrationForceComplete(compute_fakes.TestComputev2):
    def setUp(self):
        super().setUp()

        self.server = compute_fakes.create_one_sdk_server()

        # Return value for utils.find_resource for server.
        self.compute_client.find_server.return_value = self.server

        # Get the command object to test
        self.cmd = server_migration.ForceCompleteMigration(self.app, None)

    def test_migration_force_complete(self):
        self.set_compute_api_version('2.22')

        arglist = [
            self.server.id,
            '2',  # arbitrary migration ID
        ]
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.compute_client.find_server.assert_called_with(
            self.server.id, ignore_missing=False
        )
        self.compute_client.force_complete_server_migration.assert_called_with(
            '2', self.server.id
        )
        self.assertIsNone(result)

    def test_migration_force_complete_pre_v222(self):
        self.set_compute_api_version('2.21')

        arglist = [
            self.server.id,
            '2',  # arbitrary migration ID
        ]
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        ex = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-compute-api-version 2.22 or greater is required', str(ex)
        )

    def test_server_migration_force_complete_by_uuid(self):
        self.set_compute_api_version('2.59')

        self.server_migration = compute_fakes.create_one_server_migration()
        self.compute_client.server_migrations.return_value = iter(
            [self.server_migration]
        )

        arglist = [
            self.server.id,
            self.server_migration.uuid,  # arbitrary migration UUID
        ]
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        result = self.cmd.take_action(parsed_args)

        self.compute_client.find_server.assert_called_with(
            self.server.id, ignore_missing=False
        )
        self.compute_client.server_migrations.assert_called_with(
            self.server.id
        )
        self.compute_client.force_complete_server_migration.assert_called_with(
            self.server_migration.id, self.server.id
        )
        self.assertIsNone(result)

    def test_server_migration_force_complete_by_uuid_no_matches(self):
        self.set_compute_api_version('2.59')

        self.compute_client.server_migrations.return_value = iter([])

        arglist = [
            self.server.id,
            '69f95745-bfe3-4302-90f7-5b0022cba1ce',  # arbitrary migration UUID
        ]
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        ex = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            'In-progress live migration 69f95745-bfe3-4302-90f7-5b0022cba1ce',
            str(ex),
        )

    def test_server_migration_force_complete_by_uuid_pre_v259(self):
        self.set_compute_api_version('2.58')

        arglist = [
            self.server.id,
            '69f95745-bfe3-4302-90f7-5b0022cba1ce',  # arbitrary migration UUID
        ]
        verifylist = []
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        ex = self.assertRaises(
            exceptions.CommandError, self.cmd.take_action, parsed_args
        )
        self.assertIn(
            '--os-compute-api-version 2.59 or greater is required', str(ex)
        )
