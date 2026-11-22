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

from openstack import utils as sdk_utils
from osc_lib import exceptions
from osc_lib import utils

from openstackclient import command
from openstackclient.i18n import _


class SetDefaultType(command.ShowOne):
    """Set a project's default volume type override (admin only).

    Overrides the deployment-wide default for the specified project without
    changing Cinder's default_volume_type configuration. Use
    ``volume type list --default`` to see the effective default for the
    current project.

    This command requires ``--os-volume-api-version`` 3.67 or greater.
    """

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'volume_type',
            metavar='<volume_type>',
            help=_('Name or ID of the volume type.'),
        )
        parser.add_argument(
            "project",
            metavar="<project_id>",
            default=None,
            help=_(
                'ID of project to set the default volume type override for.'
            ),
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[Any]]:
        columns = ('project_id', 'volume_type_id')
        column_headers = ('Project ID', 'Volume Type ID')
        volume_client = sdk_utils.ensure_service_version(
            self.app.client_manager.volume, '3'
        )

        if not sdk_utils.supports_microversion(volume_client, '3.67'):
            msg = _(
                "--os-volume-api-version 3.67 or greater is required to "
                "support the 'volume type default set' command"
            )
            raise exceptions.CommandError(msg)

        volume_type = volume_client.find_type(
            parsed_args.volume_type, ignore_missing=False
        )
        default_type = volume_client.set_default_type(
            parsed_args.project,
            volume_type.id,
        )
        return (
            column_headers,
            utils.get_item_properties(
                default_type,
                columns,
            ),
        )


class UnsetDefaultType(command.Command):
    """Remove a project's default volume type override (admin only).

    Restores fallback to the deployment-wide default configured by Cinder's
    default_volume_type option.

    This command requires ``--os-volume-api-version`` 3.67 or greater.
    """

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "project",
            metavar="<project_id>",
            default=None,
            help=_(
                'ID of project to remove the default volume type override for.'
            ),
        )
        return parser

    def take_action(self, parsed_args: argparse.Namespace) -> None:
        volume_client = sdk_utils.ensure_service_version(
            self.app.client_manager.volume, '3'
        )

        if not sdk_utils.supports_microversion(volume_client, '3.67'):
            msg = _(
                "--os-volume-api-version 3.67 or greater is required to "
                "support the 'volume type default unset' command"
            )
            raise exceptions.CommandError(msg)

        volume_client.unset_default_type(parsed_args.project)


class ListDefaultType(command.Lister):
    """List explicit per-project default volume type overrides (admin only).

    Projects without an override are not listed. Unlike
    ``volume type list --default``, this command lists project-to-type
    mappings, not the effective default type for the current project.

    This command requires ``--os-volume-api-version`` 3.67 or greater.
    """

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[tuple[Any, ...]]]:
        volume_client = sdk_utils.ensure_service_version(
            self.app.client_manager.volume, '3'
        )

        if not sdk_utils.supports_microversion(volume_client, '3.67'):
            msg = _(
                "--os-volume-api-version 3.67 or greater is required to "
                "support the 'volume type default list' command"
            )
            raise exceptions.CommandError(msg)

        column_headers = ['Project ID', 'Volume Type ID']
        columns = ['project_id', 'volume_type_id']

        default_types = volume_client.default_types()

        return (
            column_headers,
            (utils.get_item_properties(s, columns) for s in default_types),
        )


class ShowDefaultType(command.ShowOne):
    """Show a project's explicit default volume type override (admin only).

    Returns an error if no override is configured; does not fall back to the
    deployment-wide default. Use ``volume type list --default`` to see the
    effective default for the current project, including that fallback.

    This command requires ``--os-volume-api-version`` 3.67 or greater.
    """

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "project",
            metavar="<project_id>",
            help=_(
                'ID of project to show the default volume type override for.'
            ),
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[Any]]:
        volume_client = sdk_utils.ensure_service_version(
            self.app.client_manager.volume, '3'
        )

        if not sdk_utils.supports_microversion(volume_client, '3.67'):
            msg = _(
                "--os-volume-api-version 3.67 or greater is required to "
                "support the 'volume type default show' command"
            )
            raise exceptions.CommandError(msg)

        column_headers = ['Project ID', 'Volume Type ID']
        columns = ['project_id', 'volume_type_id']

        default_types = volume_client.show_default_type(
            parsed_args.project,
        )

        data = utils.get_item_properties(default_types, columns)

        return (column_headers, data)
