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
from collections.abc import Iterable, Sequence
import logging
from typing import Any

from osc_lib.cli import parseractions
from osc_lib import exceptions
from osc_lib import utils as osc_utils

from openstackclient import command
from openstackclient.i18n import _

LOG = logging.getLogger(__name__)


class CreateShareGroupSnapshot(command.ShowOne):
    """Create a share group snapshot."""

    _description = _("Create a share group snapshot of the given share group")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "share_group",
            metavar="<share-group>",
            help=_("Name or ID of the share group."),
        )
        parser.add_argument(
            "--name",
            metavar="<name>",
            default=None,
            help=_("Optional share group snapshot name. (Default=None)"),
        )
        parser.add_argument(
            "--description",
            metavar="<description>",
            default=None,
            help=_(
                "Optional share group snapshot description. (Default=None)"
            ),
        )
        parser.add_argument(
            '--wait',
            action='store_true',
            default=False,
            help=_('Wait for share group snapshot creation'),
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[tuple[str, ...], tuple[Any, ...]]:
        share_client = self.app.client_manager.share

        share_group = osc_utils.find_resource(
            share_client.share_groups, parsed_args.share_group
        )

        share_group_snapshot = share_client.share_group_snapshots.create(
            share_group,
            name=parsed_args.name,
            description=parsed_args.description,
        )
        if parsed_args.wait:
            if not osc_utils.wait_for_status(
                status_f=share_client.share_group_snapshots.get,
                res_id=share_group_snapshot.id,
                success_status=['available'],
            ):
                LOG.error(_("ERROR: Share group snapshot is in error state."))

            share_group_snapshot = osc_utils.find_resource(
                share_client.share_group_snapshots, share_group_snapshot.id
            )

        data = share_group_snapshot._info
        data.pop('links', None)
        data.pop('members', None)

        return self.dict2columns(data)


class DeleteShareGroupSnapshot(command.Command):
    """Delete one or more share group snapshots."""

    _description = _("Delete one or more share group snapshot")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "share_group_snapshot",
            metavar="<share-group-snapshot>",
            nargs="+",
            help=_("Name or ID of the group snapshot(s) to delete"),
        )
        parser.add_argument(
            "--force",
            action='store_true',
            default=False,
            help=_(
                "Attempt to force delete the share group snapshot(s) "
                "(Default=False) (Admin only)."
            ),
        )
        parser.add_argument(
            "--wait",
            action='store_true',
            default=False,
            help=_("Wait for share group snapshot deletion"),
        )
        return parser

    def take_action(self, parsed_args: argparse.Namespace) -> None:
        share_client = self.app.client_manager.share
        result = 0

        for share_group_snapshot in parsed_args.share_group_snapshot:
            try:
                share_group_snapshot_obj = osc_utils.find_resource(
                    share_client.share_group_snapshots, share_group_snapshot
                )

                share_client.share_group_snapshots.delete(
                    share_group_snapshot_obj, force=parsed_args.force
                )

                if parsed_args.wait:
                    if not osc_utils.wait_for_delete(
                        manager=share_client.share_group_snapshots,
                        res_id=share_group_snapshot_obj.id,
                    ):
                        result += 1

            except Exception as e:
                result += 1
                LOG.error(
                    'Failed to delete a share group snapshot with '
                    'name or ID %s: %s',
                    share_group_snapshot,
                    e,
                )

        if result > 0:
            total = len(parsed_args.share_group_snapshot)
            msg = (
                f'{result} of {total} share group snapshots failed to delete.'
            )
            raise exceptions.CommandError(msg)


class ShowShareGroupSnapshot(command.ShowOne):
    """Display a share group snapshot"""

    _description = _("Show details about a share group snapshot")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "share_group_snapshot",
            metavar="<share-group-snapshot>",
            help=_("Name or ID of the share group snapshot to display"),
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[tuple[str, ...], tuple[Any, ...]]:
        share_client = self.app.client_manager.share

        share_group_snapshot = osc_utils.find_resource(
            share_client.share_group_snapshots,
            parsed_args.share_group_snapshot,
        )

        data = share_group_snapshot._info
        data.pop('links', None)
        data.pop('members', None)

        return self.dict2columns(data)


class SetShareGroupSnapshot(command.Command):
    """Set share group snapshot properties."""

    _description = _("Set share group snapshot properties")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "share_group_snapshot",
            metavar="<share-group-snapshot>",
            help=_('Name or ID of the snapshot to set a property for'),
        )
        parser.add_argument(
            "--name",
            metavar="<name>",
            default=None,
            help=_("Set a name to the snapshot."),
        )
        parser.add_argument(
            "--description",
            metavar="<description>",
            default=None,
            help=_("Set a description to the snapshot."),
        )
        parser.add_argument(
            "--status",
            metavar="<status>",
            choices=[
                'available',
                'error',
                'creating',
                'deleting',
                'error_deleting',
            ],
            help=_(
                "Explicitly set the state of a share group snapshot"
                "(Admin only). "
                "Options include : available, error, creating, "
                "deleting, error_deleting."
            ),
        )
        return parser

    def take_action(self, parsed_args: argparse.Namespace) -> None:
        share_client = self.app.client_manager.share
        result = 0

        share_group_snapshot = osc_utils.find_resource(
            share_client.share_group_snapshots,
            parsed_args.share_group_snapshot,
        )

        kwargs = {}

        if parsed_args.name is not None:
            kwargs['name'] = parsed_args.name
        if parsed_args.description is not None:
            kwargs['description'] = parsed_args.description

        if kwargs:
            try:
                share_client.share_group_snapshots.update(
                    share_group_snapshot, **kwargs
                )
            except Exception as e:
                result += 1
                LOG.error(
                    'Failed to set name or description for '
                    'share group snapshot with ID %s: %s',
                    share_group_snapshot.id,
                    e,
                )

        if parsed_args.status:
            try:
                share_client.share_group_snapshots.reset_state(
                    share_group_snapshot, parsed_args.status
                )
            except Exception as e:
                result += 1
                LOG.error(
                    'Failed to set status for share group snapshot with '
                    'ID %s: %s',
                    share_group_snapshot.id,
                    e,
                )

        if result > 0:
            raise exceptions.CommandError(
                _("One or more of the set operations failed")
            )


class UnsetShareGroupSnapshot(command.Command):
    """Unset a share group snapshot property."""

    _description = _("Unset a share group snapshot property")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "share_group_snapshot",
            metavar="<share-group-snapshot>",
            help=_("Name or ID of the group snapshot to unset a property of"),
        )
        parser.add_argument(
            "--name",
            action='store_true',
            help=_("Unset share group snapshot name."),
        )
        parser.add_argument(
            "--description",
            action='store_true',
            help=_("Unset share group snapshot description."),
        )
        return parser

    def take_action(self, parsed_args: argparse.Namespace) -> None:
        share_client = self.app.client_manager.share

        share_group_snapshot = osc_utils.find_resource(
            share_client.share_group_snapshots,
            parsed_args.share_group_snapshot,
        )

        kwargs = {}
        if parsed_args.name:
            # the SDK unsets name if it is an empty string
            kwargs['name'] = ''
        if parsed_args.description:
            # the SDK unsets description if it is an empty string
            kwargs['description'] = ''
        if kwargs:
            try:
                share_client.share_group_snapshots.update(
                    share_group_snapshot, **kwargs
                )
            except Exception as e:
                raise exceptions.CommandError(
                    'Failed to unset name or description for '
                    f'share group snapshot : {e}'
                )


class ListShareGroupSnapshot(command.Lister):
    """List share group snapshots."""

    _description = _("List share group snapshots")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "--all-projects",
            action='store_true',
            default=False,
            help=_("Display information from all projects (Admin only)."),
        )
        parser.add_argument(
            "--name",
            metavar="<name>",
            default=None,
            help=_("Filter results by name."),
        )
        parser.add_argument(
            "--status",
            metavar="<status>",
            default=None,
            help=_("Filter results by status."),
        )
        parser.add_argument(
            "--share-group",
            metavar="<share-group>",
            default=None,
            help=_("Filter results by share group name or ID."),
        )
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
            help=_("The last share group snapshot ID of the previous page"),
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
            "--detailed",
            action="store_true",
            help=_("Show detailed information about share group snapshot. "),
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[tuple[Any, ...]]]:
        share_client = self.app.client_manager.share

        share_group_id = None
        if parsed_args.share_group:
            share_group_id = osc_utils.find_resource(
                share_client.share_groups, parsed_args.share_group
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
            'share_group_id': share_group_id,
            'limit': parsed_args.limit,
            'offset': parsed_args.marker,
        }

        if parsed_args.detailed:
            columns.extend(
                [
                    'Created At',
                    'Share Group ID',
                ]
            )

        if parsed_args.all_projects:
            columns.append('Project ID')

        share_group_snapshots = share_client.share_group_snapshots.list(
            search_opts=search_opts
        )

        share_group_snapshots = osc_utils.sort_items(
            share_group_snapshots, parsed_args.sort, str
        )

        data = (
            osc_utils.get_dict_properties(share_group_snapshot._info, columns)
            for share_group_snapshot in share_group_snapshots
        )

        return (columns, data)


class ListShareGroupSnapshotMembers(command.Lister):
    """List members for share group snapshot."""

    _description = _("List members of share group snapshot")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "share_group_snapshot",
            metavar="<share-group-snapshot>",
            help=_("Name or ID of the group snapshot to list members for"),
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[tuple[Any, ...]]]:
        share_client = self.app.client_manager.share

        columns = ['Share ID', 'Size']

        share_group_snapshot = osc_utils.find_resource(
            share_client.share_group_snapshots,
            parsed_args.share_group_snapshot,
        )

        data = (
            osc_utils.get_dict_properties(member, columns)
            for member in share_group_snapshot._info.get('members', [])
        )

        return (columns, data)
