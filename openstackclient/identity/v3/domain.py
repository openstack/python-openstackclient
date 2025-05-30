#   Copyright 2012-2013 OpenStack Foundation
#
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

"""Identity v3 Domain action implementations"""

import logging

from openstack import exceptions as sdk_exceptions
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _
from openstackclient.identity import common


LOG = logging.getLogger(__name__)


def _format_domain(domain):
    columns = (
        'id',
        'name',
        'is_enabled',
        'description',
        'options',
    )
    column_headers = (
        'id',
        'name',
        'enabled',
        'description',
        'options',
    )

    return (
        column_headers,
        utils.get_item_properties(
            domain,
            columns,
        ),
    )


class CreateDomain(command.ShowOne):
    _description = _("Create new domain")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<domain-name>',
            help=_('New domain name'),
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('New domain description'),
        )
        enable_group = parser.add_mutually_exclusive_group()
        enable_group.add_argument(
            '--enable',
            dest='is_enabled',
            action='store_true',
            default=True,
            help=_('Enable domain (default)'),
        )
        enable_group.add_argument(
            '--disable',
            dest='is_enabled',
            action='store_false',
            help=_('Disable domain'),
        )
        parser.add_argument(
            '--or-show',
            action='store_true',
            help=_('Return existing domain'),
        )
        common.add_resource_option_to_parser(parser)
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.sdk_connection.identity

        options = {}
        if parsed_args.immutable is not None:
            options['immutable'] = parsed_args.immutable

        try:
            domain = identity_client.create_domain(
                name=parsed_args.name,
                description=parsed_args.description,
                options=options,
                is_enabled=parsed_args.is_enabled,
            )
        except sdk_exceptions.ConflictException:
            if parsed_args.or_show:
                domain = identity_client.find_domain(parsed_args.name)
                LOG.info(_('Returning existing domain %s'), domain.name)
            else:
                raise

        return _format_domain(domain)


class DeleteDomain(command.Command):
    _description = _("Delete domain(s)")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'domain',
            metavar='<domain>',
            nargs='+',
            help=_('Domain(s) to delete (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.sdk_connection.identity
        result = 0
        for i in parsed_args.domain:
            try:
                domain = identity_client.find_domain(i, ignore_missing=False)
                identity_client.delete_domain(domain.id)
            except Exception as e:
                result += 1
                LOG.error(
                    _(
                        "Failed to delete domain with name or "
                        "ID '%(domain)s': %(e)s"
                    ),
                    {'domain': i, 'e': e},
                )

        if result > 0:
            total = len(parsed_args.domain)
            msg = _("%(result)s of %(total)s domains failed to delete.") % {
                'result': result,
                'total': total,
            }
            raise exceptions.CommandError(msg)


class ListDomain(command.Lister):
    _description = _("List domains")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('The domain name'),
        )
        parser.add_argument(
            '--enabled',
            dest='is_enabled',
            action='store_true',
            help=_('The domains that are enabled will be returned'),
        )
        return parser

    def take_action(self, parsed_args):
        kwargs = {}
        if parsed_args.name:
            kwargs['name'] = parsed_args.name
        if parsed_args.is_enabled:
            kwargs['is_enabled'] = True

        columns = ('id', 'name', 'is_enabled', 'description')
        column_headers = ('ID', 'Name', 'Enabled', 'Description')
        data = self.app.client_manager.sdk_connection.identity.domains(
            **kwargs
        )

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


class SetDomain(command.Command):
    _description = _("Set domain properties")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'domain',
            metavar='<domain>',
            help=_('Domain to modify (name or ID)'),
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('New domain name'),
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('New domain description'),
        )
        enable_group = parser.add_mutually_exclusive_group()
        enable_group.add_argument(
            '--enable',
            dest='is_enabled',
            action='store_true',
            default=None,
            help=_('Enable domain'),
        )
        enable_group.add_argument(
            '--disable',
            dest='is_enabled',
            action='store_false',
            default=None,
            help=_('Disable domain'),
        )
        common.add_resource_option_to_parser(parser)
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.sdk_connection.identity
        domain = identity_client.find_domain(parsed_args.domain)
        kwargs = {}
        if parsed_args.name:
            kwargs['name'] = parsed_args.name
        if parsed_args.description:
            kwargs['description'] = parsed_args.description
        if parsed_args.is_enabled is not None:
            kwargs['is_enabled'] = parsed_args.is_enabled
        if parsed_args.immutable is not None:
            kwargs['options'] = {'immutable': parsed_args.immutable}

        identity_client.update_domain(domain.id, **kwargs)


class ShowDomain(command.ShowOne):
    _description = _("Display domain details")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'domain',
            metavar='<domain>',
            help=_('Domain to display (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.sdk_connection.identity
        domain = identity_client.find_domain(parsed_args.domain)

        return _format_domain(domain)
