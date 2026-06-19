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

"""Volume v2 consistency group action implementations"""

import argparse
import logging
from collections.abc import Iterable, Sequence
from typing import Any

from openstack.block_storage import v2 as block_storage_v2
from openstack.block_storage.v2 import consistency_group as _consistency_group
from openstack import utils as sdk_utils
from osc_lib.cli import format_columns
from osc_lib import exceptions
from osc_lib import utils

from openstackclient import command
from openstackclient.i18n import _


LOG = logging.getLogger(__name__)


def _find_volumes(
    parsed_args_volumes: list[str], volume_client: block_storage_v2.Proxy
) -> tuple[int, str]:
    result = 0
    uuid = ''
    for volume in parsed_args_volumes:
        try:
            volume_id = volume_client.find_volume(
                volume, ignore_missing=False
            ).id
            uuid += volume_id + ','
        except Exception as e:
            result += 1
            LOG.error(
                _("Failed to find volume with name or ID '%(volume)s':%(e)s"),
                {'volume': volume, 'e': e},
            )

    return result, uuid


def _format_consistency_group(
    consistency_group: _consistency_group.ConsistencyGroup,
) -> tuple[Sequence[str], Iterable[Any]]:
    columns = (
        'availability_zone',
        'created_at',
        'description',
        'id',
        'name',
        'status',
        'volume_types',
    )
    return columns, utils.get_item_properties(consistency_group, columns)


class AddVolumeToConsistencyGroup(command.Command):
    _description = _("Add volume(s) to consistency group")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'consistency_group',
            metavar="<consistency-group>",
            help=_('Consistency group to contain <volume> (name or ID)'),
        )
        parser.add_argument(
            'volumes',
            metavar='<volume>',
            nargs='+',
            help=_(
                'Volume(s) to add to <consistency-group> (name or ID) '
                '(repeat option to add multiple volumes)'
            ),
        )
        return parser

    def take_action(self, parsed_args: argparse.Namespace) -> None:
        volume_client = sdk_utils.ensure_service_version(
            self.app.client_manager.sdk_connection.volume, '2'
        )
        result, add_uuid = _find_volumes(parsed_args.volumes, volume_client)

        if result > 0:
            total = len(parsed_args.volumes)
            LOG.error(
                _("%(result)s of %(total)s volumes failed to add."),
                {'result': result, 'total': total},
            )

        if add_uuid:
            add_uuid = add_uuid.rstrip(',')
            consistency_group = volume_client.find_consistency_group(
                parsed_args.consistency_group, ignore_missing=False
            )
            volume_client.update_consistency_group(
                consistency_group, add_volumes=add_uuid
            )


class CreateConsistencyGroup(command.ShowOne):
    _description = _("Create new consistency group.")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "name",
            metavar="<name>",
            nargs="?",
            help=_("Name of new consistency group (default to None)"),
        )
        exclusive_group = parser.add_mutually_exclusive_group(required=True)
        exclusive_group.add_argument(
            "--volume-type",
            metavar="<volume-type>",
            help=_("Volume type of this consistency group (name or ID)"),
        )
        exclusive_group.add_argument(
            "--source",
            metavar="<consistency-group>",
            help=_("Existing consistency group (name or ID)"),
        )
        # NOTE(stephenfin): Legacy alias
        exclusive_group.add_argument(
            "--consistency-group-source",
            metavar="<consistency-group>",
            dest='source',
            help=argparse.SUPPRESS,
        )
        exclusive_group.add_argument(
            "--snapshot",
            metavar="<consistency-group-snapshot>",
            help=_("Existing consistency group snapshot (name or ID)"),
        )
        # NOTE(stephenfin): Legacy alias
        exclusive_group.add_argument(
            "--consistency-group-snapshot",
            metavar="<consistency-group-snapshot>",
            dest='snapshot',
            help=argparse.SUPPRESS,
        )
        parser.add_argument(
            "--description",
            metavar="<description>",
            help=_("Description of this consistency group"),
        )
        parser.add_argument(
            "--availability-zone",
            metavar="<availability-zone>",
            help=_(
                "Availability zone for this consistency group "
                "(not available if creating consistency group "
                "from source)"
            ),
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[Any]]:
        volume_client = sdk_utils.ensure_service_version(
            self.app.client_manager.sdk_connection.volume, '2'
        )
        if parsed_args.volume_type:
            volume_type_id = volume_client.find_type(
                parsed_args.volume_type, ignore_missing=False
            ).id
            consistency_group = volume_client.create_consistency_group(
                volume_types=volume_type_id,
                name=parsed_args.name,
                description=parsed_args.description,
                availability_zone=parsed_args.availability_zone,
            )
        else:
            if parsed_args.availability_zone:
                msg = _(
                    "'--availability-zone' option will not work "
                    "if creating consistency group from source"
                )
                LOG.warning(msg)

            consistency_group_id = None
            consistency_group_snapshot_id = None
            if parsed_args.source:
                consistency_group_id = volume_client.find_consistency_group(
                    parsed_args.source, ignore_missing=False
                ).id
            elif parsed_args.snapshot:
                consistency_group_snapshot_id = (
                    volume_client.find_consistency_group_snapshot(
                        parsed_args.snapshot, ignore_missing=False
                    ).id
                )

            consistency_group = (
                volume_client.create_consistency_group_from_source(
                    consistency_group_snapshot=consistency_group_snapshot_id,
                    consistency_group=consistency_group_id,
                    name=parsed_args.name,
                    description=parsed_args.description,
                )
            )

        return _format_consistency_group(consistency_group)


class DeleteConsistencyGroup(command.Command):
    _description = _("Delete consistency group(s).")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'consistency_groups',
            metavar='<consistency-group>',
            nargs="+",
            help=_('Consistency group(s) to delete (name or ID)'),
        )
        parser.add_argument(
            '--force',
            action='store_true',
            default=False,
            help=_("Allow delete in state other than error or available"),
        )
        return parser

    def take_action(self, parsed_args: argparse.Namespace) -> None:
        volume_client = sdk_utils.ensure_service_version(
            self.app.client_manager.sdk_connection.volume, '2'
        )
        result = 0

        for i in parsed_args.consistency_groups:
            try:
                consistency_group = volume_client.find_consistency_group(
                    i, ignore_missing=False
                )
                volume_client.delete_consistency_group(
                    consistency_group, force=parsed_args.force
                )
            except Exception as e:
                result += 1
                LOG.error(
                    _(
                        "Failed to delete consistency group with "
                        "name or ID '%(consistency_group)s':%(e)s"
                    ),
                    {'consistency_group': i, 'e': e},
                )

        if result > 0:
            total = len(parsed_args.consistency_groups)
            msg = _(
                "%(result)s of %(total)s consistency groups failed to delete."
            ) % {'result': result, 'total': total}
            raise exceptions.CommandError(msg)


class ListConsistencyGroup(command.Lister):
    _description = _("List consistency groups.")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--all-projects',
            action="store_true",
            help=_(
                'Show details for all projects. Admin only. '
                '(defaults to False)'
            ),
        )
        parser.add_argument(
            '--long',
            action="store_true",
            help=_('List additional fields in output'),
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[tuple[Any, ...]]]:
        volume_client = sdk_utils.ensure_service_version(
            self.app.client_manager.sdk_connection.volume, '2'
        )

        if parsed_args.long:
            column_headers = [
                'ID',
                'Status',
                'Availability Zone',
                'Name',
                'Description',
                'Volume Types',
            ]
            columns = [
                'id',
                'status',
                'availability_zone',
                'name',
                'description',
                'volume_types',
            ]
        else:
            column_headers = ['ID', 'Status', 'Name']
            columns = ['id', 'status', 'name']

        consistency_groups = volume_client.consistency_groups(
            all_tenants=parsed_args.all_projects,
        )

        return (
            column_headers,
            (
                utils.get_item_properties(
                    s,
                    columns,
                    formatters={'volume_types': format_columns.ListColumn},
                )
                for s in consistency_groups
            ),
        )


class RemoveVolumeFromConsistencyGroup(command.Command):
    _description = _("Remove volume(s) from consistency group")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'consistency_group',
            metavar="<consistency-group>",
            help=_('Consistency group containing <volume> (name or ID)'),
        )
        parser.add_argument(
            'volumes',
            metavar='<volume>',
            nargs='+',
            help=_(
                'Volume(s) to remove from <consistency-group> (name or ID) '
                '(repeat option to remove multiple volumes)'
            ),
        )
        return parser

    def take_action(self, parsed_args: argparse.Namespace) -> None:
        volume_client = sdk_utils.ensure_service_version(
            self.app.client_manager.sdk_connection.volume, '2'
        )
        result, remove_uuid = _find_volumes(parsed_args.volumes, volume_client)

        if result > 0:
            total = len(parsed_args.volumes)
            LOG.error(
                _("%(result)s of %(total)s volumes failed to remove."),
                {'result': result, 'total': total},
            )

        if remove_uuid:
            remove_uuid = remove_uuid.rstrip(',')
            consistency_group = volume_client.find_consistency_group(
                parsed_args.consistency_group, ignore_missing=False
            )
            volume_client.update_consistency_group(
                consistency_group, remove_volumes=remove_uuid
            )


class SetConsistencyGroup(command.Command):
    _description = _("Set consistency group properties")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'consistency_group',
            metavar='<consistency-group>',
            help=_('Consistency group to modify (name or ID)'),
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('New consistency group name'),
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('New consistency group description'),
        )
        return parser

    def take_action(self, parsed_args: argparse.Namespace) -> None:
        volume_client = sdk_utils.ensure_service_version(
            self.app.client_manager.sdk_connection.volume, '2'
        )
        kwargs = {}
        if parsed_args.name:
            kwargs['name'] = parsed_args.name
        if parsed_args.description:
            kwargs['description'] = parsed_args.description
        if kwargs:
            consistency_group = volume_client.find_consistency_group(
                parsed_args.consistency_group, ignore_missing=False
            )
            volume_client.update_consistency_group(consistency_group, **kwargs)


class ShowConsistencyGroup(command.ShowOne):
    _description = _("Display consistency group details.")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "consistency_group",
            metavar="<consistency-group>",
            help=_("Consistency group to display (name or ID)"),
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[Any]]:
        volume_client = sdk_utils.ensure_service_version(
            self.app.client_manager.sdk_connection.volume, '2'
        )
        consistency_group = volume_client.find_consistency_group(
            parsed_args.consistency_group, ignore_missing=False
        )
        return _format_consistency_group(consistency_group)
