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

from cinderclient import api_versions
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _

LOG = logging.getLogger(__name__)


def _format_group_snapshot(snapshot):
    columns = (
        'id',
        'status',
        'name',
        'description',
        'group_id',
        'group_type_id',
    )
    column_headers = (
        'ID',
        'Status',
        'Name',
        'Description',
        'Group',
        'Group Type',
    )

    return (
        column_headers,
        utils.get_item_properties(
            snapshot,
            columns,
        ),
    )


class CreateVolumeGroupSnapshot(command.ShowOne):
    """Create a volume group snapshot.

    This command requires ``--os-volume-api-version`` 3.13 or greater.
    """

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'volume_group',
            metavar='<volume_group>',
            help=_('Name or ID of volume group to create a snapshot of.'),
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('Name of the volume group snapshot.'),
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('Description of a volume group snapshot.'),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume

        if volume_client.api_version < api_versions.APIVersion('3.14'):
            msg = _(
                "--os-volume-api-version 3.14 or greater is required to "
                "support the 'volume group snapshot create' command"
            )
            raise exceptions.CommandError(msg)

        volume_group = utils.find_resource(
            volume_client.groups,
            parsed_args.volume_group,
        )

        snapshot = volume_client.group_snapshots.create(
            volume_group.id, parsed_args.name, parsed_args.description
        )

        return _format_group_snapshot(snapshot)


class DeleteVolumeGroupSnapshot(command.Command):
    """Delete a volume group snapshot.

    This command requires ``--os-volume-api-version`` 3.14 or greater.
    """

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'snapshot',
            metavar='<snapshot>',
            help=_('Name or ID of volume group snapshot to delete'),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume

        if volume_client.api_version < api_versions.APIVersion('3.14'):
            msg = _(
                "--os-volume-api-version 3.14 or greater is required to "
                "support the 'volume group snapshot delete' command"
            )
            raise exceptions.CommandError(msg)

        snapshot = utils.find_resource(
            volume_client.group_snapshots,
            parsed_args.snapshot,
        )

        volume_client.group_snapshots.delete(snapshot.id)


class ListVolumeGroupSnapshot(command.Lister):
    """Lists all volume group snapshot.

    This command requires ``--os-volume-api-version`` 3.14 or greater.
    """

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--all-projects',
            dest='all_projects',
            action='store_true',
            default=utils.env('ALL_PROJECTS', default=False),
            help=_('Shows details for all projects (admin only).'),
        )
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
        volume_client = self.app.client_manager.volume

        if volume_client.api_version < api_versions.APIVersion('3.14'):
            msg = _(
                "--os-volume-api-version 3.14 or greater is required to "
                "support the 'volume group snapshot list' command"
            )
            raise exceptions.CommandError(msg)

        search_opts = {
            'all_tenants': parsed_args.all_projects,
        }

        groups = volume_client.group_snapshots.list(search_opts=search_opts)

        column_headers = (
            'ID',
            'Status',
            'Name',
        )
        columns = (
            'id',
            'status',
            'name',
        )

        return (
            column_headers,
            (utils.get_item_properties(a, columns) for a in groups),
        )


class ShowVolumeGroupSnapshot(command.ShowOne):
    """Show detailed information for a volume group snapshot.

    This command requires ``--os-volume-api-version`` 3.14 or greater.
    """

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'snapshot',
            metavar='<snapshot>',
            help=_('Name or ID of volume group snapshot.'),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume

        if volume_client.api_version < api_versions.APIVersion('3.14'):
            msg = _(
                "--os-volume-api-version 3.14 or greater is required to "
                "support the 'volume group snapshot show' command"
            )
            raise exceptions.CommandError(msg)

        snapshot = utils.find_resource(
            volume_client.group_snapshots,
            parsed_args.snapshot,
        )

        # TODO(stephenfin): Do we need this?
        snapshot = volume_client.groups.show(snapshot.id)

        return _format_group_snapshot(snapshot)
