#   Copyright 2012-2013 OpenStack, LLC.
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

"""Tenant action implementations"""

import logging

from cliff import command
from cliff import lister
from cliff import show

from openstackclient.common import utils


class CreateTenant(show.ShowOne):
    """Create tenant command"""

    api = 'identity'
    log = logging.getLogger(__name__ + '.CreateTenant')

    def get_parser(self, prog_name):
        parser = super(CreateTenant, self).get_parser(prog_name)
        parser.add_argument(
            'tenant_name',
            metavar='<tenant-name>',
            help='New tenant name')
        parser.add_argument(
            '--description',
            metavar='<tenant-description>',
            help='New tenant description')
        enable_group = parser.add_mutually_exclusive_group()
        enable_group.add_argument(
            '--enable',
            dest='enabled',
            action='store_true',
            default=True,
            help='Enable tenant')
        enable_group.add_argument(
            '--disable',
            dest='enabled',
            action='store_false',
            help='Disable tenant')
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity
        tenant = identity_client.tenants.create(
            parsed_args.tenant_name,
            description=parsed_args.description,
            enabled=parsed_args.enabled)

        info = {}
        info.update(tenant._info)
        return zip(*sorted(info.iteritems()))


class DeleteTenant(command.Command):
    """Delete tenant command"""

    api = 'identity'
    log = logging.getLogger(__name__ + '.DeleteTenant')

    def get_parser(self, prog_name):
        parser = super(DeleteTenant, self).get_parser(prog_name)
        parser.add_argument(
            'tenant',
            metavar='<tenant>',
            help='Name or ID of tenant to delete')
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity
        tenant = utils.find_resource(identity_client.tenants,
                                     parsed_args.tenant)
        identity_client.tenants.delete(tenant.id)
        return


class ListTenant(lister.Lister):
    """List tenant command"""

    api = 'identity'
    log = logging.getLogger(__name__ + '.ListTenant')

    def get_parser(self, prog_name):
        parser = super(ListTenant, self).get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help='Additional fields are listed in output')
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        if parsed_args.long:
            columns = ('ID', 'Name', 'Description', 'Enabled')
        else:
            columns = ('ID', 'Name')
        data = self.app.client_manager.identity.tenants.list()
        return (columns,
                (utils.get_item_properties(
                    s, columns,
                    formatters={},
                ) for s in data))


class SetTenant(command.Command):
    """Set tenant command"""

    api = 'identity'
    log = logging.getLogger(__name__ + '.SetTenant')

    def get_parser(self, prog_name):
        parser = super(SetTenant, self).get_parser(prog_name)
        parser.add_argument(
            'tenant',
            metavar='<tenant>',
            help='Name or ID of tenant to change')
        parser.add_argument(
            '--name',
            metavar='<new-tenant-name>',
            help='New tenant name')
        parser.add_argument(
            '--description',
            metavar='<tenant-description>',
            help='New tenant description')
        enable_group = parser.add_mutually_exclusive_group()
        enable_group.add_argument(
            '--enable',
            dest='enabled',
            action='store_true',
            default=True,
            help='Enable tenant (default)')
        enable_group.add_argument(
            '--disable',
            dest='enabled',
            action='store_false',
            help='Disable tenant')
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity
        tenant = utils.find_resource(identity_client.tenants,
                                     parsed_args.tenant)
        kwargs = {}
        if parsed_args.name:
            kwargs['name'] = parsed_args.name
        if parsed_args.description:
            kwargs['description'] = parsed_args.description
        if 'enabled' in parsed_args:
            kwargs['enabled'] = parsed_args.enabled

        if kwargs == {}:
            stdout.write("Tenant not updated, no arguments present")
            return 0
        tenant.update(**kwargs)
        return


class ShowTenant(show.ShowOne):
    """Show tenant command"""

    api = 'identity'
    log = logging.getLogger(__name__ + '.ShowTenant')

    def get_parser(self, prog_name):
        parser = super(ShowTenant, self).get_parser(prog_name)
        parser.add_argument(
            'tenant',
            metavar='<tenant>',
            help='Name or ID of tenant to display')
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity
        tenant = utils.find_resource(identity_client.tenants,
                                     parsed_args.tenant)

        info = {}
        info.update(tenant._info)
        return zip(*sorted(info.iteritems()))
