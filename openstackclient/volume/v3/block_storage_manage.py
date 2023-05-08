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

"""Block Storage Volume/Snapshot Management implementations"""

from cinderclient import api_versions
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils
from oslo_utils import strutils

from openstackclient.i18n import _


SORT_MANAGEABLE_KEY_VALUES = ('size', 'reference')


class BlockStorageManageVolumes(command.Lister):
    """List manageable volumes.

    Supported by --os-volume-api-version 3.8 or greater.
    """

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        host_group = parser.add_mutually_exclusive_group()
        host_group.add_argument(
            "host",
            metavar="<host>",
            nargs='?',
            help=_(
                'Cinder host on which to list manageable volumes. '
                'Takes the form: host@backend-name#pool'
            ),
        )
        host_group.add_argument(
            "--cluster",
            metavar="<cluster>",
            help=_(
                'Cinder cluster on which to list manageable volumes. '
                'Takes the form: cluster@backend-name#pool. '
                '(supported by --os-volume-api-version 3.17 or later)'
            ),
        )
        parser.add_argument(
            '--detailed',
            metavar='<detailed>',
            default=True,
            help=_('Returns detailed information (Default=True).'),
        )
        parser.add_argument(
            '--marker',
            metavar='<marker>',
            default=None,
            help=_(
                'Begin returning volumes that appear later in the volume '
                'list than that represented by this reference. This '
                'reference should be json like. Default=None.'
            ),
        )
        parser.add_argument(
            '--limit',
            metavar='<limit>',
            default=None,
            help=_('Maximum number of volumes to return. Default=None.'),
        )
        parser.add_argument(
            '--offset',
            metavar='<offset>',
            default=None,
            help=_('Number of volumes to skip after marker. Default=None.'),
        )
        parser.add_argument(
            '--sort',
            metavar='<key>[:<direction>]',
            default=None,
            help=(
                _(
                    'Comma-separated list of sort keys and directions in the '
                    'form of <key>[:<asc|desc>]. '
                    'Valid keys: %s. '
                    'Default=None.'
                )
                % ', '.join(SORT_MANAGEABLE_KEY_VALUES)
            ),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume

        if parsed_args.host is None and parsed_args.cluster is None:
            msg = _(
                "Either <host> or '--cluster <cluster>' needs to be provided "
                "to run the 'block storage volume manageable list' command"
            )
            raise exceptions.CommandError(msg)

        if volume_client.api_version < api_versions.APIVersion('3.8'):
            msg = _(
                "--os-volume-api-version 3.8 or greater is required to "
                "support the 'block storage volume manageable list' command"
            )
            raise exceptions.CommandError(msg)

        if parsed_args.cluster:
            if volume_client.api_version < api_versions.APIVersion('3.17'):
                msg = _(
                    "--os-volume-api-version 3.17 or greater is required to "
                    "support the '--cluster' option"
                )
                raise exceptions.CommandError(msg)

        detailed = strutils.bool_from_string(parsed_args.detailed)
        cluster = getattr(parsed_args, 'cluster', None)

        columns = [
            'reference',
            'size',
            'safe_to_manage',
        ]
        if detailed:
            columns.extend(
                [
                    'reason_not_safe',
                    'cinder_id',
                    'extra_info',
                ]
            )

        data = volume_client.volumes.list_manageable(
            host=parsed_args.host,
            detailed=detailed,
            marker=parsed_args.marker,
            limit=parsed_args.limit,
            offset=parsed_args.offset,
            sort=parsed_args.sort,
            cluster=cluster,
        )

        return (
            columns,
            (
                utils.get_item_properties(
                    s,
                    columns,
                )
                for s in data
            ),
        )


class BlockStorageManageSnapshots(command.Lister):
    """List manageable snapshots.

    Supported by --os-volume-api-version 3.8 or greater.
    """

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        host_group = parser.add_mutually_exclusive_group()
        host_group.add_argument(
            "host",
            metavar="<host>",
            nargs='?',
            help=_(
                'Cinder host on which to list manageable snapshots. '
                'Takes the form: host@backend-name#pool'
            ),
        )
        host_group.add_argument(
            "--cluster",
            metavar="<cluster>",
            help=_(
                'Cinder cluster on which to list manageable snapshots. '
                'Takes the form: cluster@backend-name#pool. '
                '(supported by --os-volume-api-version 3.17 or later)'
            ),
        )
        parser.add_argument(
            '--detailed',
            metavar='<detailed>',
            default=True,
            help=_('Returns detailed information (Default=True).'),
        )
        parser.add_argument(
            '--marker',
            metavar='<marker>',
            default=None,
            help=_(
                'Begin returning snapshots that appear later in the '
                'snapshot list than that represented by this reference. '
                'This reference should be json like. Default=None.'
            ),
        )
        parser.add_argument(
            '--limit',
            metavar='<limit>',
            default=None,
            help=_('Maximum number of snapshots to return. Default=None.'),
        )
        parser.add_argument(
            '--offset',
            metavar='<offset>',
            default=None,
            help=_('Number of snapshots to skip after marker. Default=None.'),
        )
        parser.add_argument(
            '--sort',
            metavar='<key>[:<direction>]',
            default=None,
            help=(
                _(
                    'Comma-separated list of sort keys and directions in the '
                    'form of <key>[:<asc|desc>]. '
                    'Valid keys: %s. '
                    'Default=None.'
                )
                % ', '.join(SORT_MANAGEABLE_KEY_VALUES)
            ),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume

        if parsed_args.host is None and parsed_args.cluster is None:
            msg = _(
                "Either <host> or '--cluster <cluster>' needs to be provided "
                "to run the 'block storage volume snapshot manageable list' "
                "command"
            )
            raise exceptions.CommandError(msg)

        if volume_client.api_version < api_versions.APIVersion('3.8'):
            msg = _(
                "--os-volume-api-version 3.8 or greater is required to "
                "support the 'block storage volume snapshot manageable list' "
                "command"
            )
            raise exceptions.CommandError(msg)

        if parsed_args.cluster:
            if volume_client.api_version < api_versions.APIVersion('3.17'):
                msg = _(
                    "--os-volume-api-version 3.17 or greater is required to "
                    "support the '--cluster' option"
                )
                raise exceptions.CommandError(msg)

        detailed = strutils.bool_from_string(parsed_args.detailed)
        cluster = getattr(parsed_args, 'cluster', None)

        columns = [
            'reference',
            'size',
            'safe_to_manage',
            'source_reference',
        ]
        if detailed:
            columns.extend(
                [
                    'reason_not_safe',
                    'cinder_id',
                    'extra_info',
                ]
            )

        data = volume_client.volume_snapshots.list_manageable(
            host=parsed_args.host,
            detailed=detailed,
            marker=parsed_args.marker,
            limit=parsed_args.limit,
            offset=parsed_args.offset,
            sort=parsed_args.sort,
            cluster=cluster,
        )

        return (
            columns,
            (
                utils.get_item_properties(
                    s,
                    columns,
                )
                for s in data
            ),
        )
