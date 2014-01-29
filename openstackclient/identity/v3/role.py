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

"""Identity v3 Role action implementations"""

import logging
import six
import sys

from cliff import command
from cliff import lister
from cliff import show

from openstackclient.common import utils


class AddRole(command.Command):
    """Adds a role to a user or group on a domain or project"""

    log = logging.getLogger(__name__ + '.AddRole')

    def get_parser(self, prog_name):
        parser = super(AddRole, self).get_parser(prog_name)
        parser.add_argument(
            'role',
            metavar='<role>',
            help='Name or ID of role to add',
        )
        user_or_group = parser.add_mutually_exclusive_group()
        user_or_group.add_argument(
            '--user',
            metavar='<user>',
            help='Name or ID of user to add a role',
        )
        user_or_group.add_argument(
            '--group',
            metavar='<group>',
            help='Name or ID of group to add a role',
        )
        domain_or_project = parser.add_mutually_exclusive_group()
        domain_or_project.add_argument(
            '--domain',
            metavar='<domain>',
            help='Name or ID of domain associated with user or group',
        )
        domain_or_project.add_argument(
            '--project',
            metavar='<project>',
            help='Name or ID of project associated with user or group',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)', parsed_args)
        identity_client = self.app.client_manager.identity

        if (not parsed_args.user and not parsed_args.domain
                and not parsed_args.group and not parsed_args.project):
            return

        role = utils.find_resource(
            identity_client.roles,
            parsed_args.role,
        )

        if parsed_args.user and parsed_args.domain:
            user = utils.find_resource(
                identity_client.users,
                parsed_args.user,
            )
            domain = utils.find_resource(
                identity_client.domains,
                parsed_args.domain,
            )
            identity_client.roles.grant(
                role.id,
                user=user.id,
                domain=domain.id,
            )
        elif parsed_args.user and parsed_args.project:
            user = utils.find_resource(
                identity_client.users,
                parsed_args.user,
            )
            project = utils.find_resource(
                identity_client.projects,
                parsed_args.project,
            )
            identity_client.roles.grant(
                role.id,
                user=user.id,
                project=project.id,
            )
        elif parsed_args.group and parsed_args.domain:
            group = utils.find_resource(
                identity_client.groups,
                parsed_args.group,
            )
            domain = utils.find_resource(
                identity_client.domains,
                parsed_args.domain,
            )
            identity_client.roles.grant(
                role.id,
                group=group.id,
                domain=domain.id,
            )
        elif parsed_args.group and parsed_args.project:
            group = utils.find_resource(
                identity_client.groups,
                parsed_args.group,
            )
            project = utils.find_resource(
                identity_client.projects,
                parsed_args.project,
            )
            identity_client.roles.grant(
                role.id,
                group=group.id,
                project=project.id,
            )
        else:
            sys.stderr.write("Role not added, incorrect set of arguments \
            provided. See openstack --help for more details\n")
        return


class CreateRole(show.ShowOne):
    """Create new role"""

    log = logging.getLogger(__name__ + '.CreateRole')

    def get_parser(self, prog_name):
        parser = super(CreateRole, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<role-name>',
            help='New role name',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)', parsed_args)
        identity_client = self.app.client_manager.identity

        role = identity_client.roles.create(name=parsed_args.name)

        return zip(*sorted(six.iteritems(role._info)))


class DeleteRole(command.Command):
    """Delete existing role"""

    log = logging.getLogger(__name__ + '.DeleteRole')

    def get_parser(self, prog_name):
        parser = super(DeleteRole, self).get_parser(prog_name)
        parser.add_argument(
            'role',
            metavar='<role>',
            help='Name or ID of role to delete',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)', parsed_args)
        identity_client = self.app.client_manager.identity

        role = utils.find_resource(
            identity_client.roles,
            parsed_args.role,
        )

        identity_client.roles.delete(role.id)
        return


class ListRole(lister.Lister):
    """List roles"""

    log = logging.getLogger(__name__ + '.ListRole')

    def get_parser(self, prog_name):
        parser = super(ListRole, self).get_parser(prog_name)
        domain_or_project = parser.add_mutually_exclusive_group()
        domain_or_project.add_argument(
            '--domain',
            metavar='<domain>',
            help='Filter role list by <domain>',
        )
        domain_or_project.add_argument(
            '--project',
            metavar='<project>',
            help='Filter role list by <project>',
        )
        user_or_group = parser.add_mutually_exclusive_group()
        user_or_group.add_argument(
            '--user',
            metavar='<user>',
            help='Name or ID of user to list roles asssigned to',
        )
        user_or_group.add_argument(
            '--group',
            metavar='<group>',
            help='Name or ID of group to list roles asssigned to',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity

        if parsed_args.user:
            user = utils.find_resource(
                identity_client.users,
                parsed_args.user,
            )
        elif parsed_args.group:
            group = utils.find_resource(
                identity_client.groups,
                parsed_args.group,
            )

        if parsed_args.domain:
            domain = utils.find_resource(
                identity_client.domains,
                parsed_args.domain,
            )
        elif parsed_args.project:
            project = utils.find_resource(
                identity_client.projects,
                parsed_args.project,
            )

        # no user or group specified, list all roles in the system
        if not parsed_args.user and not parsed_args.group:
            columns = ('ID', 'Name')
            data = identity_client.roles.list()
        elif parsed_args.user and parsed_args.domain:
            columns = ('ID', 'Name', 'Domain', 'User')
            data = identity_client.roles.list(
                user=user,
                domain=domain,
            )
            for user_role in data:
                user_role.user = user.name
                user_role.domain = domain.name
        elif parsed_args.user and parsed_args.project:
            columns = ('ID', 'Name', 'Project', 'User')
            data = identity_client.roles.list(
                user=user,
                project=project,
            )
            for user_role in data:
                user_role.user = user.name
                user_role.project = project.name
        elif parsed_args.user:
            columns = ('ID', 'Name')
            data = identity_client.roles.list(
                user=user,
                domain='default',
            )
        elif parsed_args.group and parsed_args.domain:
            columns = ('ID', 'Name', 'Domain', 'Group')
            data = identity_client.roles.list(
                group=group,
                domain=domain,
            )
            for group_role in data:
                group_role.group = group.name
                group_role.domain = domain.name
        elif parsed_args.group and parsed_args.project:
            columns = ('ID', 'Name', 'Project', 'Group')
            data = identity_client.roles.list(
                group=group,
                project=project,
            )
            for group_role in data:
                group_role.group = group.name
                group_role.project = project.name
        else:
            sys.stderr.write("Error: If a user or group is specified, either "
                             "--domain or --project must also be specified to "
                             "list role grants.\n")
            return ([], [])

        return (columns,
                (utils.get_item_properties(
                    s, columns,
                    formatters={},
                ) for s in data))


class RemoveRole(command.Command):
    """Remove role command"""

    log = logging.getLogger(__name__ + '.RemoveRole')

    def get_parser(self, prog_name):
        parser = super(RemoveRole, self).get_parser(prog_name)
        parser.add_argument(
            'role',
            metavar='<role>',
            help='Name or ID of role to remove',
        )
        user_or_group = parser.add_mutually_exclusive_group()
        user_or_group.add_argument(
            '--user',
            metavar='<user>',
            help='Name or ID of user to remove a role',
        )
        user_or_group.add_argument(
            '--group',
            metavar='<group>',
            help='Name or ID of group to remove a role',
        )
        domain_or_project = parser.add_mutually_exclusive_group()
        domain_or_project.add_argument(
            '--domain',
            metavar='<domain>',
            help='Name or ID of domain associated with user or group',
        )
        domain_or_project.add_argument(
            '--project',
            metavar='<project>',
            help='Name or ID of project associated with user or group',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)', parsed_args)
        identity_client = self.app.client_manager.identity

        if (not parsed_args.user and not parsed_args.domain
                and not parsed_args.group and not parsed_args.project):
            return

        role = utils.find_resource(
            identity_client.roles,
            parsed_args.role,
        )

        if parsed_args.user and parsed_args.domain:
            user = utils.find_resource(
                identity_client.users,
                parsed_args.user,
            )
            domain = utils.find_resource(
                identity_client.domains,
                parsed_args.domain,
            )
            identity_client.roles.revoke(
                role.id,
                user=user.id,
                domain=domain.id,
            )
        elif parsed_args.user and parsed_args.project:
            user = utils.find_resource(
                identity_client.users,
                parsed_args.user,
            )
            project = utils.find_resource(
                identity_client.projects,
                parsed_args.project,
            )
            identity_client.roles.revoke(
                role.id,
                user=user.id,
                project=project.id,
            )
        elif parsed_args.group and parsed_args.domain:
            group = utils.find_resource(
                identity_client.groups,
                parsed_args.group,
            )
            domain = utils.find_resource(
                identity_client.domains,
                parsed_args.domain,
            )
            identity_client.roles.revoke(
                role.id,
                group=group.id,
                domain=domain.id,
            )
        elif parsed_args.group and parsed_args.project:
            group = utils.find_resource(
                identity_client.groups,
                parsed_args.group,
            )
            project = utils.find_resource(
                identity_client.projects,
                parsed_args.project,
            )
            identity_client.roles.revoke(
                role.id,
                group=group.id,
                project=project.id,
            )
        else:
            sys.stderr.write("Role not removed, incorrect set of arguments \
            provided. See openstack --help for more details\n")
        return


class SetRole(command.Command):
    """Set role command"""

    log = logging.getLogger(__name__ + '.SetRole')

    def get_parser(self, prog_name):
        parser = super(SetRole, self).get_parser(prog_name)
        parser.add_argument(
            'role',
            metavar='<role>',
            help='Name or ID of role to update',
        )
        parser.add_argument(
            '--name',
            metavar='<new-role-name>',
            help='New role name',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)', parsed_args)
        identity_client = self.app.client_manager.identity

        if not parsed_args.name:
            return

        role = utils.find_resource(
            identity_client.roles,
            parsed_args.role,
        )

        identity_client.roles.update(role.id, name=parsed_args.name)
        return


class ShowRole(show.ShowOne):
    """Show single role"""

    log = logging.getLogger(__name__ + '.ShowRole')

    def get_parser(self, prog_name):
        parser = super(ShowRole, self).get_parser(prog_name)
        parser.add_argument(
            'role',
            metavar='<role>',
            help='Name or ID of role to display',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)', parsed_args)
        identity_client = self.app.client_manager.identity

        role = utils.find_resource(
            identity_client.roles,
            parsed_args.role,
        )

        return zip(*sorted(six.iteritems(role._info)))
