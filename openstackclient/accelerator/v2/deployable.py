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

"""Accelerator v2 deployable action implementations"""

import argparse
from collections.abc import Iterable, Sequence
import logging
from typing import Any

from openstack.accelerator.v2 import deployable as _deployable
from openstack import exceptions as sdk_exceptions
from osc_lib import exceptions
from osc_lib import utils

from openstackclient import command
from openstackclient.i18n import _

LOG = logging.getLogger(__name__)


def _get_deployable_properties(
    deployable: _deployable.Deployable,
    columns: tuple[str, ...],
) -> tuple[Any, ...]:
    # Deployable defines ``id = resource.Body('uuid', alternate_id=True)``
    # so the Python attribute is ``id``, not ``uuid``.
    attrs = tuple("id" if c == "uuid" else c for c in columns)
    return utils.get_item_properties(deployable, attrs)


def _format_deployable(
    deployable: _deployable.Deployable,
) -> tuple[tuple[str, ...], Iterable[Any]]:
    columns = (
        "created_at",
        "updated_at",
        "uuid",
        "name",
    )
    return columns, _get_deployable_properties(deployable, columns)


class ListDeployable(command.Lister):
    _description = _("List all deployables")

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

        columns: tuple[str, ...] = (
            "uuid",
            "name",
            "device_id",
        )

        if parsed_args.detail:
            columns = (
                "created_at",
                "updated_at",
                *columns,
                "parent_id",
                "root_id",
                "num_accelerators",
            )

        data = acc_client.deployables()
        return (
            columns,
            (_get_deployable_properties(s, columns) for s in data),
        )


class ProgramDeployable(command.ShowOne):
    _description = _("Reconfigure deployable with a new bitstream")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'deployable_uuid',
            metavar='<deployable_uuid>',
            help=_("UUID of the deployable to reconfigure"),
        )
        parser.add_argument(
            'image_uuid',
            metavar='<image_uuid>',
            help=_("UUID of the image to program"),
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[Any]]:
        acc_client = self.app.client_manager.accelerator
        dep_uuid = parsed_args.deployable_uuid

        acc_client.get_deployable(dep_uuid)

        image_client = self.app.client_manager.image
        image_uuid = parsed_args.image_uuid
        try:
            image_client.get_image(image_uuid)
        except sdk_exceptions.NotFoundException:
            msg = _('image not found: %s') % image_uuid
            raise exceptions.CommandError(msg)

        patch = [
            {
                'op': 'replace',
                'path': '/program',
                'value': [{'image_uuid': image_uuid}],
            }
        ]
        acc_client.patch_deployable(dep_uuid, patch)
        deployable = acc_client.get_deployable(dep_uuid)
        return _format_deployable(deployable)


class ShowDeployable(command.ShowOne):
    _description = _("Show deployable details")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'deployable',
            metavar='<uuid>',
            help=_("UUID of the deployable"),
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[Any]]:
        acc_client = self.app.client_manager.accelerator
        deployable = acc_client.get_deployable(parsed_args.deployable)
        return _format_deployable(deployable)
