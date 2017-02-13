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
import six

from openstackclient.i18n import _
from openstackclient.identity import common


LOG = logging.getLogger(__name__)


class CreateService(command.ShowOne):
    _description = _("Create new service")

    def get_parser(self, prog_name):
        parser = super(CreateService, self).get_parser(prog_name)
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
            help=_('Enable service (default)'),
        )
        enable_group.add_argument(
            '--disable',
            action='store_true',
            help=_('Disable service'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        enabled = True
        if parsed_args.disable:
            enabled = False

        service = identity_client.services.create(
            name=parsed_args.name,
            type=parsed_args.type,
            description=parsed_args.description,
            enabled=enabled,
        )

        service._info.pop('links')
        return zip(*sorted(six.iteritems(service._info)))


class DeleteService(command.Command):
    _description = _("Delete service(s)")

    def get_parser(self, prog_name):
        parser = super(DeleteService, self).get_parser(prog_name)
        parser.add_argument(
            'service',
            metavar='<service>',
            nargs='+',
            help=_('Service(s) to delete (type, name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        result = 0
        for i in parsed_args.service:
            try:
                service = common.find_service(identity_client, i)
                identity_client.services.delete(service.id)
            except Exception as e:
                result += 1
                LOG.error(_("Failed to delete consumer with type, "
                          "name or ID '%(service)s': %(e)s"),
                          {'service': i, 'e': e})

        if result > 0:
            total = len(parsed_args.service)
            msg = (_("%(result)s of %(total)s services failed "
                   "to delete.") % {'result': result, 'total': total})
            raise exceptions.CommandError(msg)


class ListService(command.Lister):
    _description = _("List services")

    def get_parser(self, prog_name):
        parser = super(ListService, self).get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_('List additional fields in output'),
        )
        return parser

    def take_action(self, parsed_args):

        if parsed_args.long:
            columns = ('ID', 'Name', 'Type', 'Description', 'Enabled')
        else:
            columns = ('ID', 'Name', 'Type')
        data = self.app.client_manager.identity.services.list()
        return (
            columns,
            (utils.get_item_properties(s, columns) for s in data),
        )


class SetService(command.Command):
    _description = _("Set service properties")

    def get_parser(self, prog_name):
        parser = super(SetService, self).get_parser(prog_name)
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
            help=_('Enable service'),
        )
        enable_group.add_argument(
            '--disable',
            action='store_true',
            help=_('Disable service'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        service = common.find_service(identity_client,
                                      parsed_args.service)
        kwargs = {}
        if parsed_args.type:
            kwargs['type'] = parsed_args.type
        if parsed_args.name:
            kwargs['name'] = parsed_args.name
        if parsed_args.description:
            kwargs['description'] = parsed_args.description
        if parsed_args.enable:
            kwargs['enabled'] = True
        if parsed_args.disable:
            kwargs['enabled'] = False

        identity_client.services.update(
            service.id,
            **kwargs
        )


class ShowService(command.ShowOne):
    _description = _("Display service details")

    def get_parser(self, prog_name):
        parser = super(ShowService, self).get_parser(prog_name)
        parser.add_argument(
            'service',
            metavar='<service>',
            help=_('Service to display (type, name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        service = common.find_service(identity_client, parsed_args.service)

        service._info.pop('links')
        return zip(*sorted(six.iteritems(service._info)))
