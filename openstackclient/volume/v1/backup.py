#   Copyright 2012-2013 OpenStack Foundation
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

"""Volume v1 Backup action implementations"""

import copy
import logging

from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils
import six

from openstackclient.i18n import _


LOG = logging.getLogger(__name__)


class CreateVolumeBackup(command.ShowOne):
    _description = _("Create new volume backup")

    def get_parser(self, prog_name):
        parser = super(CreateVolumeBackup, self).get_parser(prog_name)
        parser.add_argument(
            'volume',
            metavar='<volume>',
            help=_('Volume to backup (name or ID)'),
        )
        parser.add_argument(
            '--container',
            metavar='<container>',
            required=False,
            help=_('Optional backup container name'),
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('Name of the backup'),
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('Description of the backup'),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        volume_id = utils.find_resource(volume_client.volumes,
                                        parsed_args.volume).id
        backup = volume_client.backups.create(
            volume_id,
            parsed_args.container,
            parsed_args.name,
            parsed_args.description
        )

        backup._info.pop('links')
        return zip(*sorted(six.iteritems(backup._info)))


class CreateBackup(CreateVolumeBackup):
    _description = _("Create new backup")

    # TODO(Huanxuan Ao): Remove this class and ``backup create`` command
    #                    two cycles after Newton.

    # This notifies cliff to not display the help for this command
    deprecated = True

    log = logging.getLogger('deprecated')

    def take_action(self, parsed_args):
        self.log.warning(_('This command has been deprecated. '
                           'Please use "volume backup create" instead.'))
        return super(CreateBackup, self).take_action(parsed_args)


class DeleteVolumeBackup(command.Command):
    _description = _("Delete volume backup(s)")

    def get_parser(self, prog_name):
        parser = super(DeleteVolumeBackup, self).get_parser(prog_name)
        parser.add_argument(
            'backups',
            metavar='<backup>',
            nargs="+",
            help=_('Backup(s) to delete (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        result = 0

        for i in parsed_args.backups:
            try:
                backup_id = utils.find_resource(
                    volume_client.backups, i).id
                volume_client.backups.delete(backup_id)
            except Exception as e:
                result += 1
                LOG.error(_("Failed to delete backup with "
                            "name or ID '%(backup)s': %(e)s"),
                          {'backup': i, 'e': e})

        if result > 0:
            total = len(parsed_args.backups)
            msg = (_("%(result)s of %(total)s backups failed "
                   "to delete.") % {'result': result, 'total': total})
            raise exceptions.CommandError(msg)


class DeleteBackup(DeleteVolumeBackup):
    _description = _("Delete backup(s)")

    # TODO(Huanxuan Ao): Remove this class and ``backup delete`` command
    #                    two cycles after Newton.

    # This notifies cliff to not display the help for this command
    deprecated = True

    log = logging.getLogger('deprecated')

    def take_action(self, parsed_args):
        self.log.warning(_('This command has been deprecated. '
                           'Please use "volume backup delete" instead.'))
        return super(DeleteBackup, self).take_action(parsed_args)


class ListVolumeBackup(command.Lister):
    _description = _("List volume backups")

    def get_parser(self, prog_name):
        parser = super(ListVolumeBackup, self).get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_('List additional fields in output'),
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
            '--all-projects',
            action='store_true',
            default=False,
            help=_('Include all projects (admin only)'),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume

        def _format_volume_id(volume_id):
            """Return a volume name if available

            :param volume_id: a volume ID
            :rtype: either the volume ID or name
            """

            volume = volume_id
            if volume_id in volume_cache.keys():
                volume = volume_cache[volume_id].display_name
            return volume

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

        filter_volume_id = None
        if parsed_args.volume:
            filter_volume_id = utils.find_resource(volume_client.volumes,
                                                   parsed_args.volume).id
        search_opts = {
            'name': parsed_args.name,
            'status': parsed_args.status,
            'volume_id': filter_volume_id,
            'all_tenants': parsed_args.all_projects,
        }
        data = volume_client.backups.list(
            search_opts=search_opts,
        )

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                    formatters={'Volume ID': _format_volume_id},
                ) for s in data))


class ListBackup(ListVolumeBackup):
    _description = _("List backups")

    # TODO(Huanxuan Ao): Remove this class and ``backup list`` command
    #                    two cycles after Newton.

    # This notifies cliff to not display the help for this command
    deprecated = True

    log = logging.getLogger('deprecated')

    def take_action(self, parsed_args):
        self.log.warning(_('This command has been deprecated. '
                           'Please use "volume backup list" instead.'))
        return super(ListBackup, self).take_action(parsed_args)


class RestoreVolumeBackup(command.Command):
    _description = _("Restore volume backup")

    def get_parser(self, prog_name):
        parser = super(RestoreVolumeBackup, self).get_parser(prog_name)
        parser.add_argument(
            'backup',
            metavar='<backup>',
            help=_('Backup to restore (name or ID)')
        )
        parser.add_argument(
            'volume',
            metavar='<volume>',
            help=_('Volume to restore to (name or ID)')
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        backup = utils.find_resource(volume_client.backups,
                                     parsed_args.backup)
        destination_volume = utils.find_resource(volume_client.volumes,
                                                 parsed_args.volume)
        return volume_client.restores.restore(backup.id,
                                              destination_volume.id)


class RestoreBackup(RestoreVolumeBackup):
    _description = _("Restore backup")

    # TODO(Huanxuan Ao): Remove this class and ``backup restore`` command
    #                    two cycles after Newton.

    # This notifies cliff to not display the help for this command
    deprecated = True

    log = logging.getLogger('deprecated')

    def take_action(self, parsed_args):
        self.log.warning(_('This command has been deprecated. '
                           'Please use "volume backup restore" instead.'))
        return super(RestoreBackup, self).take_action(parsed_args)


class ShowVolumeBackup(command.ShowOne):
    _description = _("Display volume backup details")

    def get_parser(self, prog_name):
        parser = super(ShowVolumeBackup, self).get_parser(prog_name)
        parser.add_argument(
            'backup',
            metavar='<backup>',
            help=_('Backup to display (name or ID)')
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        backup = utils.find_resource(volume_client.backups,
                                     parsed_args.backup)
        backup._info.pop('links')
        return zip(*sorted(six.iteritems(backup._info)))


class ShowBackup(ShowVolumeBackup):
    _description = _("Display backup details")

    # TODO(Huanxuan Ao): Remove this class and ``backup show`` command
    #                    two cycles after Newton.

    # This notifies cliff to not display the help for this command
    deprecated = True

    log = logging.getLogger('deprecated')

    def take_action(self, parsed_args):
        self.log.warning(_('This command has been deprecated. '
                           'Please use "volume backup show" instead.'))
        return super(ShowBackup, self).take_action(parsed_args)
