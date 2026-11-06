# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
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

FIELDS = ('name',)


class ListResourceClass(command.Lister):
    """Return a list of all resource classes.

    This command requires at least ``--os-placement-api-version 1.2``.
    """

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[tuple[str, ...], Iterable[tuple[Any, ...]]]:
        placement_client = self.app.client_manager.sdk_connection.placement

        if not sdk_utils.supports_microversion(placement_client, '1.2'):
            msg = _(
                '--os-placement-api-version 1.2 or greater is required '
                "to support the 'resource class list' command"
            )
            raise exceptions.CommandError(msg)

        resource_classes = list(placement_client.resource_classes())
        rows = ((rc.name,) for rc in resource_classes)
        return FIELDS, rows


class CreateResourceClass(command.Command):
    """Create a new resource class.

    This command requires at least ``--os-placement-api-version 1.2``.
    """

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'name', metavar='<name>', help='Name of the resource class'
        )
        return parser

    def take_action(self, parsed_args: argparse.Namespace) -> None:
        placement_client = self.app.client_manager.sdk_connection.placement

        if not sdk_utils.supports_microversion(placement_client, '1.2'):
            msg = _(
                '--os-placement-api-version 1.2 or greater is required '
                "to support the 'resource class create' command"
            )
            raise exceptions.CommandError(msg)

        placement_client.create_resource_class(name=parsed_args.name)


class SetResourceClass(command.Command):
    """Create or validate the existence of single resource class.

    Unlike ``openstack resource class create``, this command also succeeds if
    the resource class already exists, which makes this an idempotent check or
    create command.

    This command requires at least ``--os-placement-api-version 1.7``.
    """

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'name', metavar='<name>', help='Name of the resource class'
        )
        return parser

    def take_action(self, parsed_args: argparse.Namespace) -> None:
        placement_client = self.app.client_manager.sdk_connection.placement

        if not sdk_utils.supports_microversion(placement_client, '1.7'):
            msg = _(
                '--os-placement-api-version 1.7 or greater is required '
                "to support the 'resource class set' command"
            )
            raise exceptions.CommandError(msg)

        placement_client.update_resource_class(parsed_args.name)


class ShowResourceClass(command.ShowOne):
    """Return a representation of the resource class identified by ``<name>``.

    This command requires at least ``--os-placement-api-version 1.2``.
    """

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'name', metavar='<name>', help='Name of the resource class'
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[Any]]:
        placement_client = self.app.client_manager.sdk_connection.placement

        if not sdk_utils.supports_microversion(placement_client, '1.2'):
            msg = _(
                '--os-placement-api-version 1.2 or greater is required '
                "to support the 'resource class show' command"
            )
            raise exceptions.CommandError(msg)

        rc = placement_client.get_resource_class(parsed_args.name)
        return FIELDS, utils.get_item_properties(rc, FIELDS)


class DeleteResourceClass(command.Command):
    """Delete the resource class identified by ``<name>``.

    Only custom resource classes can be deleted.

    This command requires at least ``--os-placement-api-version 1.2``.
    """

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'name', metavar='<name>', help='Name of the resource class'
        )
        return parser

    def take_action(self, parsed_args: argparse.Namespace) -> None:
        placement_client = self.app.client_manager.sdk_connection.placement

        if not sdk_utils.supports_microversion(placement_client, '1.2'):
            msg = _(
                '--os-placement-api-version 1.2 or greater is required '
                "to support the 'resource class delete' command"
            )
            raise exceptions.CommandError(msg)

        placement_client.delete_resource_class(
            parsed_args.name, ignore_missing=False
        )
