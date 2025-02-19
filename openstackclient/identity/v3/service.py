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

"""Identity v3 Service action implementations"""

import logging

from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _
from openstackclient.identity import common


LOG = logging.getLogger(__name__)


def _format_service(service):
    columns = (
        'id',
        'name',
        'type',
        'is_enabled',
        'description',
    )
    column_headers = (
        'id',
        'name',
        'type',
        'enabled',
        'description',
    )

    return (
        column_headers,
        utils.get_item_properties(
            service,
            columns,
        ),
    )


class CreateService(command.ShowOne):
    _description = _("Create new service")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'type',
            metavar='<type>',
            help=_('New service type (compute, image, identity, volume, etc)'),
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('New service name'),
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('New service description'),
        )
        enable_group = parser.add_mutually_exclusive_group()
        enable_group.add_argument(
            '--enable',
            action='store_true',
            dest='is_enabled',
            default=True,
            help=_('Enable service (default)'),
        )
        enable_group.add_argument(
            '--disable',
            action='store_false',
            dest='is_enabled',
            default=True,
            help=_('Disable service'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.sdk_connection.identity

        service = identity_client.create_service(
            name=parsed_args.name,
            type=parsed_args.type,
            description=parsed_args.description,
            is_enabled=parsed_args.is_enabled,
        )

        return _format_service(service)


class DeleteService(command.Command):
    _description = _("Delete service(s)")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'service',
            metavar='<service>',
            nargs='+',
            help=_('Service(s) to delete (type, name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.sdk_connection.identity
        result = 0
        for i in parsed_args.service:
            try:
                service = common.find_service_sdk(identity_client, i)
                identity_client.delete_service(service.id)
            except Exception as e:
                result += 1
                LOG.error(
                    _(
                        "Failed to delete consumer with type, "
                        "name or ID '%(service)s': %(e)s"
                    ),
                    {'service': i, 'e': e},
                )

        if result > 0:
            total = len(parsed_args.service)
            msg = _("%(result)s of %(total)s services failed to delete.") % {
                'result': result,
                'total': total,
            }
            raise exceptions.CommandError(msg)


class ListService(command.Lister):
    _description = _("List services")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_('List additional fields in output'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.sdk_connection.identity

        columns: tuple[str, ...] = ('id', 'name', 'type')
        column_headers: tuple[str, ...] = ('ID', 'Name', 'Type')
        if parsed_args.long:
            columns += ('description', 'is_enabled')
            column_headers += ('Description', 'Enabled')

        data = identity_client.services()

        return (
            column_headers,
            (utils.get_item_properties(s, columns) for s in data),
        )


class SetService(command.Command):
    _description = _("Set service properties")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'service',
            metavar='<service>',
            help=_('Service to modify (type, name or ID)'),
        )
        parser.add_argument(
            '--type',
            metavar='<type>',
            help=_('New service type (compute, image, identity, volume, etc)'),
        )
        parser.add_argument(
            '--name',
            metavar='<service-name>',
            help=_('New service name'),
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('New service description'),
        )
        enable_group = parser.add_mutually_exclusive_group()
        enable_group.add_argument(
            '--enable',
            action='store_true',
            dest='is_enabled',
            default=None,
            help=_('Enable service'),
        )
        enable_group.add_argument(
            '--disable',
            action='store_false',
            dest='is_enabled',
            default=None,
            help=_('Disable service'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.sdk_connection.identity

        service = common.find_service_sdk(identity_client, parsed_args.service)
        kwargs = {}
        if parsed_args.type:
            kwargs['type'] = parsed_args.type
        if parsed_args.name:
            kwargs['name'] = parsed_args.name
        if parsed_args.description:
            kwargs['description'] = parsed_args.description
        if parsed_args.is_enabled is not None:
            kwargs['is_enabled'] = parsed_args.is_enabled

        identity_client.update_service(service.id, **kwargs)


class ShowService(command.ShowOne):
    _description = _("Display service details")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'service',
            metavar='<service>',
            help=_('Service to display (type, name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.sdk_connection.identity

        service = common.find_service_sdk(identity_client, parsed_args.service)

        return _format_service(service)
