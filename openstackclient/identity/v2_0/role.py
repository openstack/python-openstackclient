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

"""Identity v2 Role action implementations"""

import logging
import six

from cliff import command
from cliff import lister
from cliff import show
from keystoneclient import exceptions as ksc_exc

from openstackclient.common import exceptions
from openstackclient.common import utils
from openstackclient.i18n import _  # noqa


class AddRole(show.ShowOne):
    """Add role to project:user"""

    log = logging.getLogger(__name__ + '.AddRole')

    def get_parser(self, prog_name):
        parser = super(AddRole, self).get_parser(prog_name)
        parser.add_argument(
            'role',
            metavar='<role>',
            help=_('Role to add to <project>:<user> (name or ID)'),
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            required=True,
            help=_('Include <project> (name or ID)'),
        )
        parser.add_argument(
            '--user',
            metavar='<user>',
            required=True,
            help=_('Include <user> (name or ID)'),
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        role = utils.find_resource(identity_client.roles, parsed_args.role)
        project = utils.find_resource(
            identity_client.tenants,
            parsed_args.project,
        )
        user = utils.find_resource(identity_client.users, parsed_args.user)
        role = identity_client.roles.add_user_role(
            user.id,
            role.id,
            project.id,
        )

        info = {}
        info.update(role._info)
        return zip(*sorted(six.iteritems(info)))


class CreateRole(show.ShowOne):
    """Create new role"""

    log = logging.getLogger(__name__ + '.CreateRole')

    def get_parser(self, prog_name):
        parser = super(CreateRole, self).get_parser(prog_name)
        parser.add_argument(
            'role_name',
            metavar='<name>',
            help=_('New role name'),
        )
        parser.add_argument(
            '--or-show',
            action='store_true',
            help=_('Return existing role'),
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        try:
            role = identity_client.roles.create(parsed_args.role_name)
        except ksc_exc.Conflict as e:
            if parsed_args.or_show:
                role = utils.find_resource(
                    identity_client.roles,
                    parsed_args.role_name,
                )
                self.log.info('Returning existing role %s', role.name)
            else:
                raise e

        info = {}
        info.update(role._info)
        return zip(*sorted(six.iteritems(info)))


class DeleteRole(command.Command):
    """Delete role(s)"""

    log = logging.getLogger(__name__ + '.DeleteRole')

    def get_parser(self, prog_name):
        parser = super(DeleteRole, self).get_parser(prog_name)
        parser.add_argument(
            'roles',
            metavar='<role>',
            nargs="+",
            help=_('Role(s) to delete (name or ID)'),
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        for role in parsed_args.roles:
            role_obj = utils.find_resource(
                identity_client.roles,
                role,
            )
            identity_client.roles.delete(role_obj.id)
        return


class ListRole(lister.Lister):
    """List roles"""

    log = logging.getLogger(__name__ + '.ListRole')

    def get_parser(self, prog_name):
        parser = super(ListRole, self).get_parser(prog_name)
        parser.add_argument(
            '--project',
            metavar='<project>',
            help='Filter roles by <project> (name or ID)',
        )
        parser.add_argument(
            '--user',
            metavar='<user>',
            help='Filter roles by <user> (name or ID)',
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        auth_ref = self.app.client_manager.auth_ref

        # No user or project specified, list all roles in the system
        if not parsed_args.user and not parsed_args.project:
            columns = ('ID', 'Name')
            data = identity_client.roles.list()
        elif parsed_args.user and parsed_args.project:
            user = utils.find_resource(
                identity_client.users,
                parsed_args.user,
            )
            project = utils.find_resource(
                identity_client.projects,
                parsed_args.project,
            )
            data = identity_client.roles.roles_for_user(user.id, project.id)

        elif parsed_args.user:
            user = utils.find_resource(
                identity_client.users,
                parsed_args.user,
            )
            if self.app.client_manager.auth_ref:
                project = utils.find_resource(
                    identity_client.projects,
                    auth_ref.project_id
                )
            else:
                msg = _("Project must be specified")
                raise exceptions.CommandError(msg)
            data = identity_client.roles.roles_for_user(user.id, project.id)
        elif parsed_args.project:
            project = utils.find_resource(
                identity_client.projects,
                parsed_args.project,
            )
            if self.app.client_manager.auth_ref:
                user = utils.find_resource(
                    identity_client.users,
                    auth_ref.user_id
                )
            else:
                msg = _("User must be specified")
                raise exceptions.CommandError(msg)
            data = identity_client.roles.roles_for_user(user.id, project.id)

        if parsed_args.user or parsed_args.project:
            columns = ('ID', 'Name', 'Project', 'User')
            for user_role in data:
                user_role.user = user.name
                user_role.project = project.name

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
            help=_('User to list (name or ID)'),
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_('Filter users by <project> (name or ID)'),
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        auth_ref = self.app.client_manager.auth_ref

        # Project and user are required, if not included in command args
        # default to the values used for authentication.  For token-flow
        # authentication they must be included on the command line.
        if not parsed_args.project:
            if self.app.client_manager.auth_ref:
                parsed_args.project = auth_ref.project_id
            else:
                msg = _("Project must be specified")
                raise exceptions.CommandError(msg)
        if not parsed_args.user:
            if self.app.client_manager.auth_ref:
                parsed_args.user = auth_ref.user_id
            else:
                msg = _("User must be specified")
                raise exceptions.CommandError(msg)

        project = utils.find_resource(
            identity_client.tenants,
            parsed_args.project,
        )
        user = utils.find_resource(identity_client.users, parsed_args.user)

        data = identity_client.roles.roles_for_user(user.id, project.id)

        columns = (
            'ID',
            'Name',
            'Project',
            'User',
        )

        # Add the names to the output even though they will be constant
        for role in data:
            role.user = user.name
            role.project = project.name

        return (columns,
                (utils.get_item_properties(
                    s, columns,
                    formatters={},
                ) for s in data))


class RemoveRole(command.Command):
    """Remove role from project : user"""

    log = logging.getLogger(__name__ + '.RemoveRole')

    def get_parser(self, prog_name):
        parser = super(RemoveRole, self).get_parser(prog_name)
        parser.add_argument(
            'role',
            metavar='<role>',
            help=_('Role to remove (name or ID)'),
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            required=True,
            help=_('Include <project> (name or ID)'),
        )
        parser.add_argument(
            '--user',
            metavar='<user>',
            required=True,
            help=_('Include <user> (name or ID)'),
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        role = utils.find_resource(identity_client.roles, parsed_args.role)
        project = utils.find_resource(
            identity_client.tenants,
            parsed_args.project,
        )
        user = utils.find_resource(identity_client.users, parsed_args.user)
        identity_client.roles.remove_user_role(
            user.id,
            role.id,
            project.id)


class ShowRole(show.ShowOne):
    """Display role details"""

    log = logging.getLogger(__name__ + '.ShowRole')

    def get_parser(self, prog_name):
        parser = super(ShowRole, self).get_parser(prog_name)
        parser.add_argument(
            'role',
            metavar='<role>',
            help=_('Role to display (name or ID)'),
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        role = utils.find_resource(identity_client.roles, parsed_args.role)

        info = {}
        info.update(role._info)
        return zip(*sorted(six.iteritems(info)))
