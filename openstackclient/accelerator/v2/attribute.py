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

"""Accelerator v2 device attribute action implementations"""

import argparse
from collections.abc import Iterable, Sequence
import logging
from typing import Any

from openstack.accelerator.v2 import attribute as _attribute
from osc_lib import exceptions
from osc_lib import utils

from openstackclient import command
from openstackclient.i18n import _

LOG = logging.getLogger(__name__)


def _format_attribute(
    attribute: _attribute.Attribute,
) -> tuple[tuple[str, ...], Iterable[Any]]:
    columns = (
        "created_at",
        "updated_at",
        "uuid",
        "deployable_id",
        "key",
        "value",
    )
    return columns, utils.get_item_properties(attribute, columns)


class CreateAttribute(command.ShowOne):
    _description = _("Register a new attribute with the accelerator service")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'deployable_id',
            metavar='<deployable_id>',
            help=_("Deployable ID for the attribute"),
        )
        parser.add_argument(
            'key',
            metavar='<key>',
            help=_("Key for the attribute"),
        )
        parser.add_argument(
            'value',
            metavar='<value>',
            help=_("Value for the attribute"),
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[Any]]:
        acc_client = self.app.client_manager.accelerator
        attrs = {
            'deployable_id': parsed_args.deployable_id,
            'key': parsed_args.key,
            'value': parsed_args.value,
        }
        attribute = acc_client.create_attribute(**attrs)
        return _format_attribute(attribute)


class DeleteAttribute(command.Command):
    _description = _("Delete attribute(s)")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'attributes',
            metavar='<uuid>',
            nargs='+',
            help=_("UUID(s) of the attribute(s) to delete"),
        )
        return parser

    def take_action(self, parsed_args: argparse.Namespace) -> None:
        acc_client = self.app.client_manager.accelerator
        result = 0
        for uuid in parsed_args.attributes:
            try:
                acc_client.delete_attribute(uuid, ignore_missing=False)
            except Exception as e:
                result += 1
                LOG.error(
                    _("Failed to delete attribute '%(uuid)s': %(e)s"),
                    {'uuid': uuid, 'e': e},
                )
        if result > 0:
            total = len(parsed_args.attributes)
            msg = _("%(result)s of %(total)s attributes failed to delete.") % {
                'result': result,
                'total': total,
            }
            raise exceptions.CommandError(msg)


class ListAttribute(command.Lister):
    _description = _("List all attributes")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--long',
            dest='detail',
            action='store_true',
            default=False,
            help=_("List additional fields in output"),
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[Any]]:
        acc_client = self.app.client_manager.accelerator

        column_headers: tuple[str, ...] = (
            "uuid",
            "deployable_id",
            "key",
            "value",
        )
        columns: tuple[str, ...] = column_headers

        if parsed_args.detail:
            column_headers += ("created_at", "updated_at")
            columns = column_headers

        data = acc_client.attributes()
        return (
            column_headers,
            (utils.get_item_properties(s, columns) for s in data),
        )


class ShowAttribute(command.ShowOne):
    _description = _("Show attribute details")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'attribute',
            metavar='<uuid>',
            help=_("UUID of the attribute"),
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[Any]]:
        acc_client = self.app.client_manager.accelerator
        attribute = acc_client.get_attribute(parsed_args.attribute)
        return _format_attribute(attribute)
