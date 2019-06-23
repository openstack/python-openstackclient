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

import copy
import functools
import logging

from cliff import columns as cliff_columns
from osc_lib.cli import parseractions
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils
import six

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
        super(VolumeIdColumn, self).__init__(value)
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
        parser = super(CreateVolumeBackup, self).get_parser(prog_name)
        parser.add_argument(
            "volume",
            metavar="<volume>",
            help=_("Volume to backup (name or ID)")
        )
        parser.add_argument(
            "--name",
            metavar="<name>",
            help=_("Name of the backup")
        )
        parser.add_argument(
            "--description",
            metavar="<description>",
            help=_("Description of the backup")
        )
        parser.add_argument(
            "--container",
            metavar="<container>",
            help=_("Optional backup container name")
        )
        parser.add_argument(
            "--snapshot",
            metavar="<snapshot>",
            help=_("Snapshot to backup (name or ID)")
        )
        parser.add_argument(
            '--force',
            action='store_true',
            default=False,
            help=_("Allow to back up an in-use volume")
        )
        parser.add_argument(
            '--incremental',
            action='store_true',
            default=False,
            help=_("Perform an incremental backup")
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        volume_id = utils.find_resource(
            volume_client.volumes, parsed_args.volume).id
        snapshot_id = None
        if parsed_args.snapshot:
            snapshot_id = utils.find_resource(
                volume_client.volume_snapshots, parsed_args.snapshot).id
        backup = volume_client.backups.create(
            volume_id,
            container=parsed_args.container,
            name=parsed_args.name,
            description=parsed_args.description,
            force=parsed_args.force,
            incremental=parsed_args.incremental,
            snapshot_id=snapshot_id,
        )
        backup._info.pop("links", None)
        return zip(*sorted(six.iteritems(backup._info)))


class DeleteVolumeBackup(command.Command):
    _description = _("Delete volume backup(s)")

    def get_parser(self, prog_name):
        parser = super(DeleteVolumeBackup, self).get_parser(prog_name)
        parser.add_argument(
            "backups",
            metavar="<backup>",
            nargs="+",
            help=_("Backup(s) to delete (name or ID)")
        )
        parser.add_argument(
            '--force',
            action='store_true',
            default=False,
            help=_("Allow delete in state other than error or available")
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        result = 0

        for i in parsed_args.backups:
            try:
                backup_id = utils.find_resource(
                    volume_client.backups, i).id
                volume_client.backups.delete(backup_id, parsed_args.force)
            except Exception as e:
                result += 1
                LOG.error(_("Failed to delete backup with "
                            "name or ID '%(backup)s': %(e)s")
                          % {'backup': i, 'e': e})

        if result > 0:
            total = len(parsed_args.backups)
            msg = (_("%(result)s of %(total)s backups failed "
                   "to delete.") % {'result': result, 'total': total})
            raise exceptions.CommandError(msg)


class ListVolumeBackup(command.Lister):
    _description = _("List volume backups")

    def get_parser(self, prog_name):
        parser = super(ListVolumeBackup, self).get_parser(prog_name)
        parser.add_argument(
            "--long",
            action="store_true",
            default=False,
            help=_("List additional fields in output")
        )
        parser.add_argument(
            "--name",
            metavar="<name>",
            help=_("Filters results by the backup name")
        )
        parser.add_argument(
            "--status",
            metavar="<status>",
            choices=['creating', 'available', 'deleting',
                     'error', 'restoring', 'error_restoring'],
            help=_("Filters results by the backup status "
                   "('creating', 'available', 'deleting', "
                   "'error', 'restoring' or 'error_restoring')")
        )
        parser.add_argument(
            "--volume",
            metavar="<volume>",
            help=_("Filters results by the volume which they "
                   "backup (name or ID)")
        )
        parser.add_argument(
            '--marker',
            metavar='<volume-backup>',
            help=_('The last backup of the previous page (name or ID)'),
        )
        parser.add_argument(
            '--limit',
            type=int,
            action=parseractions.NonNegativeAction,
            metavar='<num-backups>',
            help=_('Maximum number of backups to display'),
        )
        parser.add_argument(
            '--all-projects',
            action='store_true',
            default=False,
            help=_('Include all projects (admin only)'),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume

        if parsed_args.long:
            columns = ['ID', 'Name', 'Description', 'Status', 'Size',
                       'Availability Zone', 'Volume ID', 'Container']
            column_headers = copy.deepcopy(columns)
            column_headers[6] = 'Volume'
        else:
            columns = ['ID', 'Name', 'Description', 'Status', 'Size']
            column_headers = columns

        # Cache the volume list
        volume_cache = {}
        try:
            for s in volume_client.volumes.list():
                volume_cache[s.id] = s
        except Exception:
            # Just forget it if there's any trouble
            pass
        _VolumeIdColumn = functools.partial(VolumeIdColumn,
                                            volume_cache=volume_cache)

        filter_volume_id = None
        if parsed_args.volume:
            filter_volume_id = utils.find_resource(volume_client.volumes,
                                                   parsed_args.volume).id
        marker_backup_id = None
        if parsed_args.marker:
            marker_backup_id = utils.find_resource(volume_client.backups,
                                                   parsed_args.marker).id
        search_opts = {
            'name': parsed_args.name,
            'status': parsed_args.status,
            'volume_id': filter_volume_id,
            'all_tenants': parsed_args.all_projects,
        }
        data = volume_client.backups.list(
            search_opts=search_opts,
            marker=marker_backup_id,
            limit=parsed_args.limit,
        )

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                    formatters={'Volume ID': _VolumeIdColumn},
                ) for s in data))


class RestoreVolumeBackup(command.ShowOne):
    _description = _("Restore volume backup")

    def get_parser(self, prog_name):
        parser = super(RestoreVolumeBackup, self).get_parser(prog_name)
        parser.add_argument(
            "backup",
            metavar="<backup>",
            help=_("Backup to restore (name or ID)")
        )
        parser.add_argument(
            "volume",
            metavar="<volume>",
            help=_("Volume to restore to (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        backup = utils.find_resource(volume_client.backups, parsed_args.backup)
        destination_volume = utils.find_resource(volume_client.volumes,
                                                 parsed_args.volume)
        backup = volume_client.restores.restore(backup.id,
                                                destination_volume.id)
        return zip(*sorted(six.iteritems(backup._info)))


class SetVolumeBackup(command.Command):
    _description = _("Set volume backup properties")

    def get_parser(self, prog_name):
        parser = super(SetVolumeBackup, self).get_parser(prog_name)
        parser.add_argument(
            "backup",
            metavar="<backup>",
            help=_("Backup to modify (name or ID)")
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('New backup name')
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('New backup description')
        )
        parser.add_argument(
            '--state',
            metavar='<state>',
            choices=['available', 'error'],
            help=_('New backup state ("available" or "error") (admin only) '
                   '(This option simply changes the state of the backup '
                   'in the database with no regard to actual status, '
                   'exercise caution when using)'),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        backup = utils.find_resource(volume_client.backups,
                                     parsed_args.backup)
        result = 0
        if parsed_args.state:
            try:
                volume_client.backups.reset_state(
                    backup.id, parsed_args.state)
            except Exception as e:
                LOG.error(_("Failed to set backup state: %s"), e)
                result += 1

        kwargs = {}
        if parsed_args.name:
            kwargs['name'] = parsed_args.name
        if parsed_args.description:
            kwargs['description'] = parsed_args.description
        if kwargs:
            try:
                volume_client.backups.update(backup.id, **kwargs)
            except Exception as e:
                LOG.error(_("Failed to update backup name "
                          "or description: %s"), e)
                result += 1

        if result > 0:
            raise exceptions.CommandError(_("One or more of the "
                                          "set operations failed"))


class ShowVolumeBackup(command.ShowOne):
    _description = _("Display volume backup details")

    def get_parser(self, prog_name):
        parser = super(ShowVolumeBackup, self).get_parser(prog_name)
        parser.add_argument(
            "backup",
            metavar="<backup>",
            help=_("Backup to display (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        backup = utils.find_resource(volume_client.backups,
                                     parsed_args.backup)
        backup._info.pop("links", None)
        return zip(*sorted(six.iteritems(backup._info)))
