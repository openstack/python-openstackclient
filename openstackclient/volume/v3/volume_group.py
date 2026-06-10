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

import argparse
from collections.abc import Iterable, Sequence
from typing import Any

from openstack.block_storage.v3 import group as _group
from openstack import utils as sdk_utils
from osc_lib import exceptions
from osc_lib import utils

from openstackclient import command
from openstackclient.common import envvars
from openstackclient.i18n import _


def _format_group(group: _group.Group) -> tuple[Sequence[str], Iterable[Any]]:
    columns = (
        'id',
        'status',
        'name',
        'description',
        'group_type',
        'volume_types',
        'availability_zone',
        'created_at',
        'volumes',
        'group_snapshot_id',
        'source_group_id',
    )
    column_headers = (
        'ID',
        'Status',
        'Name',
        'Description',
        'Group Type',
        'Volume Types',
        'Availability Zone',
        'Created At',
        'Volumes',
        'Group Snapshot ID',
        'Source Group ID',
    )

    # TODO(stephenfin): Consider using a formatter for volume_types since it's
    # a list
    return (
        column_headers,
        utils.get_item_properties(
            group,
            columns,
        ),
    )


class CreateVolumeGroup(command.ShowOne):
    """Create a volume group.

    Generic volume groups enable you to create a group of volumes and manage
    them together.

    Generic volume groups are more flexible than consistency groups. Currently
    volume consistency groups only support consistent group snapshot. It
    cannot be extended easily to serve other purposes. A project may want to
    put volumes used in the same application together in a group so that it is
    easier to manage them together, and this group of volumes may or may not
    support consistent group snapshot. Generic volume group solve this problem.
    By decoupling the tight relationship between the group construct and the
    consistency concept, generic volume groups can be extended to support other
    features in the future.

    This command requires ``--os-volume-api-version`` 3.13 or greater.
    """

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        # This is a bit complicated. We accept two patterns: a legacy pattern
        #
        #   volume group create \
        #     <volume-group-type> <volume-type> [<volume-type>...]
        #
        # and the modern approach
        #
        #   volume group create \
        #     --volume-group-type <volume-group-type>
        #     --volume-type <volume-type>
        #    [--volume-type <volume-type> ...]
        #
        # Because argparse doesn't properly support nested exclusive groups, we
        # use two groups: one to ensure users don't pass <volume-group-type> as
        # both a positional and an option argument and another to ensure users
        # don't pass <volume-type> this way. It's a bit weird but it catches
        # everything we care about.
        source_parser = parser.add_mutually_exclusive_group()
        # we use a different name purely so we can issue a deprecation warning
        source_parser.add_argument(
            'volume_group_type_legacy',
            metavar='<volume_group_type>',
            nargs='?',
            help=argparse.SUPPRESS,
        )
        volume_types_parser = parser.add_mutually_exclusive_group()
        # We need to use a separate dest
        # https://github.com/python/cpython/issues/101990
        volume_types_parser.add_argument(
            'volume_types_legacy',
            metavar='<volume_type>',
            nargs='*',
            default=[],
            help=argparse.SUPPRESS,
        )
        source_parser.add_argument(
            '--volume-group-type',
            metavar='<volume_group_type>',
            help=_('Volume group type to use (name or ID)'),
        )
        volume_types_parser.add_argument(
            '--volume-type',
            metavar='<volume_type>',
            dest='volume_types',
            action='append',
            default=[],
            help=_(
                'Volume type(s) to use (name or ID) '
                '(required with --volume-group-type)'
            ),
        )
        source_parser.add_argument(
            '--source-group',
            metavar='<source-group>',
            help=_(
                'Existing volume group to use (name or ID) '
                '(supported by --os-volume-api-version 3.14 or later)'
            ),
        )
        source_parser.add_argument(
            '--group-snapshot',
            metavar='<group-snapshot>',
            help=_(
                'Existing group snapshot to use (name or ID) '
                '(supported by --os-volume-api-version 3.14 or later)'
            ),
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('Name of the volume group.'),
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('Description of a volume group.'),
        )
        parser.add_argument(
            '--availability-zone',
            metavar='<availability-zone>',
            help=_(
                'Availability zone for volume group. '
                '(not available if creating group from source)'
            ),
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[Any]]:
        volume_client = sdk_utils.ensure_service_version(
            self.app.client_manager.sdk_connection.volume, '3'
        )

        if parsed_args.volume_group_type_legacy:
            msg = _(
                "Passing volume group type and volume types as positional "
                "arguments is deprecated. Use the --volume-group-type and "
                "--volume-type option arguments instead."
            )
            self.log.warning(msg)

        volume_group_type = (
            parsed_args.volume_group_type
            or parsed_args.volume_group_type_legacy
        )
        volume_types = parsed_args.volume_types[:]
        volume_types.extend(parsed_args.volume_types_legacy)

        if volume_group_type:
            if not sdk_utils.supports_microversion(volume_client, '3.13'):
                msg = _(
                    "--os-volume-api-version 3.13 or greater is required to "
                    "support the 'volume group create' command"
                )
                raise exceptions.CommandError(msg)
            if not volume_types:
                msg = _(
                    "--volume-types is a required argument when creating a "
                    "group from group type."
                )
                raise exceptions.CommandError(msg)

            volume_group_type_id = volume_client.find_group_type(
                volume_group_type, ignore_missing=False
            ).id
            volume_types_ids = [
                volume_client.find_type(vt, ignore_missing=False).id
                for vt in volume_types
            ]

            group = volume_client.create_group(
                group_type=volume_group_type_id,
                volume_types=volume_types_ids,
                name=parsed_args.name,
                description=parsed_args.description,
                availability_zone=parsed_args.availability_zone,
            )

            group = volume_client.get_group(group.id)
            return _format_group(group)

        else:
            if not sdk_utils.supports_microversion(volume_client, '3.14'):
                msg = _(
                    "--os-volume-api-version 3.14 or greater is required to "
                    "support the 'volume group create "
                    "[--source-group|--group-snapshot]' command"
                )
                raise exceptions.CommandError(msg)
            if (
                parsed_args.source_group is None
                and parsed_args.group_snapshot is None
            ):
                msg = _(
                    "Either --source-group <source_group> or "
                    "'--group-snapshot <group_snapshot>' needs to be "
                    "provided to run the 'volume group create "
                    "[--source-group|--group-snapshot]' command"
                )
                raise exceptions.CommandError(msg)
            if parsed_args.availability_zone:
                msg = _(
                    "'--availability-zone' option will not work "
                    "if creating group from source."
                )
                self.log.warning(msg)

            source_group_id = None
            if parsed_args.source_group:
                source_group_id = volume_client.find_group(
                    parsed_args.source_group, ignore_missing=False
                ).id
            group_snapshot_id = None
            if parsed_args.group_snapshot:
                group_snapshot_id = volume_client.find_group_snapshot(
                    parsed_args.group_snapshot, ignore_missing=False
                ).id

            group = volume_client.create_group_from_source(
                group_snapshot_id=group_snapshot_id,
                source_group_id=source_group_id,
                name=parsed_args.name,
                description=parsed_args.description,
            )
            group = volume_client.get_group(group.id)
            return _format_group(group)


class DeleteVolumeGroup(command.Command):
    """Delete a volume group.

    This command requires ``--os-volume-api-version`` 3.13 or greater.
    """

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'group',
            metavar='<group>',
            help=_('Name or ID of volume group to delete'),
        )
        parser.add_argument(
            '--force',
            action='store_true',
            default=False,
            help=_(
                'Delete the volume group even if it contains volumes. '
                'This will delete any remaining volumes in the group.'
            ),
        )
        return parser

    def take_action(self, parsed_args: argparse.Namespace) -> None:
        volume_client = sdk_utils.ensure_service_version(
            self.app.client_manager.sdk_connection.volume, '3'
        )

        if not sdk_utils.supports_microversion(volume_client, '3.13'):
            msg = _(
                "--os-volume-api-version 3.13 or greater is required to "
                "support the 'volume group delete' command"
            )
            raise exceptions.CommandError(msg)

        group = volume_client.find_group(
            parsed_args.group,
            ignore_missing=False,
        )

        volume_client.delete_group(group, delete_volumes=parsed_args.force)


class SetVolumeGroup(command.ShowOne):
    """Update a volume group.

    This command requires ``--os-volume-api-version`` 3.13 or greater.
    """

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'group',
            metavar='<group>',
            help=_('Name or ID of volume group.'),
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('New name for group.'),
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('New description for group.'),
        )
        type_group = parser.add_mutually_exclusive_group()
        type_group.add_argument(
            '--enable-replication',
            action='store_true',
            dest='enable_replication',
            default=None,
            help=_(
                'Enable replication for group. '
                '(supported by --os-volume-api-version 3.38 or above)'
            ),
        )
        type_group.add_argument(
            '--disable-replication',
            action='store_false',
            dest='enable_replication',
            help=_(
                'Disable replication for group. '
                '(supported by --os-volume-api-version 3.38 or above)'
            ),
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[Any]]:
        volume_client = sdk_utils.ensure_service_version(
            self.app.client_manager.sdk_connection.volume, '3'
        )

        if not sdk_utils.supports_microversion(volume_client, '3.13'):
            msg = _(
                "--os-volume-api-version 3.13 or greater is required to "
                "support the 'volume group set' command"
            )
            raise exceptions.CommandError(msg)

        group = volume_client.find_group(
            parsed_args.group,
            ignore_missing=False,
        )

        if parsed_args.enable_replication is not None:
            if not sdk_utils.supports_microversion(volume_client, '3.38'):
                msg = _(
                    "--os-volume-api-version 3.38 or greater is required to "
                    "support the '--enable-replication' or "
                    "'--disable-replication' options"
                )
                raise exceptions.CommandError(msg)

            if parsed_args.enable_replication:
                volume_client.enable_group_replication(group)
            else:
                volume_client.disable_group_replication(group)

        kwargs = {}

        if parsed_args.name is not None:
            kwargs['name'] = parsed_args.name

        if parsed_args.description is not None:
            kwargs['description'] = parsed_args.description

        if kwargs:
            group = volume_client.update_group(group, **kwargs)

        return _format_group(group)


class ListVolumeGroup(command.Lister):
    """Lists all volume groups.

    This command requires ``--os-volume-api-version`` 3.13 or greater.
    """

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--all-projects',
            dest='all_projects',
            action='store_true',
            default=envvars.boolenv('ALL_PROJECTS'),
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

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[tuple[str, ...], Iterable[tuple[Any, ...]]]:
        volume_client = sdk_utils.ensure_service_version(
            self.app.client_manager.sdk_connection.volume, '3'
        )

        if not sdk_utils.supports_microversion(volume_client, '3.13'):
            msg = _(
                "--os-volume-api-version 3.13 or greater is required to "
                "support the 'volume group list' command"
            )
            raise exceptions.CommandError(msg)

        groups = list(
            volume_client.groups(all_projects=parsed_args.all_projects)
        )

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


class ShowVolumeGroup(command.ShowOne):
    """Show detailed information for a volume group.

    This command requires ``--os-volume-api-version`` 3.13 or greater.
    """

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'group',
            metavar='<group>',
            help=_('Name or ID of volume group.'),
        )
        parser.add_argument(
            '--volumes',
            action='store_true',
            dest='show_volumes',
            default=None,
            help=_(
                'Show volumes included in the group. '
                '(supported by --os-volume-api-version 3.25 or above)'
            ),
        )
        parser.add_argument(
            '--no-volumes',
            action='store_false',
            dest='show_volumes',
            help=_(
                'Do not show volumes included in the group. '
                '(supported by --os-volume-api-version 3.25 or above)'
            ),
        )
        parser.add_argument(
            '--replication-targets',
            action='store_true',
            dest='show_replication_targets',
            default=None,
            help=_(
                'Show replication targets for the group. '
                '(supported by --os-volume-api-version 3.38 or above)'
            ),
        )
        parser.add_argument(
            '--no-replication-targets',
            action='store_false',
            dest='show_replication_targets',
            help=_(
                'Do not show replication targets for the group. '
                '(supported by --os-volume-api-version 3.38 or above)'
            ),
        )

        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[Any]]:
        volume_client = sdk_utils.ensure_service_version(
            self.app.client_manager.sdk_connection.volume, '3'
        )

        if not sdk_utils.supports_microversion(volume_client, '3.13'):
            msg = _(
                "--os-volume-api-version 3.13 or greater is required to "
                "support the 'volume group show' command"
            )
            raise exceptions.CommandError(msg)

        if parsed_args.show_volumes is not None:
            if not sdk_utils.supports_microversion(volume_client, '3.25'):
                msg = _(
                    "--os-volume-api-version 3.25 or greater is required to "
                    "support the '--(no-)volumes' option"
                )
                raise exceptions.CommandError(msg)

        if parsed_args.show_replication_targets is not None:
            if not sdk_utils.supports_microversion(volume_client, '3.38'):
                msg = _(
                    "--os-volume-api-version 3.38 or greater is required to "
                    "support the '--(no-)replication-targets' option"
                )
                raise exceptions.CommandError(msg)

        group = volume_client.find_group(
            parsed_args.group,
            ignore_missing=False,
        )

        if parsed_args.show_volumes is not None:
            group = volume_client.get_group(
                group.id, list_volume=parsed_args.show_volumes
            )

        # TODO(stephenfin): Show replication targets
        return _format_group(group)


class FailoverVolumeGroup(command.Command):
    """Failover replication for a volume group.

    This command requires ``--os-volume-api-version`` 3.38 or greater.
    """

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'group',
            metavar='<group>',
            help=_('Name or ID of volume group to failover replication for.'),
        )
        parser.add_argument(
            '--allow-attached-volume',
            action='store_true',
            dest='allow_attached_volume',
            default=False,
            help=_('Allow group with attached volumes to be failed over.'),
        )
        parser.add_argument(
            '--disallow-attached-volume',
            action='store_false',
            dest='allow_attached_volume',
            default=False,
            help=_('Disallow group with attached volumes to be failed over.'),
        )
        parser.add_argument(
            '--secondary-backend-id',
            metavar='<backend_id>',
            help=_('Secondary backend ID.'),
        )
        return parser

    def take_action(self, parsed_args: argparse.Namespace) -> None:
        volume_client = sdk_utils.ensure_service_version(
            self.app.client_manager.sdk_connection.volume, '3'
        )

        if not sdk_utils.supports_microversion(volume_client, '3.38'):
            msg = _(
                "--os-volume-api-version 3.38 or greater is required to "
                "support the 'volume group failover' command"
            )
            raise exceptions.CommandError(msg)

        group = volume_client.find_group(
            parsed_args.group,
            ignore_missing=False,
        )

        volume_client.failover_group_replication(
            group,
            allowed_attached_volume=parsed_args.allow_attached_volume,
            secondary_backend_id=parsed_args.secondary_backend_id,
        )
