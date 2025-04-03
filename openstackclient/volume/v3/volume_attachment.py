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

import logging

from openstack import utils as sdk_utils
from osc_lib.cli import format_columns
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.common import envvars
from openstackclient.common import pagination
from openstackclient.i18n import _
from openstackclient.identity import common as identity_common

LOG = logging.getLogger(__name__)

_FILTER_DEPRECATED = _(
    "This option is deprecated. Consider using the '--filters' option which "
    "was introduced in microversion 3.33 instead."
)


def _format_attachment(attachment):
    columns = (
        'id',
        'volume_id',
        'instance',
        'status',
        'attach_mode',
        'attached_at',
        'detached_at',
        'connection_info',
    )
    column_headers = (
        'ID',
        'Volume ID',
        'Instance ID',
        'Status',
        'Attach Mode',
        'Attached At',
        'Detached At',
        'Properties',
    )

    # VolumeAttachmentManager.create returns a dict while everything else
    # returns a VolumeAttachment object
    if isinstance(attachment, dict):
        data = []
        for column in columns:
            if column == 'connection_info':
                data.append(format_columns.DictColumn(attachment[column]))
                continue
            data.append(attachment[column])
    else:
        data = utils.get_item_properties(
            attachment,
            columns,
            formatters={
                'connection_info': format_columns.DictColumn,
            },
        )

    # TODO(stephenfin): Improve output with the nested connection_info
    # field - cinderclient printed two things but that's equally ugly
    return (column_headers, data)


class CreateVolumeAttachment(command.ShowOne):
    """Create an attachment for a volume.

    This command will only create a volume attachment in the Volume service. It
    will not invoke the necessary Compute service actions to actually attach
    the volume to the server at the hypervisor level. As a result, it should
    typically only be used for troubleshooting issues with an existing server
    in combination with other tooling. For all other use cases, the 'server
    add volume' command should be preferred.
    """

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'volume',
            metavar='<volume>',
            help=_('Name or ID of volume to attach to server.'),
        )
        parser.add_argument(
            'server',
            metavar='<server>',
            help=_('Name or ID of server to attach volume to.'),
        )
        parser.add_argument(
            '--connect',
            action='store_true',
            dest='connect',
            default=False,
            help=_('Make an active connection using provided connector info'),
        )
        parser.add_argument(
            '--no-connect',
            action='store_false',
            dest='connect',
            help=_(
                'Do not make an active connection using provided connector '
                'info'
            ),
        )
        parser.add_argument(
            '--initiator',
            metavar='<initiator>',
            help=_('IQN of the initiator attaching to'),
        )
        parser.add_argument(
            '--ip',
            metavar='<ip>',
            help=_('IP of the system attaching to'),
        )
        parser.add_argument(
            '--host',
            metavar='<host>',
            help=_('Name of the host attaching to'),
        )
        parser.add_argument(
            '--platform',
            metavar='<platform>',
            help=_('Platform type'),
        )
        parser.add_argument(
            '--os-type',
            metavar='<ostype>',
            help=_('OS type'),
        )
        parser.add_argument(
            '--multipath',
            action='store_true',
            dest='multipath',
            default=False,
            help=_('Use multipath'),
        )
        parser.add_argument(
            '--no-multipath',
            action='store_false',
            dest='multipath',
            help=_('Use multipath'),
        )
        parser.add_argument(
            '--mountpoint',
            metavar='<mountpoint>',
            help=_('Mountpoint volume will be attached at'),
        )
        parser.add_argument(
            '--mode',
            metavar='<mode>',
            help=_(
                'Mode of volume attachment, rw, ro and null, where null '
                'indicates we want to honor any existing admin-metadata '
                'settings '
                '(supported by --os-volume-api-version 3.54 or later)'
            ),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.sdk_connection.volume
        compute_client = self.app.client_manager.compute

        if not sdk_utils.supports_microversion(volume_client, '3.27'):
            msg = _(
                "--os-volume-api-version 3.27 or greater is required to "
                "support the 'volume attachment create' command"
            )
            raise exceptions.CommandError(msg)

        if parsed_args.mode:
            if not sdk_utils.supports_microversion(volume_client, '3.54'):
                msg = _(
                    "--os-volume-api-version 3.54 or greater is required to "
                    "support the '--mode' option"
                )
                raise exceptions.CommandError(msg)

        connector = {}
        if parsed_args.connect:
            connector = {
                'initiator': parsed_args.initiator,
                'ip': parsed_args.ip,
                'platform': parsed_args.platform,
                'host': parsed_args.host,
                'os_type': parsed_args.os_type,
                'multipath': parsed_args.multipath,
                'mountpoint': parsed_args.mountpoint,
            }
        else:
            if any(
                {
                    parsed_args.initiator,
                    parsed_args.ip,
                    parsed_args.platform,
                    parsed_args.host,
                    parsed_args.host,
                    parsed_args.multipath,
                    parsed_args.mountpoint,
                }
            ):
                msg = _(
                    'You must specify the --connect option for any of the '
                    'connection-specific options such as --initiator to be '
                    'valid'
                )
                raise exceptions.CommandError(msg)

        volume = volume_client.find_volume(
            parsed_args.volume, ignore_missing=False
        )
        server = compute_client.find_server(
            parsed_args.server, ignore_missing=False
        )

        attachment = volume_client.create_attachment(
            volume.id,
            connector=connector,
            instance=server.id,
            mode=parsed_args.mode,
        )

        return _format_attachment(attachment)


class DeleteVolumeAttachment(command.Command):
    """Delete an attachment for a volume.

    Similarly to the 'volume attachment create' command, this command will only
    delete the volume attachment record in the Volume service. It will not
    invoke the necessary Compute service actions to actually attach the volume
    to the server at the hypervisor level. As a result, it should typically
    only be used for troubleshooting issues with an existing server in
    combination with other tooling. For all other use cases, the 'server volume
    remove' command should be preferred.
    """

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'attachment',
            metavar='<attachment>',
            help=_('ID of volume attachment to delete'),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.sdk_connection.volume

        if not sdk_utils.supports_microversion(volume_client, '3.27'):
            msg = _(
                "--os-volume-api-version 3.27 or greater is required to "
                "support the 'volume attachment delete' command"
            )
            raise exceptions.CommandError(msg)

        volume_client.delete_attachment(parsed_args.attachment)


class SetVolumeAttachment(command.ShowOne):
    """Update an attachment for a volume.

    This call is designed to be more of an volume attachment completion than
    anything else. It expects the value of a connector object to notify the
    driver that the volume is going to be connected and where it's being
    connected to.
    """

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'attachment',
            metavar='<attachment>',
            help=_('ID of volume attachment.'),
        )
        parser.add_argument(
            '--initiator',
            metavar='<initiator>',
            help=_('IQN of the initiator attaching to'),
        )
        parser.add_argument(
            '--ip',
            metavar='<ip>',
            help=_('IP of the system attaching to'),
        )
        parser.add_argument(
            '--host',
            metavar='<host>',
            help=_('Name of the host attaching to'),
        )
        parser.add_argument(
            '--platform',
            metavar='<platform>',
            help=_('Platform type'),
        )
        parser.add_argument(
            '--os-type',
            metavar='<ostype>',
            help=_('OS type'),
        )
        parser.add_argument(
            '--multipath',
            action='store_true',
            dest='multipath',
            default=False,
            help=_('Use multipath'),
        )
        parser.add_argument(
            '--no-multipath',
            action='store_false',
            dest='multipath',
            help=_('Use multipath'),
        )
        parser.add_argument(
            '--mountpoint',
            metavar='<mountpoint>',
            help=_('Mountpoint volume will be attached at'),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.sdk_connection.volume

        if not sdk_utils.supports_microversion(volume_client, '3.27'):
            msg = _(
                "--os-volume-api-version 3.27 or greater is required to "
                "support the 'volume attachment set' command"
            )
            raise exceptions.CommandError(msg)

        connector = {
            'initiator': parsed_args.initiator,
            'ip': parsed_args.ip,
            'platform': parsed_args.platform,
            'host': parsed_args.host,
            'os_type': parsed_args.os_type,
            'multipath': parsed_args.multipath,
            'mountpoint': parsed_args.mountpoint,
        }

        attachment = volume_client.update_attachment(
            parsed_args.attachment,
            connector=connector,
        )

        return _format_attachment(attachment)


class CompleteVolumeAttachment(command.Command):
    """Complete an attachment for a volume."""

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'attachment',
            metavar='<attachment>',
            help=_('ID of volume attachment to mark as completed'),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.sdk_connection.volume

        if not sdk_utils.supports_microversion(volume_client, '3.44'):
            msg = _(
                "--os-volume-api-version 3.44 or greater is required to "
                "support the 'volume attachment complete' command"
            )
            raise exceptions.CommandError(msg)

        volume_client.complete_attachment(parsed_args.attachment)


class ListVolumeAttachment(command.Lister):
    """Lists all volume attachments."""

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--project',
            dest='project',
            metavar='<project>',
            help=_('Filter results by project (name or ID) (admin only)'),
        )
        identity_common.add_project_domain_option_to_parser(parser)
        parser.add_argument(
            '--all-projects',
            dest='all_projects',
            action='store_true',
            default=envvars.boolenv('ALL_PROJECTS'),
            help=_('Shows details for all projects (admin only).'),
        )
        parser.add_argument(
            '--volume-id',
            metavar='<volume-id>',
            default=None,
            help=_('Filters results by a volume ID. ') + _FILTER_DEPRECATED,
        )
        parser.add_argument(
            '--status',
            metavar='<status>',
            help=_('Filters results by a status. ') + _FILTER_DEPRECATED,
        )
        pagination.add_marker_pagination_option_to_parser(parser)
        # TODO(stephenfin): Add once we have an equivalent command for
        # 'cinder list-filters'
        # parser.add_argument(
        #     '--filter',
        #     metavar='<key=value>',
        #     action=parseractions.KeyValueAction,
        #     dest='filters',
        #     help=_(
        #         "Filter key and value pairs. Use 'foo' to "
        #         "check enabled filters from server. Use 'key~=value' for "
        #         "inexact filtering if the key supports "
        #         "(supported by --os-volume-api-version 3.33 or above)"
        #     ),
        # )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.sdk_connection.volume
        identity_client = self.app.client_manager.identity

        if not sdk_utils.supports_microversion(volume_client, '3.27'):
            msg = _(
                "--os-volume-api-version 3.27 or greater is required to "
                "support the 'volume attachment list' command"
            )
            raise exceptions.CommandError(msg)

        project_id = None
        if parsed_args.project:
            project_id = identity_common.find_project(
                identity_client,
                parsed_args.project,
                parsed_args.project_domain,
            ).id

        search_opts = {
            'all_tenants': True if project_id else parsed_args.all_projects,
            'project_id': project_id,
            'status': parsed_args.status,
            'volume_id': parsed_args.volume_id,
        }
        # Update search option with `filters`
        # if AppendFilters.filters:
        #     search_opts.update(shell_utils.extract_filters(AppendFilters.filters))

        # TODO(stephenfin): Implement sorting
        attachments = volume_client.attachments(
            search_opts=search_opts,
            marker=parsed_args.marker,
            limit=parsed_args.limit,
        )

        column_headers = (
            'ID',
            'Volume ID',
            'Server ID',
            'Status',
        )
        columns = (
            'id',
            'volume_id',
            'instance',
            'status',
        )

        return (
            column_headers,
            (utils.get_item_properties(a, columns) for a in attachments),
        )


class ShowVolumeAttachment(command.ShowOne):
    """Show detailed information for a volume attachment."""

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'attachment',
            metavar='<attachment>',
            help=_('ID of volume attachment.'),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.sdk_connection.volume

        if not sdk_utils.supports_microversion(volume_client, '3.27'):
            msg = _(
                "--os-volume-api-version 3.27 or greater is required to "
                "support the 'volume attachment show' command"
            )
            raise exceptions.CommandError(msg)

        attachment = volume_client.get_attachment(parsed_args.attachment)

        return _format_attachment(attachment)
