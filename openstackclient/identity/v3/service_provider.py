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
import six
import sys

from cliff import command
from cliff import lister
from cliff import show

from openstackclient.common import utils


class CreateServiceProvider(show.ShowOne):
    """Create new service provider"""

    log = logging.getLogger(__name__ + '.CreateServiceProvider')

    def get_parser(self, prog_name):
        parser = super(CreateServiceProvider, self).get_parser(prog_name)
        parser.add_argument(
            'service_provider_id',
            metavar='<name>',
            help='New service provider name (must be unique)'
        )
        parser.add_argument(
            '--auth-url',
            metavar='<auth-url>',
            required=True,
            help='Authentication URL of remote federated service provider '
                 '(required)',
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help='New service provider description',
        )
        parser.add_argument(
            '--service-provider-url',
            metavar='<sp-url>',
            required=True,
            help='A service URL where SAML assertions are being sent '
                 '(required)',
        )

        enable_service_provider = parser.add_mutually_exclusive_group()
        enable_service_provider.add_argument(
            '--enable',
            dest='enabled',
            action='store_true',
            default=True,
            help='Enable the service provider (default)',
        )
        enable_service_provider.add_argument(
            '--disable',
            dest='enabled',
            action='store_false',
            help='Disable the service provider',
        )

        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
        service_client = self.app.client_manager.identity
        sp = service_client.federation.service_providers.create(
            id=parsed_args.service_provider_id,
            auth_url=parsed_args.auth_url,
            description=parsed_args.description,
            enabled=parsed_args.enabled,
            sp_url=parsed_args.service_provider_url)

        sp._info.pop('links', None)
        return zip(*sorted(six.iteritems(sp._info)))


class DeleteServiceProvider(command.Command):
    """Delete service provider"""

    log = logging.getLogger(__name__ + '.DeleteServiceProvider')

    def get_parser(self, prog_name):
        parser = super(DeleteServiceProvider, self).get_parser(prog_name)
        parser.add_argument(
            'service_provider',
            metavar='<service-provider>',
            help='Service provider to delete',
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
        service_client = self.app.client_manager.identity
        service_client.federation.service_providers.delete(
            parsed_args.service_provider)
        return


class ListServiceProvider(lister.Lister):
    """List service providers"""

    log = logging.getLogger(__name__ + '.ListServiceProvider')

    @utils.log_method(log)
    def take_action(self, parsed_args):
        service_client = self.app.client_manager.identity
        data = service_client.federation.service_providers.list()

        column_headers = ('ID', 'Enabled', 'Description', 'Auth URL')
        return (column_headers,
                (utils.get_item_properties(
                    s, column_headers,
                    formatters={},
                ) for s in data))


class SetServiceProvider(command.Command):
    """Set service provider properties"""

    log = logging.getLogger(__name__ + '.SetServiceProvider')

    def get_parser(self, prog_name):
        parser = super(SetServiceProvider, self).get_parser(prog_name)
        parser.add_argument(
            'service_provider',
            metavar='<service-provider>',
            help='Service provider to modify',
        )
        parser.add_argument(
            '--auth-url',
            metavar='<auth-url>',
            help='New Authentication URL of remote federated service provider',
        )

        parser.add_argument(
            '--description',
            metavar='<description>',
            help='New service provider description',
        )
        parser.add_argument(
            '--service-provider-url',
            metavar='<sp-url>',
            help='New service provider URL, where SAML assertions are sent',
        )
        enable_service_provider = parser.add_mutually_exclusive_group()
        enable_service_provider.add_argument(
            '--enable',
            action='store_true',
            help='Enable the service provider',
        )
        enable_service_provider.add_argument(
            '--disable',
            action='store_true',
            help='Disable the service provider',
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
        federation_client = self.app.client_manager.identity.federation

        enabled = None
        if parsed_args.enable is True:
            enabled = True
        elif parsed_args.disable is True:
            enabled = False

        if not any((enabled is not None, parsed_args.description,
                    parsed_args.service_provider_url,
                    parsed_args.auth_url)):
            sys.stdout.write("Service Provider not updated, no arguments "
                             "present")
            return (None, None)

        service_provider = federation_client.service_providers.update(
            parsed_args.service_provider, enabled=enabled,
            description=parsed_args.description,
            auth_url=parsed_args.auth_url,
            sp_url=parsed_args.service_provider_url)
        return zip(*sorted(six.iteritems(service_provider._info)))


class ShowServiceProvider(show.ShowOne):
    """Display service provider details"""

    log = logging.getLogger(__name__ + '.ShowServiceProvider')

    def get_parser(self, prog_name):
        parser = super(ShowServiceProvider, self).get_parser(prog_name)
        parser.add_argument(
            'service_provider',
            metavar='<service-provider>',
            help='Service provider to display',
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
        service_client = self.app.client_manager.identity
        service_provider = utils.find_resource(
            service_client.federation.service_providers,
            parsed_args.service_provider)

        service_provider._info.pop('links', None)
        return zip(*sorted(six.iteritems(service_provider._info)))
