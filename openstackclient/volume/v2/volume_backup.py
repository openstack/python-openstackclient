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

"""Volume v2 Backup action implementations"""

import functools
import logging

from cliff import columns as cliff_columns
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.common import pagination
from openstackclient.i18n import _

LOG = logging.getLogger(__name__)


class VolumeIdColumn(cliff_columns.FormattableColumn):
    """Formattable column for volume ID column.

    Unlike the parent FormattableColumn class, the initializer of the
    class takes volume_cache as the second argument.
    osc_lib.utils.get_item_properties instantiate cliff FormattableColumn
    object with a single parameter "column value", so you need to pass
    a partially initialized class like
    ``functools.partial(VolumeIdColumn, volume_cache)``.
    """

    def __init__(self, value, volume_cache=None):
        super().__init__(value)
        self._volume_cache = volume_cache or {}

    def human_readable(self):
        """Return a volume name if available

        :rtype: either the volume ID or name
        """
        volume_id = self._value
        volume = volume_id
        if volume_id in self._volume_cache.keys():
            volume = self._volume_cache[volume_id].name
        return volume


class CreateVolumeBackup(command.ShowOne):
    _description = _("Create new volume backup")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "volume",
            metavar="<volume>",
            help=_("Volume to backup (name or ID)"),
        )
        parser.add_argument(
            "--name", metavar="<name>", help=_("Name of the backup")
        )
        parser.add_argument(
            "--description",
            metavar="<description>",
            help=_("Description of the backup"),
        )
        parser.add_argument(
            "--container",
            metavar="<container>",
            help=_("Optional backup container name"),
        )
        parser.add_argument(
            "--snapshot",
            metavar="<snapshot>",
            help=_("Snapshot to backup (name or ID)"),
        )
        parser.add_argument(
            '--force',
            action='store_true',
            default=False,
            help=_("Allow to back up an in-use volume"),
        )
        parser.add_argument(
            '--incremental',
            action='store_true',
            default=False,
            help=_("Perform an incremental backup"),
        )
        parser.add_argument(
            '--no-incremental',
            action='store_false',
            help=_("Do not perform an incremental backup"),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.sdk_connection.volume

        volume_id = volume_client.find_volume(
            parsed_args.volume,
            ignore_missing=False,
        ).id

        kwargs = {}

        if parsed_args.snapshot:
            kwargs['snapshot_id'] = volume_client.find_snapshot(
                parsed_args.snapshot,
                ignore_missing=False,
            ).id

        columns: tuple[str, ...] = (
            "id",
            "name",
            "volume_id",
        )
        backup = volume_client.create_backup(
            volume_id=volume_id,
            container=parsed_args.container,
            name=parsed_args.name,
            description=parsed_args.description,
            force=parsed_args.force,
            is_incremental=parsed_args.incremental,
            **kwargs,
        )
        data = utils.get_dict_properties(backup, columns)
        return (columns, data)


class DeleteVolumeBackup(command.Command):
    _description = _("Delete volume backup(s)")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "backups",
            metavar="<backup>",
            nargs="+",
            help=_("Backup(s) to delete (name or ID)"),
        )
        parser.add_argument(
            '--force',
            action='store_true',
            default=False,
            help=_("Allow delete in state other than error or available"),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.sdk_connection.volume
        result = 0

        for backup in parsed_args.backups:
            try:
                backup_id = volume_client.find_backup(
                    backup, ignore_missing=False
                ).id
                volume_client.delete_backup(
                    backup_id,
                    ignore_missing=False,
                    force=parsed_args.force,
                )
            except Exception as e:
                result += 1
                LOG.error(
                    _(
                        "Failed to delete backup with "
                        "name or ID '%(backup)s': %(e)s"
                    )
                    % {'backup': backup, 'e': e}
                )

        if result > 0:
            total = len(parsed_args.backups)
            msg = _("%(result)s of %(total)s backups failed to delete.") % {
                'result': result,
                'total': total,
            }
            raise exceptions.CommandError(msg)


class ListVolumeBackup(command.Lister):
    _description = _("List volume backups")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "--long",
            action="store_true",
            default=False,
            help=_("List additional fields in output"),
        )
        parser.add_argument(
            "--name",
            metavar="<name>",
            help=_("Filters results by the backup name"),
        )
        parser.add_argument(
            "--status",
            metavar="<status>",
            choices=[
                'creating',
                'available',
                'deleting',
                'error',
                'restoring',
                'error_restoring',
            ],
            help=_(
                "Filters results by the backup status, one of: "
                "creating, available, deleting, error, restoring or "
                "error_restoring"
            ),
        )
        parser.add_argument(
            "--volume",
            metavar="<volume>",
            help=_(
                "Filters results by the volume which they backup (name or ID)"
            ),
        )
        pagination.add_marker_pagination_option_to_parser(parser)
        parser.add_argument(
            '--all-projects',
            action='store_true',
            default=False,
            help=_('Include all projects (admin only)'),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.sdk_connection.volume

        columns: tuple[str, ...] = (
            'id',
            'name',
            'description',
            'status',
            'size',
            'is_incremental',
            'created_at',
        )
        column_headers: tuple[str, ...] = (
            'ID',
            'Name',
            'Description',
            'Status',
            'Size',
            'Incremental',
            'Created At',
        )
        if parsed_args.long:
            columns += ('availability_zone', 'volume_id', 'container')
            column_headers += ('Availability Zone', 'Volume', 'Container')

        # Cache the volume list
        volume_cache = {}
        try:
            for s in volume_client.volumes():
                volume_cache[s.id] = s
        except Exception:  # noqa: S110
            # Just forget it if there's any trouble
            pass

        _VolumeIdColumn = functools.partial(
            VolumeIdColumn, volume_cache=volume_cache
        )

        filter_volume_id = None
        if parsed_args.volume:
            try:
                filter_volume_id = volume_client.find_volume(
                    parsed_args.volume,
                    ignore_missing=False,
                ).id
            except exceptions.CommandError:
                # Volume with that ID does not exist, but search for backups
                # for that volume nevertheless
                LOG.debug(
                    "No volume with ID %s existing, continuing to "
                    "search for backups for that volume ID",
                    parsed_args.volume,
                )
                filter_volume_id = parsed_args.volume

        marker_backup_id = None
        if parsed_args.marker:
            marker_backup_id = volume_client.find_backup(
                parsed_args.marker,
                ignore_missing=False,
            ).id

        data = volume_client.backups(
            name=parsed_args.name,
            status=parsed_args.status,
            volume_id=filter_volume_id,
            all_tenants=parsed_args.all_projects,
            marker=marker_backup_id,
            limit=parsed_args.limit,
        )

        return (
            column_headers,
            (
                utils.get_item_properties(
                    s,
                    columns,
                    formatters={'volume_id': _VolumeIdColumn},
                )
                for s in data
            ),
        )


class RestoreVolumeBackup(command.ShowOne):
    _description = _("Restore volume backup")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "backup",
            metavar="<backup>",
            help=_("Backup to restore (name or ID)"),
        )
        parser.add_argument(
            "volume",
            metavar="<volume>",
            nargs="?",
            help=_(
                "Volume to restore to "
                "(name or ID for existing volume, name only for new volume) "
                "(default to None)"
            ),
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help=_(
                "Restore the backup to an existing volume (default to False)"
            ),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.sdk_connection.volume

        backup = volume_client.find_backup(
            parsed_args.backup,
            ignore_missing=False,
        )

        columns: tuple[str, ...] = (
            'id',
            'volume_id',
            'volume_name',
        )

        volume_name = None
        volume_id = None
        try:
            volume_id = volume_client.find_volume(
                parsed_args.volume,
                ignore_missing=False,
            ).id
        except Exception:
            volume_name = parsed_args.volume
        else:
            # If we didn't fail, the volume must already exist. We only allow
            # this to work if the user forced things
            if not parsed_args.force:
                msg = _(
                    "Volume '%s' already exists; if you want to restore the "
                    "backup to it you need to specify the '--force' option"
                )
                raise exceptions.CommandError(msg % parsed_args.volume)

        restore = volume_client.restore_backup(
            backup.id,
            volume_id=volume_id,
            name=volume_name,
        )

        data = utils.get_dict_properties(restore, columns)
        return (columns, data)


class SetVolumeBackup(command.Command):
    _description = _("Set volume backup properties")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "backup",
            metavar="<backup>",
            help=_("Backup to modify (name or ID)"),
        )
        parser.add_argument(
            '--state',
            metavar='<state>',
            choices=['available', 'error'],
            help=_(
                'New backup state ("available" or "error") (admin only) '
                '(This option simply changes the state of the backup '
                'in the database with no regard to actual status; '
                'exercise caution when using)'
            ),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.sdk_connection.volume

        backup = volume_client.find_backup(
            parsed_args.backup,
            ignore_missing=False,
        )

        result = 0
        if parsed_args.state:
            try:
                volume_client.reset_backup_status(
                    backup, status=parsed_args.state
                )
            except Exception as e:
                LOG.error(_("Failed to set backup state: %s"), e)
                result += 1

        if result > 0:
            msg = _("One or more of the set operations failed")
            raise exceptions.CommandError(msg)


class ShowVolumeBackup(command.ShowOne):
    _description = _("Display volume backup details")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "backup",
            metavar="<backup>",
            help=_("Backup to display (name or ID)"),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.sdk_connection.volume
        backup = volume_client.find_backup(parsed_args.backup)
        columns: tuple[str, ...] = (
            "availability_zone",
            "container",
            "created_at",
            "data_timestamp",
            "description",
            "fail_reason",
            "has_dependent_backups",
            "id",
            "is_incremental",
            "name",
            "object_count",
            "size",
            "snapshot_id",
            "status",
            "updated_at",
            "volume_id",
        )
        data = utils.get_dict_properties(backup, columns)
        return (columns, data)
