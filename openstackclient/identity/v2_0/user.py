# Copyright 2012 OpenStack LLC.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#
# vim: tabstop=4 shiftwidth=4 softtabstop=4

"""
User action implementations
"""

import logging

from cliff import lister
from cliff import show

from openstackclient.common import command
from openstackclient.common import utils


class CreateUser(command.OpenStackCommand, show.ShowOne):
    """Create user command"""

    api = 'identity'
    log = logging.getLogger(__name__ + '.CreateUser')

    def get_parser(self, prog_name):
        parser = super(CreateUser, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<user-name>',
            help='New user name',
        )
        parser.add_argument(
            '--password',
            metavar='<user-password>',
            help='New user password',
        )
        parser.add_argument(
            '--email',
            metavar='<user-email>',
            help='New user email address',
        )
        parser.add_argument(
            '--tenant',
            metavar='<tenant>',
            help='New default tenant name or ID',
        )
        enable_group = parser.add_mutually_exclusive_group()
        enable_group.add_argument(
            '--enable',
            dest='enabled',
            action='store_true',
            default=True,
            help='Enable user',
        )
        enable_group.add_argument(
            '--disable',
            dest='enabled',
            action='store_false',
            help='Disable user',
        )
        return parser

    def get_data(self, parsed_args):
        self.log.debug('get_data(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity
        if parsed_args.tenant:
            tenant_id = utils.find_resource(
                identity_client.tenants, parsed_args.tenant).id
        else:
            tenant_id = None
        user = identity_client.users.create(
            parsed_args.name,
            parsed_args.password,
            parsed_args.email,
            tenant_id=tenant_id,
            enabled=parsed_args.enabled,
        )

        info = {}
        info.update(user._info)
        return zip(*sorted(info.iteritems()))


class DeleteUser(command.OpenStackCommand):
    """Delete user command"""

    api = 'identity'
    log = logging.getLogger(__name__ + '.DeleteUser')

    def get_parser(self, prog_name):
        parser = super(DeleteUser, self).get_parser(prog_name)
        parser.add_argument(
            'user',
            metavar='<user>',
            help='Name or ID of user to delete',
        )
        return parser

    def run(self, parsed_args):
        self.log.debug('run(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity
        user = utils.find_resource(
            identity_client.users, parsed_args.user)
        identity_client.users.delete(user.id)
        return


class ListUser(command.OpenStackCommand, lister.Lister):
    """List user command"""

    api = 'identity'
    log = logging.getLogger(__name__ + '.ListUser')

    def get_parser(self, prog_name):
        parser = super(ListUser, self).get_parser(prog_name)
        parser.add_argument(
            '--tenant',
            metavar='<tenant>',
            help='Name or ID of tenant to filter users',
        )
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help='Additional fields are listed in output',
        )
        return parser

    def get_data(self, parsed_args):
        self.log.debug('get_data(%s)' % parsed_args)
        if parsed_args.long:
            columns = ('ID', 'Name', 'TenantId', 'Email', 'Enabled')
        else:
            columns = ('ID', 'Name')
        data = self.app.client_manager.identity.users.list()
        return (columns,
                (utils.get_item_properties(
                    s, columns,
                    formatters={},
                ) for s in data),
               )


class SetUser(command.OpenStackCommand):
    """Set user command"""

    api = 'identity'
    log = logging.getLogger(__name__ + '.SetUser')

    def get_parser(self, prog_name):
        parser = super(SetUser, self).get_parser(prog_name)
        parser.add_argument(
            'user',
            metavar='<user>',
            help='Name or ID of user to change',
        )
        parser.add_argument(
            '--password',
            metavar='<user-password>',
            help='New user password',
        )
        parser.add_argument(
            '--email',
            metavar='<user-email>',
            help='New user email address',
        )
        parser.add_argument(
            '--tenant',
            metavar='<tenant>',
            help='New default tenant name or ID',
        )
        enable_group = parser.add_mutually_exclusive_group()
        enable_group.add_argument(
            '--enable',
            dest='enabled',
            action='store_true',
            default=True,
            help='Enable user (default)',
        )
        enable_group.add_argument(
            '--disable',
            dest='enabled',
            action='store_false',
            help='Disable user',
        )
        return parser

    def run(self, parsed_args):
        self.log.debug('run(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity
        user = utils.find_resource(
            identity_client.users, parsed_args.user)
        kwargs = {}
        if parsed_args.name:
            kwargs['name'] = parsed_args.name
        if parsed_args.email:
            kwargs['email'] = parsed_args.email
        if parsed_args.tenant:
            tenant_id = utils.find_resource(
                identity_client.tenants, parsed_args.tenant).id
            kwargs['tenantId'] = tenant_id
        if 'enabled' in parsed_args:
            kwargs['enabled'] = parsed_args.enabled

        if not len(kwargs):
            stdout.write("User not updated, no arguments present")
            return
        identity_client.users.delete(user.id)
        return


class ShowUser(command.OpenStackCommand, show.ShowOne):
    """Show user command"""

    api = 'identity'
    log = logging.getLogger(__name__ + '.ShowUser')

    def get_parser(self, prog_name):
        parser = super(ShowUser, self).get_parser(prog_name)
        parser.add_argument(
            'user',
            metavar='<user>',
            help='Name or ID of user to display',
        )
        return parser

    def get_data(self, parsed_args):
        self.log.debug('get_data(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity
        user = utils.find_resource(
            identity_client.users, parsed_args.user)

        info = {}
        info.update(user._info)
        return zip(*sorted(info.iteritems()))
