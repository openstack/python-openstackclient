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

"""Volume V3 Volume action implementations"""

import logging

from openstack import utils as sdk_utils
from osc_lib.cli import format_columns
from osc_lib.cli import parseractions
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _
from openstackclient.volume.v2 import volume as volume_v2

LOG = logging.getLogger(__name__)


class VolumeSummary(command.ShowOne):
    _description = _("Show a summary of all volumes in this deployment.")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--all-projects',
            action='store_true',
            default=False,
            help=_('Include all projects (admin only)'),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.sdk_connection.volume

        if not sdk_utils.supports_microversion(volume_client, '3.12'):
            msg = _(
                "--os-volume-api-version 3.12 or greater is required to "
                "support the 'volume summary' command"
            )
            raise exceptions.CommandError(msg)

        columns = [
            'total_count',
            'total_size',
        ]
        column_headers = [
            'Total Count',
            'Total Size',
        ]
        if sdk_utils.supports_microversion(volume_client, '3.36'):
            columns.append('metadata')
            column_headers.append('Metadata')

        # set value of 'all_tenants' when using project option
        all_projects = parsed_args.all_projects

        vol_summary = volume_client.summary(all_projects)

        return (
            column_headers,
            utils.get_item_properties(
                vol_summary,
                columns,
                formatters={'metadata': format_columns.DictColumn},
            ),
        )


class VolumeRevertToSnapshot(command.Command):
    _description = _("Revert a volume to a snapshot.")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'snapshot',
            metavar="<snapshot>",
            help=_(
                'Name or ID of the snapshot to restore. The snapshot must '
                'be the most recent one known to cinder.'
            ),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.sdk_connection.volume

        if not sdk_utils.supports_microversion(volume_client, '3.40'):
            msg = _(
                "--os-volume-api-version 3.40 or greater is required to "
                "support the 'volume revert snapshot' command"
            )
            raise exceptions.CommandError(msg)

        snapshot = volume_client.find_snapshot(
            parsed_args.snapshot,
            ignore_missing=False,
        )
        volume = volume_client.find_volume(
            snapshot.volume_id,
            ignore_missing=False,
        )

        volume_client.revert_volume_to_snapshot(volume, snapshot)


class CreateVolume(volume_v2.CreateVolume):
    _description = _("Create new volume")

    @staticmethod
    def _check_size_arg(args):
        """Check whether --size option is required or not.

        Require size parameter in case if any of the following is not specified:
        * snapshot
        * source volume
        * backup
        * remote source (volume to be managed)
        """

        if (
            args.snapshot or args.source or args.backup or args.remote_source
        ) is None and args.size is None:
            msg = _(
                "--size is a required option if none of --snapshot, "
                "--backup, --source, or --remote-source are provided."
            )
            raise exceptions.CommandError(msg)

    def get_parser(self, prog_name):
        parser, source_group = self._get_parser(prog_name)

        source_group.add_argument(
            "--remote-source",
            metavar="<key=value>",
            action=parseractions.KeyValueAction,
            help=_(
                "The attribute(s) of the existing remote volume "
                "(admin required) (repeat option to specify multiple "
                "attributes) e.g.: '--remote-source source-name=test_name "
                "--remote-source source-id=test_id'"
            ),
        )
        parser.add_argument(
            "--host",
            metavar="<host>",
            help=_(
                "Cinder host on which the existing volume resides; "
                "takes the form: host@backend-name#pool. This is only "
                "used along with the --remote-source option."
            ),
        )
        parser.add_argument(
            "--cluster",
            metavar="<cluster>",
            help=_(
                "Cinder cluster on which the existing volume resides; "
                "takes the form: cluster@backend-name#pool. This is only "
                "used along with the --remote-source option. "
                "(supported by --os-volume-api-version 3.16 or above)",
            ),
        )
        return parser

    def take_action(self, parsed_args):
        CreateVolume._check_size_arg(parsed_args)

        volume_client_sdk = self.app.client_manager.sdk_connection.volume

        if (
            parsed_args.host or parsed_args.cluster
        ) and not parsed_args.remote_source:
            msg = _(
                "The --host and --cluster options are only supported "
                "with --remote-source parameter."
            )
            raise exceptions.CommandError(msg)

        if parsed_args.remote_source:
            if (
                parsed_args.size
                or parsed_args.consistency_group
                or parsed_args.hint
                or parsed_args.read_only
                or parsed_args.read_write
            ):
                msg = _(
                    "The --size, --consistency-group, --hint, --read-only "
                    "and --read-write options are not supported with the "
                    "--remote-source parameter."
                )
                raise exceptions.CommandError(msg)
            if parsed_args.cluster:
                if not sdk_utils.supports_microversion(
                    volume_client_sdk, '3.16'
                ):
                    msg = _(
                        "--os-volume-api-version 3.16 or greater is required "
                        "to support the cluster parameter."
                    )
                    raise exceptions.CommandError(msg)
            if parsed_args.cluster and parsed_args.host:
                msg = _(
                    "Only one of --host or --cluster needs to be specified "
                    "to manage a volume."
                )
                raise exceptions.CommandError(msg)
            if not parsed_args.cluster and not parsed_args.host:
                msg = _(
                    "One of --host or --cluster needs to be specified to "
                    "manage a volume."
                )
                raise exceptions.CommandError(msg)
            volume = volume_client_sdk.manage_volume(
                host=parsed_args.host,
                cluster=parsed_args.cluster,
                ref=parsed_args.remote_source,
                name=parsed_args.name,
                description=parsed_args.description,
                volume_type=parsed_args.type,
                availability_zone=parsed_args.availability_zone,
                metadata=parsed_args.property,
                bootable=parsed_args.bootable,
            )
            return zip(*sorted(volume.items()))

        return self._take_action(parsed_args)


class DeleteVolume(volume_v2.DeleteVolume):
    _description = _("Delete volume(s)")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--remote',
            action='store_true',
            help=_("Specify this parameter to unmanage a volume."),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        volume_client_sdk = self.app.client_manager.sdk_connection.volume
        result = 0

        if parsed_args.remote and (parsed_args.force or parsed_args.purge):
            msg = _(
                "The --force and --purge options are not "
                "supported with the --remote parameter."
            )
            raise exceptions.CommandError(msg)

        for i in parsed_args.volumes:
            try:
                volume_obj = utils.find_resource(volume_client.volumes, i)
                if parsed_args.remote:
                    volume_client_sdk.unmanage_volume(volume_obj.id)
                elif parsed_args.force:
                    volume_client.volumes.force_delete(volume_obj.id)
                else:
                    volume_client.volumes.delete(
                        volume_obj.id, cascade=parsed_args.purge
                    )
            except Exception as e:
                result += 1
                LOG.error(
                    _(
                        "Failed to delete volume with "
                        "name or ID '%(volume)s': %(e)s"
                    ),
                    {'volume': i, 'e': e},
                )

        if result > 0:
            total = len(parsed_args.volumes)
            msg = _("%(result)s of %(total)s volumes failed " "to delete.") % {
                'result': result,
                'total': total,
            }
            raise exceptions.CommandError(msg)
