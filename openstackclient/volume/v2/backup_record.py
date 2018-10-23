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

import logging

from osc_lib.command import command
from osc_lib import utils
import six

from openstackclient.i18n import _


LOG = logging.getLogger(__name__)


class ExportBackupRecord(command.ShowOne):
    _description = _('Export volume backup details. Backup information can be '
                     'imported into a new service instance to be able to '
                     'restore.')

    def get_parser(self, prog_name):
        parser = super(ExportBackupRecord, self).get_parser(prog_name)
        parser.add_argument(
            "backup",
            metavar="<backup>",
            help=_("Backup to export (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        backup = utils.find_resource(volume_client.backups, parsed_args.backup)
        backup_data = volume_client.backups.export_record(backup.id)

        # We only want to show "friendly" display names, but also want to keep
        # json structure compatibility with cinderclient
        if parsed_args.formatter == 'table':
            backup_data['Backup Service'] = backup_data.pop('backup_service')
            backup_data['Metadata'] = backup_data.pop('backup_url')

        return zip(*sorted(six.iteritems(backup_data)))


class ImportBackupRecord(command.ShowOne):
    _description = _('Import volume backup details. Exported backup details '
                     'contain the metadata necessary to restore to a new or '
                     'rebuilt service instance')

    def get_parser(self, prog_name):
        parser = super(ImportBackupRecord, self).get_parser(prog_name)
        parser.add_argument(
            "backup_service",
            metavar="<backup_service>",
            help=_("Backup service containing the backup.")
        )
        parser.add_argument(
            "backup_metadata",
            metavar="<backup_metadata>",
            help=_("Encoded backup metadata from export.")
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        backup_data = volume_client.backups.import_record(
            parsed_args.backup_service,
            parsed_args.backup_metadata)
        backup_data.pop('links', None)
        return zip(*sorted(six.iteritems(backup_data)))
