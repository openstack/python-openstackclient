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

"""Accelerator v2 device profile action implementations"""

import argparse
from collections.abc import Iterable, Sequence
import json
import logging
from typing import Any

from openstack.accelerator.v2 import device_profile as _device_profile
from osc_lib import exceptions
from osc_lib import utils

from openstackclient import command
from openstackclient.i18n import _

LOG = logging.getLogger(__name__)


def _format_device_profile(
    device_profile: _device_profile.DeviceProfile,
) -> tuple[tuple[str, ...], Iterable[Any]]:
    columns = (
        "created_at",
        "updated_at",
        "uuid",
        "name",
        "groups",
        "description",
    )
    return columns, utils.get_item_properties(device_profile, columns)


class CreateDeviceProfile(command.ShowOne):
    _description = _(
        "Register a new device profile with the accelerator service"
    )

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<name>',
            help=_("Unique name for the device profile"),
        )
        parser.add_argument(
            'groups',
            metavar='<groups>',
            help=_(
                "Device profile groups as a JSON list. "
                "e.g. '[{\"resources:FPGA\": 1, "
                "\"trait:CUSTOM_FPGA_INTEL\": \"required\"}]'"
            ),
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_("Description for the device profile"),
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[Any]]:
        acc_client = self.app.client_manager.accelerator
        attrs = {
            'name': parsed_args.name,
            'groups': list(json.loads(parsed_args.groups)),
            'description': parsed_args.description,
        }
        device_profile = acc_client.create_device_profile(**attrs)
        return _format_device_profile(device_profile)


class DeleteDeviceProfile(command.Command):
    _description = _("Delete device profile(s)")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'device_profiles',
            metavar='<uuid>',
            nargs='+',
            help=_("UUID(s) of the device profile(s) to delete"),
        )
        return parser

    def take_action(self, parsed_args: argparse.Namespace) -> None:
        acc_client = self.app.client_manager.accelerator
        result = 0
        for uuid in parsed_args.device_profiles:
            try:
                acc_client.delete_device_profile(uuid, ignore_missing=False)
            except Exception as e:
                result += 1
                LOG.error(
                    _("Failed to delete device profile '%(uuid)s': %(e)s"),
                    {'uuid': uuid, 'e': e},
                )
        if result > 0:
            total = len(parsed_args.device_profiles)
            msg = _(
                "%(result)s of %(total)s device profiles failed to delete."
            ) % {'result': result, 'total': total}
            raise exceptions.CommandError(msg)


class ListDeviceProfile(command.Lister):
    _description = _("List all device profiles")

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
            "name",
            "groups",
            "description",
        )
        columns: tuple[str, ...] = column_headers

        if parsed_args.detail:
            column_headers += ("created_at", "updated_at")
            columns = column_headers

        data = acc_client.device_profiles()
        return (
            column_headers,
            (utils.get_item_properties(s, columns) for s in data),
        )


class ShowDeviceProfile(command.ShowOne):
    _description = _("Show device profile details")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'device_profile',
            metavar='<device_profile>',
            help=_("Name or UUID of the device profile"),
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[Any]]:
        acc_client = self.app.client_manager.accelerator
        device_profile = acc_client.get_device_profile(
            parsed_args.device_profile
        )
        return _format_device_profile(device_profile)
