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

"""Volume v3 snapshot action implementations"""

import logging

from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _

LOG = logging.getLogger(__name__)


class DeleteVolumeSnapshot(command.Command):
    _description = _("Delete volume snapshot(s)")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "snapshots",
            metavar="<snapshot>",
            nargs="+",
            help=_("Snapshot(s) to delete (name or ID)"),
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help=_(
                "Attempt forced removal of snapshot(s), "
                "regardless of state (defaults to False)"
            ),
        )
        parser.add_argument(
            '--remote',
            action='store_true',
            help=_(
                'Unmanage the snapshot, removing it from the Block Storage '
                'service management but not from the backend.'
            ),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        volume_client_sdk = self.app.client_manager.sdk_connection.volume

        result = 0

        if parsed_args.remote:
            if parsed_args.force:
                msg = _(
                    "The --force option is not supported with the "
                    "--remote parameter."
                )
                raise exceptions.CommandError(msg)

        for i in parsed_args.snapshots:
            try:
                snapshot_id = utils.find_resource(
                    volume_client.volume_snapshots, i
                ).id
                if parsed_args.remote:
                    volume_client_sdk.unmanage_snapshot(snapshot_id)
                else:
                    volume_client.volume_snapshots.delete(
                        snapshot_id, parsed_args.force
                    )
            except Exception as e:
                result += 1
                LOG.error(
                    _(
                        "Failed to delete snapshot with "
                        "name or ID '%(snapshot)s': %(e)s"
                    )
                    % {'snapshot': i, 'e': e}
                )

        if result > 0:
            total = len(parsed_args.snapshots)
            msg = _("%(result)s of %(total)s snapshots failed to delete.") % {
                'result': result,
                'total': total,
            }
            raise exceptions.CommandError(msg)
