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
#

"""Identity v3 IdentityProvider action implementations"""

import argparse
from collections.abc import Iterable, Sequence
import logging
from typing import Any

from openstack import utils as sdk_utils
from osc_lib.cli import format_columns
from osc_lib import exceptions
from osc_lib import utils

from openstackclient import command
from openstackclient.i18n import _
from openstackclient.identity import common


LOG = logging.getLogger(__name__)


def _format_identity_provider(idp):
    columns = (
        'authorization_ttl',
        'description',
        'domain_id',
        'is_enabled',
        'name',
        'remote_ids',
    )
    column_headers = (
        'authorization_ttl',
        'description',
        'domain_id',
        'enabled',
        'id',
        'remote_ids',
    )
    return (
        column_headers,
        utils.get_item_properties(
            idp, columns, formatters={'remote_ids': format_columns.ListColumn}
        ),
    )


class CreateIdentityProvider(command.ShowOne):
    _description = _("Create new identity provider")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'identity_provider_id',
            metavar='<name>',
            help=_('New identity provider name (must be unique)'),
        )
        identity_remote_id_provider = parser.add_mutually_exclusive_group()
        identity_remote_id_provider.add_argument(
            '--remote-id',
            metavar='<remote-id>',
            dest='remote_ids',
            action='append',
            help=_(
                'Remote IDs to associate with the Identity Provider '
                '(repeat option to provide multiple values)'
            ),
        )
        identity_remote_id_provider.add_argument(
            '--remote-id-file',
            metavar='<file-name>',
            help=_(
                'Name of a file that contains many remote IDs to associate '
                'with the identity provider, one per line'
            ),
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('New identity provider description'),
        )
        parser.add_argument(
            '--domain',
            metavar='<domain>',
            help=_(
                'Domain to associate with the identity provider. If not '
                'specified, a domain will be created automatically. '
                '(Name or ID)'
            ),
        )
        parser.add_argument(
            '--authorization-ttl',
            metavar='<authorization-ttl>',
            type=int,
            help=_(
                'Time to keep the role assignments for users '
                'authenticating via this identity provider. '
                'When not provided, global default configured in the '
                'Identity service will be used. '
                'Available since Identity API version 3.14 (Ussuri).'
            ),
        )
        enable_identity_provider = parser.add_mutually_exclusive_group()
        enable_identity_provider.add_argument(
            '--enable',
            dest='enabled',
            action='store_true',
            default=True,
            help=_('Enable identity provider (default)'),
        )
        enable_identity_provider.add_argument(
            '--disable',
            dest='enabled',
            action='store_false',
            help=_('Disable the identity provider'),
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[Any]]:
        identity_client = sdk_utils.ensure_service_version(
            self.app.client_manager.sdk_connection.identity, '3'
        )
        kwargs = {'is_enabled': parsed_args.enabled}
        if parsed_args.identity_provider_id:
            kwargs['id'] = parsed_args.identity_provider_id
        if parsed_args.description:
            kwargs['description'] = parsed_args.description

        if parsed_args.remote_id_file:
            file_content = utils.read_blob_file_contents(
                parsed_args.remote_id_file
            )
            remote_ids = file_content.splitlines()
            kwargs['remote_ids'] = list(map(str.strip, remote_ids))
        elif parsed_args.remote_ids:
            kwargs['remote_ids'] = parsed_args.remote_ids

        if parsed_args.domain:
            kwargs['domain_id'] = common.find_domain_id_sdk(
                identity_client,
                parsed_args.domain,
                validate_actor_existence=False,
            )

        auth_ttl = parsed_args.authorization_ttl
        if auth_ttl is not None:
            if auth_ttl < 0:
                msg = _("%(param)s must be positive integer or zero.") % {
                    "param": "authorization-ttl"
                }
                raise exceptions.CommandError(msg)
            kwargs['authorization_ttl'] = auth_ttl

        idp = identity_client.create_identity_provider(**kwargs)

        return _format_identity_provider(idp)


class DeleteIdentityProvider(command.Command):
    _description = _("Delete identity provider(s)")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'identity_provider',
            metavar='<identity-provider>',
            nargs='+',
            help=_('Identity provider(s) to delete'),
        )
        return parser

    def take_action(self, parsed_args: argparse.Namespace) -> None:
        identity_client = sdk_utils.ensure_service_version(
            self.app.client_manager.sdk_connection.identity, '3'
        )
        result = 0
        for i in parsed_args.identity_provider:
            try:
                identity_client.delete_identity_provider(i)
            except Exception as e:
                result += 1
                LOG.error(
                    _(
                        "Failed to delete identity provider with "
                        "name or ID '%(provider)s': %(e)s"
                    ),
                    {'provider': i, 'e': e},
                )

        if result > 0:
            total = len(parsed_args.identity_provider)
            msg = _(
                "%(result)s of %(total)s identity providers failed to delete."
            ) % {'result': result, 'total': total}
            raise exceptions.CommandError(msg)


class ListIdentityProvider(command.Lister):
    _description = _("List identity providers")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--id',
            metavar='<id>',
            help=_('Filter identity providers by ID'),
        )
        parser.add_argument(
            '--enabled',
            dest='enabled',
            action='store_true',
            help=_('List only enabled identity providers'),
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[tuple[str, ...], Iterable[tuple[Any, ...]]]:
        columns = ('id', 'is_enabled', 'domain_id', 'description')
        column_headers = ('ID', 'Enabled', 'Domain ID', 'Description')
        identity_client = sdk_utils.ensure_service_version(
            self.app.client_manager.sdk_connection.identity, '3'
        )

        kwargs = {}
        if parsed_args.id:
            kwargs['id'] = parsed_args.id
        if parsed_args.enabled:
            kwargs['is_enabled'] = True

        data = identity_client.identity_providers(**kwargs)
        return (
            column_headers,
            (
                utils.get_item_properties(
                    s,
                    columns,
                    formatters={},
                )
                for s in data
            ),
        )


class SetIdentityProvider(command.Command):
    _description = _("Set identity provider properties")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'identity_provider',
            metavar='<identity-provider>',
            help=_('Identity provider to modify'),
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('Set identity provider description'),
        )
        identity_remote_id_provider = parser.add_mutually_exclusive_group()
        identity_remote_id_provider.add_argument(
            '--remote-id',
            metavar='<remote-id>',
            dest='remote_ids',
            action='append',
            help=_(
                'Remote IDs to associate with the Identity Provider '
                '(repeat option to provide multiple values)'
            ),
        )
        identity_remote_id_provider.add_argument(
            '--remote-id-file',
            metavar='<file-name>',
            help=_(
                'Name of a file that contains many remote IDs to associate '
                'with the identity provider, one per line'
            ),
        )
        parser.add_argument(
            '--authorization-ttl',
            metavar='<authorization-ttl>',
            type=int,
            help=_(
                'Time to keep the role assignments for users '
                'authenticating via this identity provider. '
                'Available since Identity API version 3.14 (Ussuri).'
            ),
        )
        enable_identity_provider = parser.add_mutually_exclusive_group()
        enable_identity_provider.add_argument(
            '--enable',
            action='store_true',
            help=_('Enable the identity provider'),
        )
        enable_identity_provider.add_argument(
            '--disable',
            action='store_true',
            help=_('Disable the identity provider'),
        )
        return parser

    def take_action(self, parsed_args: argparse.Namespace) -> None:
        identity_client = sdk_utils.ensure_service_version(
            self.app.client_manager.sdk_connection.identity, '3'
        )

        # Always set remote_ids if either is passed in
        if parsed_args.remote_id_file:
            file_content = utils.read_blob_file_contents(
                parsed_args.remote_id_file
            )
            remote_ids = file_content.splitlines()
            remote_ids = list(map(str.strip, remote_ids))
        elif parsed_args.remote_ids:
            remote_ids = parsed_args.remote_ids

        # Setup keyword args for the client
        kwargs = {}
        if parsed_args.description:
            kwargs['description'] = parsed_args.description
        if parsed_args.enable:
            kwargs['is_enabled'] = True
        if parsed_args.disable:
            kwargs['is_enabled'] = False
        if parsed_args.remote_id_file or parsed_args.remote_ids:
            kwargs['remote_ids'] = remote_ids

        # NOTE(0weng): This is now possible in SDK! An option should be added.
        # Original comment:
        # TODO(pas-ha) make it possible to reset authorization_ttl
        # back to None value.
        # Currently not possible as filter_kwargs decorator in
        # keystoneclient/base.py explicitly drops the None-valued keys
        # from kwargs, and 'update' method is wrapped in this decorator.
        auth_ttl = parsed_args.authorization_ttl
        if auth_ttl is not None:
            if auth_ttl < 0:
                msg = _("%(param)s must be positive integer or zero.") % {
                    "param": "authorization-ttl"
                }
                raise exceptions.CommandError(msg)
            kwargs['authorization_ttl'] = auth_ttl

        identity_client.update_identity_provider(
            parsed_args.identity_provider, **kwargs
        )


class ShowIdentityProvider(command.ShowOne):
    _description = _("Display identity provider details")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'identity_provider',
            metavar='<identity-provider>',
            help=_('Identity provider to display'),
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[Any]]:
        identity_client = sdk_utils.ensure_service_version(
            self.app.client_manager.sdk_connection.identity, '3'
        )
        idp = identity_client.get_identity_provider(
            parsed_args.identity_provider
        )

        return _format_identity_provider(idp)
