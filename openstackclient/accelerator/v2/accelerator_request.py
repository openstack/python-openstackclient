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

"""Accelerator v2 accelerator request (ARQ) action implementations"""

import argparse
from collections.abc import Iterable, Sequence
import logging
from typing import Any

from openstack.accelerator.v2 import accelerator_request as _arq
from osc_lib import exceptions
from osc_lib import utils

from openstackclient import command
from openstackclient.i18n import _

LOG = logging.getLogger(__name__)


def _format_accelerator_request(
    arq: _arq.AcceleratorRequest,
) -> tuple[tuple[str, ...], Iterable[Any]]:
    columns = (
        "uuid",
        "state",
        "device_profile_name",
        "hostname",
        "device_rp_uuid",
        "instance_uuid",
        "attach_handle_type",
        "attach_handle_info",
    )
    return columns, utils.get_item_properties(arq, columns)


class BindAcceleratorRequest(command.ShowOne):
    _description = _("Bind accelerator to instance")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'accelerator_request',
            metavar='<accelerator_request>',
            help=_("UUID of the accelerator request"),
        )
        parser.add_argument(
            'hostname',
            metavar='<hostname>',
            help=_("Hostname to bind the accelerator request to"),
        )
        parser.add_argument(
            'instance_uuid',
            metavar='<instance_uuid>',
            help=_("UUID of the instance to bind the accelerator request to"),
        )
        parser.add_argument(
            'device_rp_uuid',
            metavar='<device_rp_uuid>',
            help=_(
                "UUID of the device resource provider to "
                "bind the accelerator request to"
            ),
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[Any]]:
        acc_client = self.app.client_manager.accelerator
        patch = []
        for field in ('hostname', 'instance_uuid', 'device_rp_uuid'):
            value = getattr(parsed_args, field)
            if value:
                patch.append(
                    {
                        'op': 'add',
                        'path': '/' + field,
                        'value': value,
                    }
                )
        if patch:
            acc_client.patch_accelerator_request(
                parsed_args.accelerator_request, patch
            )
        arq = acc_client.get_accelerator_request(
            parsed_args.accelerator_request
        )
        return _format_accelerator_request(arq)


class CreateAcceleratorRequest(command.ShowOne):
    _description = _(
        "Register a new accelerator request with the accelerator service"
    )

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'device_profile_name',
            metavar='<device_profile_name>',
            help=_("Name of the device profile for the accelerator request"),
        )
        parser.add_argument(
            '--group-id',
            metavar='<device_profile_group_id>',
            dest='group_id',
            help=_(
                "Group ID of the device profile for the accelerator request"
            ),
        )
        parser.add_argument(
            '--image-uuid',
            metavar='<glance_image_uuid>',
            dest='img_uuid',
            help=_("UUID of the image saved in Glance"),
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[Any]]:
        acc_client = self.app.client_manager.accelerator
        attrs = {
            'device_profile_name': parsed_args.device_profile_name,
            'device_profile_group_id': parsed_args.group_id,
            'image_uuid': parsed_args.img_uuid,
        }
        arq = acc_client.create_accelerator_request(**attrs)
        return _format_accelerator_request(arq)


class DeleteAcceleratorRequest(command.Command):
    _description = _("Delete accelerator request(s)")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'accelerator_requests',
            metavar='<uuid>',
            nargs='+',
            help=_("UUID(s) of the accelerator request(s) to delete"),
        )
        return parser

    def take_action(self, parsed_args: argparse.Namespace) -> None:
        acc_client = self.app.client_manager.accelerator
        result = 0
        for uuid in parsed_args.accelerator_requests:
            try:
                acc_client.delete_accelerator_request(
                    uuid, ignore_missing=False
                )
            except Exception as e:
                result += 1
                LOG.error(
                    _(
                        "Failed to delete accelerator "
                        "request '%(uuid)s': %(e)s"
                    ),
                    {'uuid': uuid, 'e': e},
                )
        if result > 0:
            total = len(parsed_args.accelerator_requests)
            msg = _(
                "%(result)s of %(total)s accelerator requests "
                "failed to delete."
            ) % {'result': result, 'total': total}
            raise exceptions.CommandError(msg)


class ListAcceleratorRequest(command.Lister):
    _description = _("List all accelerator requests")

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
            "state",
            "device_profile_name",
            "instance_uuid",
            "attach_handle_type",
            "attach_handle_info",
        )
        columns: tuple[str, ...] = column_headers

        if parsed_args.detail:
            column_headers += ("hostname", "device_rp_uuid")
            columns = column_headers

        data = acc_client.accelerator_requests()
        return (
            column_headers,
            (utils.get_item_properties(s, columns) for s in data),
        )


class ShowAcceleratorRequest(command.ShowOne):
    _description = _("Show accelerator request details")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'accelerator_request',
            metavar='<uuid>',
            help=_("UUID of the accelerator request"),
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[Any]]:
        acc_client = self.app.client_manager.accelerator
        arq = acc_client.get_accelerator_request(
            parsed_args.accelerator_request
        )
        return _format_accelerator_request(arq)


class UnbindAcceleratorRequest(command.ShowOne):
    _description = _("Unbind accelerator from instance")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'accelerator_request',
            metavar='<accelerator_request>',
            help=_("UUID of the accelerator request"),
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[Any]]:
        acc_client = self.app.client_manager.accelerator
        patch = [
            {'op': 'remove', 'path': '/hostname'},
            {'op': 'remove', 'path': '/instance_uuid'},
            {'op': 'remove', 'path': '/device_rp_uuid'},
        ]
        acc_client.patch_accelerator_request(
            parsed_args.accelerator_request, patch
        )
        arq = acc_client.get_accelerator_request(
            parsed_args.accelerator_request
        )
        return _format_accelerator_request(arq)
