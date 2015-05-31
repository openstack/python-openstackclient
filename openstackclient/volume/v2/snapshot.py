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

"""Volume v2 snapshot action implementations"""

import logging

from cliff import command
from cliff import show
import six

from openstackclient.common import utils


class DeleteSnapshot(command.Command):
    """Delete volume snapshot(s)"""

    log = logging.getLogger(__name__ + ".DeleteSnapshot")

    def get_parser(self, prog_name):
        parser = super(DeleteSnapshot, self).get_parser(prog_name)
        parser.add_argument(
            "snapshots",
            metavar="<snapshot>",
            nargs="+",
            help="Snapsho(s) to delete (name or ID)"
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action: (%s)", parsed_args)
        volume_client = self.app.client_manager.volume
        for snapshot in parsed_args.snapshots:
            snapshot_id = utils.find_resource(
                volume_client.volume_snapshots, snapshot).id
            volume_client.volume_snapshots.delete(snapshot_id)
        return


class ShowSnapshot(show.ShowOne):
    """Display snapshot details"""

    log = logging.getLogger(__name__ + ".ShowSnapshot")

    def get_parser(self, prog_name):
        parser = super(ShowSnapshot, self).get_parser(prog_name)
        parser.add_argument(
            "snapshot",
            metavar="<snapshot>",
            help="Snapshot to display (name or ID)"
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action: (%s)", parsed_args)
        volume_client = self.app.client_manager.volume
        snapshot = utils.find_resource(
            volume_client.volume_snapshots, parsed_args.snapshot)
        snapshot = volume_client.volume_snapshots.get(snapshot.id)
        return zip(*sorted(six.iteritems(snapshot._info)))
