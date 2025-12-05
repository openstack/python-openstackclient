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

import argparse
import logging
from collections.abc import Iterable, Sequence
from typing import Any

from manilaclient import api_versions
from osc_lib.cli import parseractions
from osc_lib import exceptions
from osc_lib import utils as osc_utils

from openstackclient import command
from openstackclient.i18n import _
from openstackclient.identity import common as identity_common

LOG = logging.getLogger(__name__)


class CreateShareGroup(command.ShowOne):
    """Create new share group."""

    _description = _("Create new share group")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--name',
            metavar="<name>",
            default=None,
            help=_('Share group name'),
        )
        parser.add_argument(
            "--description",
            metavar="<description>",
            default=None,
            help=_("Share group description."),
        )
        parser.add_argument(
            "--share-types",
            metavar="<share-types>",
            nargs="+",
            default=[],
            help=_("Name or ID of share type(s)."),
        )
        parser.add_argument(
            "--share-group-type",
            metavar="<share-group-type>",
            default=None,
            help=_(
                "Share group type name or ID of the share group to be created."
            ),
        )
        parser.add_argument(
            "--share-network",
            metavar="<share-network>",
            default=False,
            help=_("Specify share network name or id"),
        )
        parser.add_argument(
            "--source-share-group-snapshot",
            metavar="<source-share-group-snapshot>",
            default=False,
            help=_(
                "Share group snapshot name or ID to create "
                "the share group from."
            ),
        )
        parser.add_argument(
            "--availability-zone",
            metavar='<availability-zone>',
            default=None,
            help=_(
                "Optional availability zone in which group should be created"
            ),
        )
        parser.add_argument(
            "--wait",
            action='store_true',
            default=False,
            help=_('Wait for share group creation'),
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[tuple[str, ...], tuple[Any, ...]]:
        share_client = self.app.client_manager.share

        share_types = []
        for share_type in parsed_args.share_types:
            share_types.append(
                osc_utils.find_resource(
                    share_client.share_types,
                    share_type,
                )
            )
        share_group_type = None
        if parsed_args.share_group_type:
            share_group_type = osc_utils.find_resource(
                share_client.share_group_types, parsed_args.share_group_type
            ).id

        share_network = None
        if parsed_args.share_network:
            share_network = osc_utils.find_resource(
                share_client.share_networks, parsed_args.share_network
            ).id

        source_share_group_snapshot = None
        if parsed_args.source_share_group_snapshot:
            source_share_group_snapshot = osc_utils.find_resource(
                share_client.share_group_snapshots,
                parsed_args.source_share_group_snapshot,
            ).id

        body = {
            'name': parsed_args.name,
            'description': parsed_args.description,
            'share_types': share_types,
            'share_group_type': share_group_type,
            'share_network': share_network,
            'source_share_group_snapshot': source_share_group_snapshot,
            'availability_zone': parsed_args.availability_zone,
        }

        share_group = share_client.share_groups.create(**body)

        if parsed_args.wait:
            if not osc_utils.wait_for_status(
                status_f=share_client.share_groups.get,
                res_id=share_group.id,
                success_status=['available'],
            ):
                LOG.error(_("ERROR: Share group is in error state."))

            share_group = osc_utils.find_resource(
                share_client.share_groups, share_group.id
            )

        printable_share_group = share_group._info
        printable_share_group.pop('links', None)

        if printable_share_group.get('share_types'):
            if parsed_args.formatter == 'table':
                printable_share_group['share_types'] = "\n".join(
                    printable_share_group['share_types']
                )

        return self.dict2columns(printable_share_group)


class DeleteShareGroup(command.Command):
    """Delete one or more share groups."""

    _description = _("Delete one or more share groups")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "share_group",
            metavar="<share_group>",
            nargs="+",
            help=_("Name or ID of the share group(s) to delete"),
        )
        parser.add_argument(
            "--force",
            action='store_true',
            default=False,
            help=_(
                "Attempt to force delete the share group (Default=False) "
                "(Admin only)."
            ),
        )
        parser.add_argument(
            "--wait",
            action='store_true',
            default=False,
            help=_("Wait for share group to delete"),
        )
        return parser

    def take_action(self, parsed_args: argparse.Namespace) -> None:
        share_client = self.app.client_manager.share
        result = 0

        for share_group in parsed_args.share_group:
            try:
                share_group_obj = osc_utils.find_resource(
                    share_client.share_groups, share_group
                )

                share_client.share_groups.delete(
                    share_group_obj, force=parsed_args.force
                )

                if parsed_args.wait:
                    if not osc_utils.wait_for_delete(
                        manager=share_client.share_groups,
                        res_id=share_group_obj.id,
                    ):
                        result += 1

            except Exception as e:
                result += 1
                LOG.error(
                    _(
                        "Failed to delete share group with "
                        "name or ID '%(share_group)s': %(e)s"
                    ),
                    {'share_group': share_group, 'e': e},
                )

        if result > 0:
            total = len(parsed_args.share_group)
            msg = _(
                "%(result)s of %(total)s share groups failed to delete."
            ) % {'result': result, 'total': total}
            raise exceptions.CommandError(msg)


class ListShareGroup(command.Lister):
    """List share groups."""

    _description = _("List share groups")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "--all-projects",
            action='store_true',
            default=False,
            help=_("Display share groups from all projects (Admin only)."),
        )
        parser.add_argument(
            "--name",
            metavar="<name>",
            default=None,
            help=_("Filter results by name."),
        )
        parser.add_argument(
            "--description",
            metavar="<description>",
            default=None,
            help=_(
                "Filter results by description. Available "
                "only for microversion >= 2.36."
            ),
        )
        parser.add_argument(
            "--status",
            metavar="<status>",
            default=None,
            help=_("Filter results by status."),
        )
        parser.add_argument(
            "--share-server",
            metavar="<share-server-id>",
            default=None,
            help=_("Filter results by share server ID."),
        )
        parser.add_argument(
            "--share-group-type",
            metavar="<share-group-type>",
            default=None,
            help=_(
                "Filter results by a share group type ID "
                "or name that was used for share group "
                "creation. "
            ),
        )
        parser.add_argument(
            "--snapshot",
            metavar="<snapshot>",
            default=None,
            help=_(
                "Filter results by share group snapshot "
                "name or ID that was used to create the "
                "share group. "
            ),
        )
        parser.add_argument(
            "--host",
            metavar="<host>",
            default=None,
            help=_("Filter results by host."),
        )
        parser.add_argument(
            "--share-network",
            metavar="<share-network>",
            default=None,
            help=_("Filter results by share-network name or ID. "),
        )
        parser.add_argument(
            "--project",
            metavar="<project>",
            default=None,
            help=_(
                "Filter results by project name or ID. Useful with "
                "set key '--all-projects'. "
            ),
        )
        identity_common.add_project_domain_option_to_parser(parser)
        parser.add_argument(
            "--limit",
            metavar="<limit>",
            type=int,
            default=None,
            action=parseractions.NonNegativeAction,
            help=_("Limit the number of share groups returned"),
        )
        parser.add_argument(
            "--marker",
            metavar="<marker>",
            help=_("The last share group ID of the previous page"),
        )
        parser.add_argument(
            '--sort',
            metavar="<key>[:<direction>]",
            default='name:asc',
            help=_(
                "Sort output by selected keys and directions(asc or desc) "
                "(default: name:asc), multiple keys and directions can be "
                "specified separated by comma"
            ),
        )
        parser.add_argument(
            "--name~",
            metavar="<name~>",
            default=None,
            help=_(
                "Filter results matching a share group "
                "name pattern. Available only for "
                "microversion >= 2.36. "
            ),
        )
        parser.add_argument(
            "--description~",
            metavar="<description~>",
            default=None,
            help=_(
                "Filter results matching a share group "
                "description pattern. Available only for "
                "microversion >= 2.36. "
            ),
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[tuple[Any, ...]]]:
        share_client = self.app.client_manager.share
        identity_client = self.app.client_manager.identity

        share_server_id = None
        if parsed_args.share_server:
            share_server_id = osc_utils.find_resource(
                share_client.share_servers, parsed_args.share_server
            ).id

        share_group_type = None
        if parsed_args.share_group_type:
            share_group_type = osc_utils.find_resource(
                share_client.share_group_types, parsed_args.share_group_type
            ).id

        snapshot = None
        if parsed_args.snapshot:
            snapshot = osc_utils.find_resource(
                share_client.share_snapshots, parsed_args.snapshot
            ).id

        share_network = None
        if parsed_args.share_network:
            share_network = osc_utils.find_resource(
                share_client.share_networks, parsed_args.share_network
            ).id

        project_id = None
        if parsed_args.project:
            project_id = identity_common.find_project(
                identity_client,
                parsed_args.project,
                parsed_args.project_domain,
            ).id

        columns = [
            'ID',
            'Name',
            'Status',
            'Description',
        ]

        search_opts = {
            'all_tenants': parsed_args.all_projects,
            'name': parsed_args.name,
            'status': parsed_args.status,
            'share_server_id': share_server_id,
            'share_group_type': share_group_type,
            'snapshot': snapshot,
            'host': parsed_args.host,
            'share_network': share_network,
            'project_id': project_id,
            'limit': parsed_args.limit,
            'offset': parsed_args.marker,
        }

        if share_client.api_version >= api_versions.APIVersion("2.36"):
            search_opts['name~'] = getattr(parsed_args, 'name~')
            search_opts['description~'] = getattr(parsed_args, 'description~')
            search_opts['description'] = parsed_args.description
        elif (
            parsed_args.description
            or getattr(parsed_args, 'name~')
            or getattr(parsed_args, 'description~')
        ):
            raise exceptions.CommandError(
                "Pattern based filtering (name~, description~ and description)"
                " is only available with manila API version >= 2.36"
            )

        if parsed_args.all_projects:
            columns.append('Project ID')
        share_groups = share_client.share_groups.list(search_opts=search_opts)

        data = (
            osc_utils.get_dict_properties(share_group._info, columns)
            for share_group in share_groups
        )

        return (columns, data)


class ShowShareGroup(command.ShowOne):
    """Show share group."""

    _description = _("Show details about a share group")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "share_group",
            metavar="<share-group>",
            help=_("Name or ID of the share group."),
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[tuple[str, ...], tuple[Any, ...]]:
        share_client = self.app.client_manager.share

        share_group = osc_utils.find_resource(
            share_client.share_groups, parsed_args.share_group
        )

        printable_share_group = share_group._info
        printable_share_group.pop('links', None)

        if printable_share_group.get('share_types'):
            if parsed_args.formatter == 'table':
                printable_share_group['share_types'] = "\n".join(
                    printable_share_group['share_types']
                )

        return self.dict2columns(printable_share_group)


class SetShareGroup(command.Command):
    """Set share group."""

    _description = _("Explicitly set share group status")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'share_group',
            metavar="<share-group>",
            help=_('Name or ID of the share group to update.'),
        )
        parser.add_argument(
            '--name',
            metavar="<name>",
            default=None,
            help=_('New name for the share group. (Default=None)'),
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            default=None,
            help=_('Share group description. (Default=None)'),
        )
        parser.add_argument(
            '--status',
            metavar='<status>',
            default=None,
            help=_(
                'Explicitly update the status of a share group (Admin  '
                'only). Examples include: available, error, creating, '
                'deleting, error_deleting.'
            ),
        )
        return parser

    def take_action(self, parsed_args: argparse.Namespace) -> None:
        share_client = self.app.client_manager.share
        result = 0

        share_group = osc_utils.find_resource(
            share_client.share_groups, parsed_args.share_group
        )

        kwargs = {}
        if parsed_args.name is not None:
            kwargs['name'] = parsed_args.name
        if parsed_args.description is not None:
            kwargs['description'] = parsed_args.description
        if kwargs:
            try:
                share_client.share_groups.update(share_group.id, **kwargs)
            except Exception as e:
                LOG.error(
                    _("Failed to update share group name or description: %s"),
                    e,
                )
                result += 1
        if parsed_args.status:
            try:
                share_group.reset_state(parsed_args.status)
            except Exception as e:
                LOG.error(_("Failed to set status for the share group: %s"), e)
                result += 1

        if result > 0:
            raise exceptions.CommandError(
                _("One or more of the set operations failed")
            )


class UnsetShareGroup(command.Command):
    """Unset a share group property."""

    _description = _("Unset a share group property")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'share_group',
            metavar="<share-group>",
            help=_("Name or ID of the share group to set a property for."),
        )
        parser.add_argument(
            "--name",
            action='store_true',
            help=_("Unset share group name."),
        )
        parser.add_argument(
            "--description",
            action='store_true',
            help=_("Unset share group description."),
        )
        return parser

    def take_action(self, parsed_args: argparse.Namespace) -> None:
        share_client = self.app.client_manager.share

        share_group = osc_utils.find_resource(
            share_client.share_groups, parsed_args.share_group
        )

        kwargs: dict[str, None] = {}
        if parsed_args.name:
            kwargs['name'] = None
        if parsed_args.description:
            kwargs['description'] = None
        if kwargs:
            try:
                share_client.share_groups.update(share_group, **kwargs)
            except Exception as e:
                msg = _(
                    "Failed to unset share_group name or description: %(e)s"
                )
                raise exceptions.CommandError(msg % {'e': e})
