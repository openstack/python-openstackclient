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

"""Compute v2 Server Migration action implementations"""

import uuid

from openstack import utils as sdk_utils
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.common import pagination
from openstackclient.i18n import _
from openstackclient.identity import common as identity_common


class ListMigration(command.Lister):
    _description = _("""List server migrations""")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--server',
            metavar='<server>',
            help=_('Filter migrations by server (name or ID)'),
        )
        parser.add_argument(
            '--host',
            metavar='<host>',
            help=_('Filter migrations by source or destination host'),
        )
        parser.add_argument(
            '--status',
            metavar='<status>',
            help=_('Filter migrations by status'),
        )
        parser.add_argument(
            '--type',
            metavar='<type>',
            choices=[
                'evacuation',
                'live-migration',
                'cold-migration',
                'resize',
            ],
            help=_('Filter migrations by type'),
        )
        pagination.add_marker_pagination_option_to_parser(parser)
        parser.add_argument(
            '--changes-since',
            dest='changes_since',
            metavar='<changes-since>',
            help=_(
                "List only migrations changed later or equal to a certain "
                "point of time. The provided time should be an ISO 8061 "
                "formatted time, e.g. ``2016-03-04T06:27:59Z``. "
                "(supported with --os-compute-api-version 2.59 or above)"
            ),
        )
        parser.add_argument(
            '--changes-before',
            dest='changes_before',
            metavar='<changes-before>',
            help=_(
                "List only migrations changed earlier or equal to a "
                "certain point of time. The provided time should be an ISO "
                "8061 formatted time, e.g. ``2016-03-04T06:27:59Z``. "
                "(supported with --os-compute-api-version 2.66 or above)"
            ),
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_(
                "Filter migrations by project (name or ID) "
                "(supported with --os-compute-api-version 2.80 or above)"
            ),
        )
        identity_common.add_project_domain_option_to_parser(parser)
        parser.add_argument(
            '--user',
            metavar='<user>',
            help=_(
                "Filter migrations by user (name or ID) "
                "(supported with --os-compute-api-version 2.80 or above)"
            ),
        )
        identity_common.add_user_domain_option_to_parser(parser)
        return parser

    def print_migrations(self, parsed_args, compute_client, migrations):
        column_headers = [
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

        # Response fields coming back from the REST API are not always exactly
        # the same as the column header names.
        columns = [
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

        # Insert migrations UUID after ID
        if sdk_utils.supports_microversion(compute_client, "2.59"):
            column_headers.insert(0, "UUID")
            columns.insert(0, "uuid")

        if sdk_utils.supports_microversion(compute_client, "2.23"):
            column_headers.insert(0, "Id")
            columns.insert(0, "id")
            column_headers.insert(len(column_headers) - 2, "Type")
            columns.insert(len(columns) - 2, "migration_type")

        if sdk_utils.supports_microversion(compute_client, "2.80"):
            if parsed_args.project:
                column_headers.insert(len(column_headers) - 2, "Project")
                columns.insert(len(columns) - 2, "project_id")
            if parsed_args.user:
                column_headers.insert(len(column_headers) - 2, "User")
                columns.insert(len(columns) - 2, "user_id")

        return (
            column_headers,
            (utils.get_item_properties(mig, columns) for mig in migrations),
        )

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        identity_client = self.app.client_manager.identity

        search_opts = {}

        if parsed_args.host is not None:
            search_opts['host'] = parsed_args.host

        if parsed_args.status is not None:
            search_opts['status'] = parsed_args.status

        if parsed_args.server:
            server = compute_client.find_server(
                parsed_args.server, ignore_missing=False
            )
            search_opts['instance_uuid'] = server.id

        if parsed_args.type:
            migration_type = parsed_args.type
            # we're using an alias because the default value is confusing
            if migration_type == 'cold-migration':
                migration_type = 'migration'
            search_opts['migration_type'] = migration_type

        if parsed_args.marker:
            if not sdk_utils.supports_microversion(compute_client, "2.59"):
                msg = _(
                    '--os-compute-api-version 2.59 or greater is required to '
                    'support the --marker option'
                )
                raise exceptions.CommandError(msg)
            search_opts['marker'] = parsed_args.marker

        if parsed_args.limit:
            if not sdk_utils.supports_microversion(compute_client, "2.59"):
                msg = _(
                    '--os-compute-api-version 2.59 or greater is required to '
                    'support the --limit option'
                )
                raise exceptions.CommandError(msg)
            search_opts['limit'] = parsed_args.limit
            search_opts['paginated'] = False

        if parsed_args.changes_since:
            if not sdk_utils.supports_microversion(compute_client, "2.59"):
                msg = _(
                    '--os-compute-api-version 2.59 or greater is required to '
                    'support the --changes-since option'
                )
                raise exceptions.CommandError(msg)
            search_opts['changes_since'] = parsed_args.changes_since

        if parsed_args.changes_before:
            if not sdk_utils.supports_microversion(compute_client, "2.66"):
                msg = _(
                    '--os-compute-api-version 2.66 or greater is required to '
                    'support the --changes-before option'
                )
                raise exceptions.CommandError(msg)
            search_opts['changes_before'] = parsed_args.changes_before

        if parsed_args.project:
            if not sdk_utils.supports_microversion(compute_client, "2.80"):
                msg = _(
                    '--os-compute-api-version 2.80 or greater is required to '
                    'support the --project option'
                )
                raise exceptions.CommandError(msg)

            search_opts['project_id'] = identity_common.find_project(
                identity_client,
                parsed_args.project,
                parsed_args.project_domain,
            ).id

        if parsed_args.user:
            if not sdk_utils.supports_microversion(compute_client, "2.80"):
                msg = _(
                    '--os-compute-api-version 2.80 or greater is required to '
                    'support the --user option'
                )
                raise exceptions.CommandError(msg)

            search_opts['user_id'] = identity_common.find_user(
                identity_client,
                parsed_args.user,
                parsed_args.user_domain,
            ).id

        migrations = list(compute_client.migrations(**search_opts))

        return self.print_migrations(parsed_args, compute_client, migrations)


def _get_migration_by_uuid(compute_client, server_id, migration_uuid):
    for migration in compute_client.server_migrations(server_id):
        if migration.uuid == migration_uuid:
            return migration
    else:
        msg = _(
            'In-progress live migration %(migration)s is not found for '
            'server %(server)s'
        )
        raise exceptions.CommandError(
            msg
            % {
                'migration': migration_uuid,
                'server': server_id,
            }
        )


class ShowMigration(command.ShowOne):
    """Show an in-progress live migration for a given server.

    Note that it is not possible to show cold migrations or completed
    live-migrations. Use 'openstack server migration list' to get details for
    these.
    """

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help=_('Server (name or ID)'),
        )
        parser.add_argument(
            'migration',
            metavar='<migration>',
            help=_("Migration (ID)"),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute

        if not sdk_utils.supports_microversion(compute_client, '2.24'):
            msg = _(
                '--os-compute-api-version 2.24 or greater is required to '
                'support the server migration show command'
            )
            raise exceptions.CommandError(msg)

        if not parsed_args.migration.isdigit():
            try:
                uuid.UUID(parsed_args.migration)
            except ValueError:
                msg = _('The <migration> argument must be an ID or UUID')
                raise exceptions.CommandError(msg)

            if not sdk_utils.supports_microversion(compute_client, '2.59'):
                msg = _(
                    '--os-compute-api-version 2.59 or greater is required to '
                    'retrieve server migrations by UUID'
                )
                raise exceptions.CommandError(msg)

        server = compute_client.find_server(
            parsed_args.server,
            ignore_missing=False,
        )

        # the nova API doesn't currently allow retrieval by UUID but it's a
        # reasonably common operation so emulate this behavior by listing
        # migrations - the responses are identical
        if not parsed_args.migration.isdigit():
            server_migration = _get_migration_by_uuid(
                compute_client,
                server.id,
                parsed_args.migration,
            )
        else:
            server_migration = compute_client.get_server_migration(
                server.id,
                parsed_args.migration,
                ignore_missing=False,
            )

        column_headers: tuple[str, ...] = (
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

        columns: tuple[str, ...] = (
            'id',
            'server_id',
            'status',
            'source_compute',
            'source_node',
            'dest_compute',
            'dest_host',
            'dest_node',
            'memory_total_bytes',
            'memory_processed_bytes',
            'memory_remaining_bytes',
            'disk_total_bytes',
            'disk_processed_bytes',
            'disk_remaining_bytes',
            'created_at',
            'updated_at',
        )

        if sdk_utils.supports_microversion(compute_client, '2.59'):
            column_headers += ('UUID',)
            columns += ('uuid',)

        if sdk_utils.supports_microversion(compute_client, '2.80'):
            column_headers += ('User ID', 'Project ID')
            columns += ('user_id', 'project_id')

        data = utils.get_item_properties(server_migration, columns)
        return column_headers, data


class AbortMigration(command.Command):
    """Cancel an ongoing live migration.

    This command requires ``--os-compute-api-version`` 2.24 or greater.
    """

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help=_('Server (name or ID)'),
        )
        parser.add_argument(
            'migration',
            metavar='<migration>',
            help=_("Migration (ID)"),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute

        if not sdk_utils.supports_microversion(compute_client, '2.24'):
            msg = _(
                '--os-compute-api-version 2.24 or greater is required to '
                'support the server migration abort command'
            )
            raise exceptions.CommandError(msg)

        if not parsed_args.migration.isdigit():
            try:
                uuid.UUID(parsed_args.migration)
            except ValueError:
                msg = _('The <migration> argument must be an ID or UUID')
                raise exceptions.CommandError(msg)

            if not sdk_utils.supports_microversion(compute_client, '2.59'):
                msg = _(
                    '--os-compute-api-version 2.59 or greater is required to '
                    'abort server migrations by UUID'
                )
                raise exceptions.CommandError(msg)

        server = compute_client.find_server(
            parsed_args.server,
            ignore_missing=False,
        )

        # the nova API doesn't currently allow retrieval by UUID but it's a
        # reasonably common operation so emulate this behavior by listing
        # migrations - the responses are identical
        migration_id = parsed_args.migration
        if not parsed_args.migration.isdigit():
            migration_id = _get_migration_by_uuid(
                compute_client,
                server.id,
                parsed_args.migration,
            ).id

        compute_client.abort_server_migration(
            migration_id,
            server.id,
            ignore_missing=False,
        )


class ForceCompleteMigration(command.Command):
    """Force an ongoing live migration to complete.

    This command requires ``--os-compute-api-version`` 2.22 or greater.
    """

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help=_('Server (name or ID)'),
        )
        parser.add_argument(
            'migration', metavar='<migration>', help=_('Migration (ID)')
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute

        if not sdk_utils.supports_microversion(compute_client, '2.22'):
            msg = _(
                '--os-compute-api-version 2.22 or greater is required to '
                'support the server migration force complete command'
            )
            raise exceptions.CommandError(msg)

        if not parsed_args.migration.isdigit():
            try:
                uuid.UUID(parsed_args.migration)
            except ValueError:
                msg = _('The <migration> argument must be an ID or UUID')
                raise exceptions.CommandError(msg)

            if not sdk_utils.supports_microversion(compute_client, '2.59'):
                msg = _(
                    '--os-compute-api-version 2.59 or greater is required to '
                    'abort server migrations by UUID'
                )
                raise exceptions.CommandError(msg)

        server = compute_client.find_server(
            parsed_args.server,
            ignore_missing=False,
        )

        # the nova API doesn't currently allow retrieval by UUID but it's a
        # reasonably common operation so emulate this behavior by listing
        # migrations - the responses are identical
        migration_id = parsed_args.migration
        if not parsed_args.migration.isdigit():
            migration_id = _get_migration_by_uuid(
                compute_client,
                server.id,
                parsed_args.migration,
            ).id

        compute_client.force_complete_server_migration(migration_id, server.id)
