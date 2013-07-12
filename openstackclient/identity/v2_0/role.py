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

"""Role action implementations"""

import logging

from cliff import command
from cliff import lister
from cliff import show

from openstackclient.common import utils


class AddRole(show.ShowOne):
    """Add role to tenant:user"""

    log = logging.getLogger(__name__ + '.AddRole')

    def get_parser(self, prog_name):
        parser = super(AddRole, self).get_parser(prog_name)
        parser.add_argument(
            'role',
            metavar='<role>',
            help='Role name or ID to add to user')
        parser.add_argument(
            '--tenant',
            metavar='<tenant>',
            required=True,
            help='Name or ID of tenant to include')
        parser.add_argument(
            '--user',
            metavar='<user>',
            required=True,
            help='Name or ID of user to include')
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity
        role = utils.find_resource(identity_client.roles, parsed_args.role)
        tenant = utils.find_resource(identity_client.tenants,
                                     parsed_args.tenant)
        user = utils.find_resource(identity_client.users, parsed_args.user)
        role = identity_client.roles.add_user_role(
            user,
            role,
            tenant)

        info = {}
        info.update(role._info)
        return zip(*sorted(info.iteritems()))


class CreateRole(show.ShowOne):
    """Create new role"""

    log = logging.getLogger(__name__ + '.CreateRole')

    def get_parser(self, prog_name):
        parser = super(CreateRole, self).get_parser(prog_name)
        parser.add_argument(
            'role_name',
            metavar='<role-name>',
            help='New role name')
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity
        role = identity_client.roles.create(parsed_args.role_name)

        info = {}
        info.update(role._info)
        return zip(*sorted(info.iteritems()))


class DeleteRole(command.Command):
    """Delete existing role"""

    log = logging.getLogger(__name__ + '.DeleteRole')

    def get_parser(self, prog_name):
        parser = super(DeleteRole, self).get_parser(prog_name)
        parser.add_argument(
            'role',
            metavar='<role>',
            help='Name or ID of role to delete')
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity
        role = utils.find_resource(identity_client.roles, parsed_args.role)
        identity_client.roles.delete(role.id)
        return


class ListRole(lister.Lister):
    """List roles"""

    log = logging.getLogger(__name__ + '.ListRole')

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        columns = ('ID', 'Name')
        data = self.app.client_manager.identity.roles.list()
        return (columns,
                (utils.get_item_properties(
                    s, columns,
                    formatters={},
                ) for s in data))


class ListUserRole(lister.Lister):
    """List user-role assignments"""

    log = logging.getLogger(__name__ + '.ListUserRole')

    def get_parser(self, prog_name):
        parser = super(ListUserRole, self).get_parser(prog_name)
        parser.add_argument(
            'user',
            metavar='<user>',
            nargs='?',
            help='Name or ID of user to include')
        parser.add_argument(
            '--tenant',
            metavar='<tenant>',
            help='Name or ID of tenant to include')
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        columns = ('ID', 'Name', 'Tenant ID', 'User ID')
        identity_client = self.app.client_manager.identity

        # user-only roles are not supported in KSL so we are
        # required to have a user and tenant; default to the
        # values used for authentication if not specified
        if not parsed_args.tenant:
            parsed_args.tenant = identity_client.auth_tenant_id
        if not parsed_args.user:
            parsed_args.user = identity_client.auth_user_id

        tenant = utils.find_resource(identity_client.tenants,
                                     parsed_args.tenant)
        user = utils.find_resource(identity_client.users, parsed_args.user)

        data = identity_client.roles.roles_for_user(user.id, tenant.id)

        # Add the names to the output even though they will be constant
        for role in data:
            role.user_id = user.name
            role.tenant_id = tenant.name

        return (columns,
                (utils.get_item_properties(
                    s, columns,
                    formatters={},
                ) for s in data))


class RemoveRole(command.Command):
    """Remove role from tenant:user"""

    log = logging.getLogger(__name__ + '.RemoveRole')

    def get_parser(self, prog_name):
        parser = super(RemoveRole, self).get_parser(prog_name)
        parser.add_argument(
            'role',
            metavar='<role>',
            help='Role name or ID to remove from user')
        parser.add_argument(
            '--tenant',
            metavar='<tenant>',
            required=True,
            help='Name or ID of tenant')
        parser.add_argument(
            '--user',
            metavar='<user>',
            required=True,
            help='Name or ID of user')
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity
        role = utils.find_resource(identity_client.roles, parsed_args.role)
        tenant = utils.find_resource(identity_client.tenants,
                                     parsed_args.tenant)
        user = utils.find_resource(identity_client.users, parsed_args.user)
        identity_client.roles.remove_user_role(
            user.id,
            role.id,
            tenant.id)


class ShowRole(show.ShowOne):
    """Show single role"""

    log = logging.getLogger(__name__ + '.ShowRole')

    def get_parser(self, prog_name):
        parser = super(ShowRole, self).get_parser(prog_name)
        parser.add_argument(
            'role',
            metavar='<role>',
            help='Name or ID of role to display')
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity
        role = utils.find_resource(identity_client.roles, parsed_args.role)

        info = {}
        info.update(role._info)
        return zip(*sorted(info.iteritems()))
