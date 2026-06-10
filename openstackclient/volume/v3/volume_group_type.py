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
import logging
from typing import Any

from openstack.block_storage.v3 import group_type as _group_type
from openstack import utils as sdk_utils
from osc_lib.cli import format_columns
from osc_lib.cli import parseractions
from osc_lib import exceptions
from osc_lib import utils

from openstackclient import command
from openstackclient.i18n import _

LOG = logging.getLogger(__name__)


def _format_group_type(
    group_type: _group_type.GroupType,
) -> tuple[Sequence[str], Iterable[Any]]:
    columns = (
        'id',
        'name',
        'description',
        'is_public',
        'group_specs',
    )
    column_headers = (
        'ID',
        'Name',
        'Description',
        'Is Public',
        'Properties',
    )

    return (
        column_headers,
        utils.get_item_properties(
            group_type,
            columns,
            formatters={'group_specs': format_columns.DictColumn},
        ),
    )


class CreateVolumeGroupType(command.ShowOne):
    """Create a volume group type.

    This command requires ``--os-volume-api-version`` 3.11 or greater.
    """

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<name>',
            help=_('Name of new volume group type.'),
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('Description of the volume group type.'),
        )
        type_group = parser.add_mutually_exclusive_group()
        type_group.add_argument(
            '--public',
            dest='is_public',
            action='store_true',
            default=True,
            help=_(
                'Volume group type is available to other projects (default)'
            ),
        )
        type_group.add_argument(
            '--private',
            dest='is_public',
            action='store_false',
            help=_('Volume group type is not available to other projects'),
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[Any]]:
        volume_client = sdk_utils.ensure_service_version(
            self.app.client_manager.sdk_connection.volume, '3'
        )

        if not sdk_utils.supports_microversion(volume_client, '3.11'):
            msg = _(
                "--os-volume-api-version 3.11 or greater is required to "
                "support the 'volume group type create' command"
            )
            raise exceptions.CommandError(msg)

        group_type = volume_client.create_group_type(
            name=parsed_args.name,
            description=parsed_args.description,
            is_public=parsed_args.is_public,
        )

        return _format_group_type(group_type)


class DeleteVolumeGroupType(command.Command):
    """Delete a volume group type.

    This command requires ``--os-volume-api-version`` 3.11 or greater.
    """

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'group_type',
            metavar='<group_type>',
            help=_('Name or ID of volume group type to delete'),
        )
        return parser

    def take_action(self, parsed_args: argparse.Namespace) -> None:
        volume_client = sdk_utils.ensure_service_version(
            self.app.client_manager.sdk_connection.volume, '3'
        )

        if not sdk_utils.supports_microversion(volume_client, '3.11'):
            msg = _(
                "--os-volume-api-version 3.11 or greater is required to "
                "support the 'volume group type delete' command"
            )
            raise exceptions.CommandError(msg)

        group_type = volume_client.find_group_type(
            parsed_args.group_type,
            ignore_missing=False,
        )

        volume_client.delete_group_type(group_type)


class SetVolumeGroupType(command.ShowOne):
    """Update a volume group type.

    This command requires ``--os-volume-api-version`` 3.11 or greater.
    """

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'group_type',
            metavar='<group_type>',
            help=_('Name or ID of volume group type.'),
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('New name for volume group type.'),
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('New description for volume group type.'),
        )
        type_group = parser.add_mutually_exclusive_group()
        type_group.add_argument(
            '--public',
            dest='is_public',
            action='store_true',
            default=None,
            help=_('Make volume group type available to other projects.'),
        )
        type_group.add_argument(
            '--private',
            dest='is_public',
            action='store_false',
            help=_('Make volume group type unavailable to other projects.'),
        )
        parser.add_argument(
            '--no-property',
            action='store_true',
            help=_(
                'Remove all properties from this volume group type '
                '(specify both --no-property and --property '
                'to remove the current properties before setting '
                'new properties)'
            ),
        )
        parser.add_argument(
            '--property',
            metavar='<key=value>',
            action=parseractions.KeyValueAction,
            dest='properties',
            help=_(
                'Property to add or modify for this volume group type '
                '(repeat option to set multiple properties)'
            ),
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[Any]]:
        volume_client = sdk_utils.ensure_service_version(
            self.app.client_manager.sdk_connection.volume, '3'
        )

        if not sdk_utils.supports_microversion(volume_client, '3.11'):
            msg = _(
                "--os-volume-api-version 3.11 or greater is required to "
                "support the 'volume group type set' command"
            )
            raise exceptions.CommandError(msg)

        group_type = volume_client.find_group_type(
            parsed_args.group_type,
            ignore_missing=False,
        )

        kwargs = {}
        errors = 0

        if parsed_args.name is not None:
            kwargs['name'] = parsed_args.name

        if parsed_args.description is not None:
            kwargs['description'] = parsed_args.description

        if parsed_args.is_public is not None:
            kwargs['is_public'] = parsed_args.is_public

        if kwargs:
            try:
                group_type = volume_client.update_group_type(
                    group_type.id, **kwargs
                )
            except Exception as e:
                LOG.error(_("Failed to update group type: %s"), e)
                errors += 1

        if parsed_args.no_property:
            try:
                for key in group_type.group_specs:
                    volume_client.delete_group_type_group_specs_property(
                        group_type.id, key
                    )
            except Exception as e:
                LOG.error(_("Failed to clear group type properties: %s"), e)
                errors += 1

        if parsed_args.properties:
            try:
                volume_client.create_group_type_group_specs(
                    group_type.id, parsed_args.properties
                )
            except Exception as e:
                LOG.error(_("Failed to set group type properties: %s"), e)
                errors += 1

        if errors > 0:
            msg = _("Command Failed: One or more of the operations failed")
            raise exceptions.CommandError(msg)

        group_type = volume_client.find_group_type(
            parsed_args.group_type,
            ignore_missing=False,
        )

        return _format_group_type(group_type)


class UnsetVolumeGroupType(command.ShowOne):
    """Unset properties of a volume group type.

    This command requires ``--os-volume-api-version`` 3.11 or greater.
    """

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'group_type',
            metavar='<group_type>',
            help=_('Name or ID of volume group type.'),
        )
        parser.add_argument(
            '--property',
            metavar='<key>',
            action='append',
            dest='properties',
            help=_(
                'Property to remove from this volume group type '
                '(repeat option to unset multiple properties)'
            ),
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[Any]]:
        volume_client = sdk_utils.ensure_service_version(
            self.app.client_manager.sdk_connection.volume, '3'
        )

        if not sdk_utils.supports_microversion(volume_client, '3.11'):
            msg = _(
                "--os-volume-api-version 3.11 or greater is required to "
                "support the 'volume group type unset' command"
            )
            raise exceptions.CommandError(msg)

        for key in parsed_args.properties or []:
            volume_client.delete_group_type_group_specs_property(
                parsed_args.group_type, key
            )

        group_type = volume_client.find_group_type(
            parsed_args.group_type,
            ignore_missing=False,
        )

        return _format_group_type(group_type)


class ListVolumeGroupType(command.Lister):
    """Lists all volume group types.

    This command requires ``--os-volume-api-version`` 3.11 or greater.
    """

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--default',
            action='store_true',
            dest='show_default',
            default=False,
            help=_('List the default volume group type.'),
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

        if not sdk_utils.supports_microversion(volume_client, '3.11'):
            msg = _(
                "--os-volume-api-version 3.11 or greater is required to "
                "support the 'volume group type list' command"
            )
            raise exceptions.CommandError(msg)

        if parsed_args.show_default:
            group_types = [volume_client.get_group_type('default')]
        else:
            group_types = list(volume_client.group_types())

        column_headers = (
            'ID',
            'Name',
            'Is Public',
            'Group Specs',
        )
        columns = (
            'ID',
            'Name',
            'Is Public',
            'Group Specs',
        )

        return (
            column_headers,
            (
                utils.get_item_properties(
                    a,
                    columns,
                    formatters={'Group Specs': format_columns.DictColumn},
                )
                for a in group_types
            ),
        )


class ShowVolumeGroupType(command.ShowOne):
    """Show detailed information for a volume group type.

    This command requires ``--os-volume-api-version`` 3.11 or greater.
    """

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'group_type',
            metavar='<group_type>',
            help=_('Name or ID of volume group type.'),
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[Any]]:
        volume_client = sdk_utils.ensure_service_version(
            self.app.client_manager.sdk_connection.volume, '3'
        )

        if not sdk_utils.supports_microversion(volume_client, '3.11'):
            msg = _(
                "--os-volume-api-version 3.11 or greater is required to "
                "support the 'volume group type show' command"
            )
            raise exceptions.CommandError(msg)

        group_type = volume_client.find_group_type(
            parsed_args.group_type,
            ignore_missing=False,
        )

        return _format_group_type(group_type)
