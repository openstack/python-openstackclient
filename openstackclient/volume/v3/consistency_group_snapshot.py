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

"""Volume v3 consistency group snapshot action implementations"""

import argparse
import logging
from collections.abc import Iterable, Sequence
from typing import Any

from openstack.block_storage.v3 import (
    consistency_group_snapshot as _cg_snapshot,
)
from openstack import utils as sdk_utils
from osc_lib import exceptions
from osc_lib import utils

from openstackclient import command
from openstackclient.i18n import _


LOG = logging.getLogger(__name__)


def _format_consistency_group_snapshot(
    consistency_group_snapshot: _cg_snapshot.ConsistencyGroupSnapshot,
) -> tuple[Sequence[str], Iterable[Any]]:
    columns = (
        'consistencygroup_id',
        'created_at',
        'description',
        'id',
        'name',
        'status',
    )
    return columns, utils.get_item_properties(
        consistency_group_snapshot, columns
    )


class CreateConsistencyGroupSnapshot(command.ShowOne):
    _description = _("Create new consistency group snapshot.")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "snapshot_name",
            metavar="<snapshot-name>",
            nargs="?",
            help=_("Name of new consistency group snapshot (default to None)"),
        )
        parser.add_argument(
            "--consistency-group",
            metavar="<consistency-group>",
            help=_(
                "Consistency group to snapshot (name or ID) "
                "(default to be the same as <snapshot-name>)"
            ),
        )
        parser.add_argument(
            "--description",
            metavar="<description>",
            help=_("Description of this consistency group snapshot"),
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[Any]]:
        volume_client = sdk_utils.ensure_service_version(
            self.app.client_manager.sdk_connection.volume, '3'
        )
        consistency_group = parsed_args.consistency_group
        if not parsed_args.consistency_group:
            # If "--consistency-group" not specified, then consistency_group
            # will be the same as the new consistency group snapshot name
            consistency_group = parsed_args.snapshot_name
        consistency_group_id = volume_client.find_consistency_group(
            consistency_group, ignore_missing=False
        ).id
        consistency_group_snapshot = (
            volume_client.create_consistency_group_snapshot(
                consistencygroup_id=consistency_group_id,
                name=parsed_args.snapshot_name,
                description=parsed_args.description,
            )
        )

        return _format_consistency_group_snapshot(consistency_group_snapshot)


class DeleteConsistencyGroupSnapshot(command.Command):
    _description = _("Delete consistency group snapshot(s).")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "consistency_group_snapshot",
            metavar="<consistency-group-snapshot>",
            nargs="+",
            help=_("Consistency group snapshot(s) to delete (name or ID)"),
        )
        return parser

    def take_action(self, parsed_args: argparse.Namespace) -> None:
        volume_client = sdk_utils.ensure_service_version(
            self.app.client_manager.sdk_connection.volume, '3'
        )
        result = 0

        for snapshot in parsed_args.consistency_group_snapshot:
            try:
                consistency_group_snapshot = (
                    volume_client.find_consistency_group_snapshot(
                        snapshot, ignore_missing=False
                    )
                )
                volume_client.delete_consistency_group_snapshot(
                    consistency_group_snapshot
                )
            except Exception as e:
                result += 1
                LOG.error(
                    _(
                        "Failed to delete consistency group snapshot "
                        "with name or ID '%(snapshot)s': %(e)s"
                    ),
                    {'snapshot': snapshot, 'e': e},
                )

        if result > 0:
            total = len(parsed_args.consistency_group_snapshot)
            msg = _(
                "%(result)s of %(total)s consistency group snapshots "
                "failed to delete."
            ) % {'result': result, 'total': total}
            raise exceptions.CommandError(msg)


class ListConsistencyGroupSnapshot(command.Lister):
    _description = _("List consistency group snapshots.")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--all-projects',
            action="store_true",
            help=_(
                'Show detail for all projects (admin only) (defaults to False)'
            ),
        )
        parser.add_argument(
            '--long',
            action="store_true",
            help=_('List additional fields in output'),
        )
        parser.add_argument(
            '--status',
            metavar="<status>",
            choices=[
                'available',
                'error',
                'creating',
                'deleting',
                'error_deleting',
            ],
            help=_(
                'Filters results by a status ("available", "error", '
                '"creating", "deleting" or "error_deleting")'
            ),
        )
        parser.add_argument(
            '--consistency-group',
            metavar="<consistency-group>",
            help=_('Filters results by a consistency group (name or ID)'),
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[tuple[Any, ...]]]:
        volume_client = sdk_utils.ensure_service_version(
            self.app.client_manager.sdk_connection.volume, '3'
        )

        if parsed_args.long:
            column_headers = [
                'ID',
                'Status',
                'ConsistencyGroup ID',
                'Name',
                'Description',
                'Created At',
            ]
            columns = [
                'id',
                'status',
                'consistencygroup_id',
                'name',
                'description',
                'created_at',
            ]
        else:
            column_headers = ['ID', 'Status', 'Name']
            columns = ['id', 'status', 'name']

        consistency_group_id = None
        if parsed_args.consistency_group:
            consistency_group_id = volume_client.find_consistency_group(
                parsed_args.consistency_group, ignore_missing=False
            ).id

        consistency_group_snapshots = (
            volume_client.consistency_group_snapshots(
                all_tenants=parsed_args.all_projects,
                status=parsed_args.status,
                consistencygroup_id=consistency_group_id,
            )
        )

        return (
            column_headers,
            (
                utils.get_item_properties(s, columns)
                for s in consistency_group_snapshots
            ),
        )


class ShowConsistencyGroupSnapshot(command.ShowOne):
    _description = _("Display consistency group snapshot details")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "consistency_group_snapshot",
            metavar="<consistency-group-snapshot>",
            help=_("Consistency group snapshot to display (name or ID)"),
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[Any]]:
        volume_client = sdk_utils.ensure_service_version(
            self.app.client_manager.sdk_connection.volume, '3'
        )
        consistency_group_snapshot = (
            volume_client.find_consistency_group_snapshot(
                parsed_args.consistency_group_snapshot, ignore_missing=False
            )
        )
        return _format_consistency_group_snapshot(consistency_group_snapshot)
