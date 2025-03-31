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

"""Service Provider action implementations"""

import logging

from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _


LOG = logging.getLogger(__name__)


def _format_service_provider(sp):
    column_headers = (
        'id',
        'enabled',
        'description',
        'auth_url',
        'sp_url',
        'relay_state_prefix',
    )
    columns = (
        'id',
        'is_enabled',
        'description',
        'auth_url',
        'sp_url',
        'relay_state_prefix',
    )
    return (
        column_headers,
        utils.get_item_properties(sp, columns),
    )


class CreateServiceProvider(command.ShowOne):
    _description = _("Create new service provider")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'service_provider_id',
            metavar='<name>',
            help=_('New service provider name (must be unique)'),
        )
        parser.add_argument(
            '--auth-url',
            metavar='<auth-url>',
            required=True,
            help=_(
                'Authentication URL of remote federated service provider '
                '(required)'
            ),
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('New service provider description'),
        )
        parser.add_argument(
            '--service-provider-url',
            metavar='<sp-url>',
            required=True,
            help=_(
                'A service URL where SAML assertions are being sent (required)'
            ),
        )

        enable_service_provider = parser.add_mutually_exclusive_group()
        enable_service_provider.add_argument(
            '--enable',
            dest='is_enabled',
            action='store_true',
            default=True,
            help=_('Enable the service provider (default)'),
        )
        enable_service_provider.add_argument(
            '--disable',
            dest='is_enabled',
            action='store_false',
            help=_('Disable the service provider'),
        )

        return parser

    def take_action(self, parsed_args):
        service_client = self.app.client_manager.sdk_connection.identity

        kwargs = {}

        kwargs = {'id': parsed_args.service_provider_id}

        if parsed_args.is_enabled is not None:
            kwargs['is_enabled'] = parsed_args.is_enabled

        if parsed_args.description:
            kwargs['description'] = parsed_args.description

        if parsed_args.auth_url:
            kwargs['auth_url'] = parsed_args.auth_url

        if parsed_args.service_provider_url:
            kwargs['sp_url'] = parsed_args.service_provider_url

        sp = service_client.create_service_provider(**kwargs)

        return _format_service_provider(sp)


class DeleteServiceProvider(command.Command):
    _description = _("Delete service provider(s)")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'service_provider',
            metavar='<service-provider>',
            nargs='+',
            help=_('Service provider(s) to delete'),
        )
        return parser

    def take_action(self, parsed_args):
        service_client = self.app.client_manager.sdk_connection.identity
        result = 0
        for i in parsed_args.service_provider:
            try:
                service_client.delete_service_provider(i)
            except Exception as e:
                result += 1
                LOG.error(
                    _(
                        "Failed to delete service provider with "
                        "name or ID '%(provider)s': %(e)s"
                    ),
                    {'provider': i, 'e': e},
                )

        if result > 0:
            total = len(parsed_args.service_provider)
            msg = _(
                "%(result)s of %(total)s service providers failed to delete."
            ) % {'result': result, 'total': total}
            raise exceptions.CommandError(msg)


class ListServiceProvider(command.Lister):
    _description = _("List service providers")

    def take_action(self, parsed_args):
        service_client = self.app.client_manager.sdk_connection.identity
        data = service_client.service_providers()

        column_headers = (
            'ID',
            'Enabled',
            'Description',
            'Auth URL',
            'Service Provider URL',
            'Relay State Prefix',
        )
        columns = (
            'id',
            'is_enabled',
            'description',
            'auth_url',
            'sp_url',
            'relay_state_prefix',
        )
        return (
            column_headers,
            (utils.get_item_properties(s, columns) for s in data),
        )


class SetServiceProvider(command.ShowOne):
    _description = _("Set service provider properties")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'service_provider',
            metavar='<service-provider>',
            help=_('Service provider to modify'),
        )
        parser.add_argument(
            '--auth-url',
            metavar='<auth-url>',
            help=_(
                'New Authentication URL of remote federated service provider'
            ),
        )

        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('New service provider description'),
        )
        parser.add_argument(
            '--service-provider-url',
            metavar='<sp-url>',
            help=_('New service provider URL, where SAML assertions are sent'),
        )
        enable_service_provider = parser.add_mutually_exclusive_group()
        enable_service_provider.add_argument(
            '--enable',
            dest='is_enabled',
            action='store_true',
            default=None,
            help=_('Enable the service provider'),
        )
        enable_service_provider.add_argument(
            '--disable',
            dest='is_enabled',
            action='store_false',
            default=None,
            help=_('Disable the service provider'),
        )
        return parser

    def take_action(self, parsed_args):
        service_client = self.app.client_manager.sdk_connection.identity

        kwargs = {}

        if parsed_args.is_enabled is not None:
            kwargs['is_enabled'] = parsed_args.is_enabled

        if parsed_args.description:
            kwargs['description'] = parsed_args.description

        if parsed_args.auth_url:
            kwargs['auth_url'] = parsed_args.auth_url

        if parsed_args.service_provider_url:
            kwargs['sp_url'] = parsed_args.service_provider_url

        service_provider = service_client.update_service_provider(
            parsed_args.service_provider,
            **kwargs,
        )

        return _format_service_provider(service_provider)


class ShowServiceProvider(command.ShowOne):
    _description = _("Display service provider details")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'service_provider',
            metavar='<service-provider>',
            help=_('Service provider to display'),
        )
        return parser

    def take_action(self, parsed_args):
        service_client = self.app.client_manager.sdk_connection.identity
        service_provider = service_client.find_service_provider(
            parsed_args.service_provider,
            ignore_missing=False,
        )

        return _format_service_provider(service_provider)
