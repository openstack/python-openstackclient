# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from cinderclient import api_versions
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _


def _format_cluster(cluster, detailed=False):
    columns: tuple[str, ...] = (
        'name',
        'binary',
        'state',
        'status',
    )
    column_headers: tuple[str, ...] = (
        'Name',
        'Binary',
        'State',
        'Status',
    )

    if detailed:
        columns += (
            'disabled_reason',
            'num_hosts',
            'num_down_hosts',
            'last_heartbeat',
            'created_at',
            'updated_at',
            # optional columns, depending on whether replication is enabled
            'replication_status',
            'frozen',
            'active_backend_id',
        )
        column_headers += (
            'Disabled Reason',
            'Hosts',
            'Down Hosts',
            'Last Heartbeat',
            'Created At',
            'Updated At',
            # optional columns, depending on whether replication is enabled
            'Replication Status',
            'Frozen',
            'Active Backend ID',
        )

    return (
        column_headers,
        utils.get_item_properties(
            cluster,
            columns,
        ),
    )


class ListBlockStorageCluster(command.Lister):
    """List block storage clusters.

    This command requires ``--os-volume-api-version`` 3.7 or greater.
    """

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--cluster',
            metavar='<name>',
            default=None,
            help=_(
                'Filter by cluster name, without backend will list '
                'all clustered services from the same cluster.'
            ),
        )
        parser.add_argument(
            '--binary',
            metavar='<binary>',
            help=_('Cluster binary.'),
        )
        parser.add_argument(
            '--up',
            action='store_true',
            dest='is_up',
            default=None,
            help=_('Filter by up status.'),
        )
        parser.add_argument(
            '--down',
            action='store_false',
            dest='is_up',
            help=_('Filter by down status.'),
        )
        parser.add_argument(
            '--disabled',
            action='store_true',
            dest='is_disabled',
            default=None,
            help=_('Filter by disabled status.'),
        )
        parser.add_argument(
            '--enabled',
            action='store_false',
            dest='is_disabled',
            help=_('Filter by enabled status.'),
        )
        parser.add_argument(
            '--num-hosts',
            metavar='<hosts>',
            type=int,
            default=None,
            help=_('Filter by number of hosts in the cluster.'),
        )
        parser.add_argument(
            '--num-down-hosts',
            metavar='<hosts>',
            type=int,
            default=None,
            help=_('Filter by number of hosts that are down.'),
        )
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_("List additional fields in output"),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume

        if volume_client.api_version < api_versions.APIVersion('3.7'):
            msg = _(
                "--os-volume-api-version 3.7 or greater is required to "
                "support the 'block storage cluster list' command"
            )
            raise exceptions.CommandError(msg)

        columns: tuple[str, ...] = ('Name', 'Binary', 'State', 'Status')
        if parsed_args.long:
            columns += (
                'Num Hosts',
                'Num Down Hosts',
                'Last Heartbeat',
                'Disabled Reason',
                'Created At',
                'Updated At',
            )

        data = volume_client.clusters.list(
            name=parsed_args.cluster,
            binary=parsed_args.binary,
            is_up=parsed_args.is_up,
            disabled=parsed_args.is_disabled,
            num_hosts=parsed_args.num_hosts,
            num_down_hosts=parsed_args.num_down_hosts,
            detailed=parsed_args.long,
        )

        return (
            columns,
            (utils.get_item_properties(s, columns) for s in data),
        )


class SetBlockStorageCluster(command.Command):
    """Set block storage cluster properties.

    This command requires ``--os-volume-api-version`` 3.7 or greater.
    """

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'cluster',
            metavar='<cluster>',
            help=_('Name of block storage cluster to update (name only)'),
        )
        parser.add_argument(
            '--binary',
            metavar='<binary>',
            default='cinder-volume',
            help=_(
                "Name of binary to filter by; defaults to 'cinder-volume' "
                "(optional)"
            ),
        )
        enabled_group = parser.add_mutually_exclusive_group()
        enabled_group.add_argument(
            '--enable',
            action='store_false',
            dest='disabled',
            default=None,
            help=_('Enable cluster'),
        )
        enabled_group.add_argument(
            '--disable',
            action='store_true',
            dest='disabled',
            help=_('Disable cluster'),
        )
        parser.add_argument(
            '--disable-reason',
            metavar='<reason>',
            dest='disabled_reason',
            help=_(
                'Reason for disabling the cluster '
                '(should be used with --disable option)'
            ),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume

        if volume_client.api_version < api_versions.APIVersion('3.7'):
            msg = _(
                "--os-volume-api-version 3.7 or greater is required to "
                "support the 'block storage cluster set' command"
            )
            raise exceptions.CommandError(msg)

        if parsed_args.disabled_reason and not parsed_args.disabled:
            msg = _("Cannot specify --disable-reason without --disable")
            raise exceptions.CommandError(msg)

        cluster = volume_client.clusters.update(
            parsed_args.cluster,
            parsed_args.binary,
            disabled=parsed_args.disabled,
            disabled_reason=parsed_args.disabled_reason,
        )

        return _format_cluster(cluster, detailed=True)


class ShowBlockStorageCluster(command.ShowOne):
    """Show detailed information for a block storage cluster.

    This command requires ``--os-volume-api-version`` 3.7 or greater.
    """

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'cluster',
            metavar='<cluster>',
            help=_('Name of block storage cluster.'),
        )
        parser.add_argument(
            '--binary',
            metavar='<binary>',
            help=_('Service binary.'),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume

        if volume_client.api_version < api_versions.APIVersion('3.7'):
            msg = _(
                "--os-volume-api-version 3.7 or greater is required to "
                "support the 'block storage cluster show' command"
            )
            raise exceptions.CommandError(msg)

        cluster = volume_client.clusters.show(
            parsed_args.cluster,
            binary=parsed_args.binary,
        )

        return _format_cluster(cluster, detailed=True)
