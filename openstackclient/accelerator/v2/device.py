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

"""Accelerator v2 device action implementations"""

import argparse
from collections.abc import Iterable, Sequence
import logging
from typing import Any

from openstack.accelerator.v2 import device as _device
from osc_lib import utils

from openstackclient import command
from openstackclient.i18n import _

LOG = logging.getLogger(__name__)


def _format_device(
    device: _device.Device,
) -> tuple[tuple[str, ...], Iterable[Any]]:
    columns = (
        "created_at",
        "updated_at",
        "uuid",
        "type",
        "vendor",
        "model",
        "hostname",
        "std_board_info",
        "vendor_board_info",
    )
    return columns, utils.get_item_properties(device, columns)


class ListDevice(command.Lister):
    _description = _("List all devices")

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
            "type",
            "vendor",
            "hostname",
            "std_board_info",
        )
        columns: tuple[str, ...] = column_headers

        if parsed_args.detail:
            column_headers += (
                "created_at",
                "updated_at",
                "model",
                "vendor_board_info",
            )
            columns = column_headers

        data = acc_client.devices()
        return (
            column_headers,
            (utils.get_item_properties(s, columns) for s in data),
        )


class ShowDevice(command.ShowOne):
    _description = _("Show device details")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'device',
            metavar='<uuid>',
            help=_("UUID of the device"),
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[Any]]:
        acc_client = self.app.client_manager.accelerator
        device = acc_client.get_device(parsed_args.device)
        return _format_device(device)
