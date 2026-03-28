# Copyright 2020, Red Hat Inc.
#
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

"""Compute v2 Server action implementations"""

import argparse
from collections.abc import Iterable, Sequence
from typing import Any

from openstack import utils as sdk_utils
from osc_lib import exceptions
from osc_lib import utils

from openstackclient import command
from openstackclient.i18n import _


def _get_server_share_columns(
    item: Any,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    # Non admin cannot see uuid and export location, so hide them
    if item.uuid is None:
        column_map = {
            'share_id': 'Share ID',
            'status': 'Status',
            'tag': 'Tag',
        }
        hidden_columns = [
            'id',
            'location',
            'name',
            'uuid',
            'export_location',
            'share_proto',
        ]
    else:
        column_map = {
            'uuid': 'UUID',
            'share_id': 'Share ID',
            'status': 'Status',
            'tag': 'Tag',
            'export_location': 'Export Location',
        }
        hidden_columns = ['id', 'location', 'name', 'share_proto']

    return utils.get_osc_show_columns_for_sdk_resource(
        item, column_map, hidden_columns
    )


class ListServerShare(command.Lister):
    """List all the shares attached to a server.

    Requires ``--os-compute-api-version 2.97`` or later.
    """

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help=_('Server to list share mapping for (name or ID)'),
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[tuple[str, ...], Iterable[tuple[Any, ...]]]:
        compute_client = self.app.client_manager.compute

        if not sdk_utils.supports_microversion(compute_client, '2.97'):
            msg = _(
                '--os-compute-api-version 2.97 or greater is required '
                'to support share attachments'
            )
            raise exceptions.CommandError(msg)

        server = compute_client.find_server(
            parsed_args.server,
            ignore_missing=False,
        )
        shares = compute_client.share_attachments(server)

        columns = (
            'share_id',
            'status',
            'tag',
        )
        column_headers = (
            'Share ID',
            'Status',
            'Tag',
        )

        return (
            column_headers,
            (utils.get_item_properties(s, columns) for s in shares),
        )


class ShowServerShare(command.ShowOne):
    """Show detail of a share attachment to a server.

    Requires ``--os-compute-api-version 2.97`` or later.
    """

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help=_('Server to show share mapping for (name or ID)'),
        )
        parser.add_argument(
            'share',
            metavar='<share>',
            help=_('Share to show details for (name or ID)'),
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[Any]]:
        compute_client = self.app.client_manager.compute
        shared_file_system_client = (
            self.app.client_manager.sdk_connection.shared_file_system
        )

        if not sdk_utils.supports_microversion(compute_client, '2.97'):
            msg = _(
                '--os-compute-api-version 2.97 or greater is required '
                'to support share attachments'
            )
            raise exceptions.CommandError(msg)

        server = compute_client.find_server(
            parsed_args.server,
            ignore_missing=False,
        )
        share = shared_file_system_client.find_share(
            parsed_args.share,
            ignore_missing=False,
        )
        share_attachment = compute_client.get_share_attachment(
            server, share.id
        )

        display_columns, columns = _get_server_share_columns(
            share_attachment,
        )
        data = utils.get_item_properties(share_attachment, columns)
        return display_columns, data


class AddServerShare(command.ShowOne):
    """Add a share to a server.

    Requires ``--os-compute-api-version 2.97`` or later.
    """

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help=_('Server to add share to (name or ID)'),
        )
        parser.add_argument(
            'share',
            metavar='<share>',
            help=_('Share to add (name or ID)'),
        )
        parser.add_argument(
            '--tag',
            metavar='<tag>',
            help=_(
                'Optional tag used to mount the share, '
                'if not provided the share uuid is used as tag by default'
            ),
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[Any]]:
        compute_client = self.app.client_manager.compute
        shared_file_system_client = (
            self.app.client_manager.sdk_connection.shared_file_system
        )

        if not sdk_utils.supports_microversion(compute_client, '2.97'):
            msg = _(
                '--os-compute-api-version 2.97 or greater is required '
                'to support share attachments'
            )
            raise exceptions.CommandError(msg)

        server = compute_client.find_server(
            parsed_args.server,
            ignore_missing=False,
        )
        share = shared_file_system_client.find_share(
            parsed_args.share,
            ignore_missing=False,
        )

        kwargs: dict[str, Any] = {}
        if parsed_args.tag:
            kwargs['tag'] = parsed_args.tag

        share_attachment = compute_client.create_share_attachment(
            server, share.id, **kwargs
        )

        display_columns, columns = _get_server_share_columns(
            share_attachment,
        )
        data = utils.get_item_properties(share_attachment, columns)
        return display_columns, data


class RemoveServerShare(command.Command):
    """Remove a share from a server.

    Requires ``--os-compute-api-version 2.97`` or later.
    """

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help=_('Server to remove share from (name or ID)'),
        )
        parser.add_argument(
            'share',
            metavar='<share>',
            help=_('Share to remove (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args: argparse.Namespace) -> None:
        compute_client = self.app.client_manager.compute
        shared_file_system_client = (
            self.app.client_manager.sdk_connection.shared_file_system
        )

        if not sdk_utils.supports_microversion(compute_client, '2.97'):
            msg = _(
                '--os-compute-api-version 2.97 or greater is required '
                'to support share attachments'
            )
            raise exceptions.CommandError(msg)

        server = compute_client.find_server(
            parsed_args.server,
            ignore_missing=False,
        )
        share = shared_file_system_client.find_share(
            parsed_args.share,
            ignore_missing=False,
        )
        compute_client.delete_share_attachment(server, share.id)
