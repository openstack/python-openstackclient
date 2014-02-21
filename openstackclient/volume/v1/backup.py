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

import logging
import six

from cliff import command
from cliff import lister
from cliff import show

from openstackclient.common import utils


class CreateBackup(show.ShowOne):
    """Create backup command"""

    log = logging.getLogger(__name__ + '.CreateBackup')

    def get_parser(self, prog_name):
        parser = super(CreateBackup, self).get_parser(prog_name)
        parser.add_argument(
            'volume',
            metavar='<volume>',
            help='The name or ID of the volume to backup',
        )
        parser.add_argument(
            '--container',
            metavar='<container>',
            required=False,
            help='Optional backup container name.',
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            required=False,
            help='Name of the backup',
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help='Description of the backup',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        volume_client = self.app.client_manager.volume
        volume_id = utils.find_resource(volume_client.volumes,
                                        parsed_args.volume).id
        backup = volume_client.backups.create(
            volume_id,
            parsed_args.volume,
            parsed_args.name,
            parsed_args.description
        )

        backup._info.pop('links')
        return zip(*sorted(six.iteritems(backup._info)))


class DeleteBackup(command.Command):
    """Delete backup command"""

    log = logging.getLogger(__name__ + '.DeleteBackup')

    def get_parser(self, prog_name):
        parser = super(DeleteBackup, self).get_parser(prog_name)
        parser.add_argument(
            'backup',
            metavar='<backup>',
            help='Name or ID of backup to delete',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        volume_client = self.app.client_manager.volume
        backup_id = utils.find_resource(volume_client.backups,
                                        parsed_args.backup).id
        volume_client.backups.delete(backup_id)
        return


class ListBackup(lister.Lister):
    """List backup command"""

    log = logging.getLogger(__name__ + '.ListBackup')

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        columns = (
            'ID',
            'Display Name',
            'Display Description',
            'Status',
            'Size'
        )
        data = self.app.client_manager.volume.backups.list()
        return (columns,
                (utils.get_item_properties(
                    s, columns,
                    formatters={},
                ) for s in data))


class RestoreBackup(command.Command):
    """Restore backup command"""

    log = logging.getLogger(__name__ + '.RestoreBackup')

    def get_parser(self, prog_name):
        parser = super(RestoreBackup, self).get_parser(prog_name)
        parser.add_argument(
            'backup',
            metavar='<backup>',
            help='ID of backup to restore')
        parser.add_argument(
            'volume',
            metavar='<dest-volume>',
            help='ID of volume to restore to')
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        volume_client = self.app.client_manager.volume
        backup = utils.find_resource(volume_client.backups,
                                     parsed_args.backup)
        destination_volume = utils.find_resource(volume_client.volumes,
                                                 parsed_args.volume)
        return volume_client.restores.restore(backup.id,
                                              destination_volume.id)


class ShowBackup(show.ShowOne):
    """Show backup command"""

    log = logging.getLogger(__name__ + '.ShowBackup')

    def get_parser(self, prog_name):
        parser = super(ShowBackup, self).get_parser(prog_name)
        parser.add_argument(
            'backup',
            metavar='<backup>',
            help='Name or ID of backup to display')
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        volume_client = self.app.client_manager.volume
        backup = utils.find_resource(volume_client.backups,
                                     parsed_args.backup)
        backup._info.pop('links')
        return zip(*sorted(six.iteritems(backup._info)))
