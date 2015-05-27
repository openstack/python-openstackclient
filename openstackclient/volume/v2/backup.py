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

from cliff import command
from cliff import show
import six

from openstackclient.common import utils


class DeleteBackup(command.Command):
    """Delete backup(s)"""

    log = logging.getLogger(__name__ + ".DeleteBackup")

    def get_parser(self, prog_name):
        parser = super(DeleteBackup, self).get_parser(prog_name)
        parser.add_argument(
            "backups",
            metavar="<backup>",
            nargs="+",
            help="Backup(s) to delete (name or ID)"
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action: (%s)", parsed_args)
        volume_client = self.app.client_manager.volume
        for backup in parsed_args.backups:
            backup_id = utils.find_resource(
                volume_client.backups, backup).id
            volume_client.backups.delete(backup_id)
        return


class ShowBackup(show.ShowOne):
    """Display backup details"""

    log = logging.getLogger(__name__ + ".ShowBackup")

    def get_parser(self, prog_name):
        parser = super(ShowBackup, self).get_parser(prog_name)
        parser.add_argument(
            "backup",
            metavar="<backup>",
            help="Backup to display (name or ID)")
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action: (%s)", parsed_args)
        volume_client = self.app.client_manager.volume
        backup = utils.find_resource(volume_client.backups,
                                     parsed_args.backup)
        backup._info.pop("links", None)
        return zip(*sorted(six.iteritems(backup._info)))
