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

"""Identity v3 Role action implementations"""

import logging
import sys

from cliff import command
from cliff import lister
from cliff import show

from openstackclient.common import utils


class AddRole(command.Command):
    """Add role command"""

    api = 'identity'
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
            help='Name or ID of user to assign a role',
        )
        user_or_group.add_argument(
            '--group',
            metavar='<group>',
            help='Name or ID of group to assign a role',
        )
        domain_or_project = parser.add_mutually_exclusive_group()
        domain_or_project.add_argument(
            '--domain',
            metavar='<domain>',
            help='Name or ID of domain where user or group resides',
        )
        domain_or_project.add_argument(
            '--project',
            metavar='<project>',
            help='Name or ID of project where user or group resides',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity

        if (not parsed_args.user and not parsed_args.domain
                and not parsed_args.group and not parsed_args.project):
            sys.stdout.write("Role not updated, no arguments present \n")
            return

        role_id = utils.find_resource(identity_client.roles,
                                      parsed_args.role).id

        if (parsed_args.user and parsed_args.domain):
            user = utils.find_resource(identity_client.users,
                                       parsed_args.user)
            domain = utils.find_resource(identity_client.domains,
                                         parsed_args.domain)
            identity_client.roles.grant(role_id, user=user, domain=domain)
            return
        elif (parsed_args.user and parsed_args.project):
            user = utils.find_resource(identity_client.users,
                                       parsed_args.user)
            project = utils.find_resource(identity_client.projects,
                                          parsed_args.project)
            identity_client.roles.grant(role_id, user=user, project=project)
            return
        elif (parsed_args.group and parsed_args.project):
            group = utils.find_resource(identity_client.group,
                                        parsed_args.group)
            project = utils.find_resource(identity_client.projects,
                                          parsed_args.project)
            identity_client.roles.grant(role_id, group=group, project=project)
            return
        elif (parsed_args.group and parsed_args.domain):
            group = utils.find_resource(identity_client.group,
                                        parsed_args.group)
            domain = utils.find_resource(identity_client.domains,
                                         parsed_args.domain)
            identity_client.roles.grant(role_id, group=group, domain=domain)
            return
        else:
            return


class CreateRole(show.ShowOne):
    """Create new role"""

    api = 'identity'
    log = logging.getLogger(__name__ + '.CreateRole')

    def get_parser(self, prog_name):
        parser = super(CreateRole, self).get_parser(prog_name)
        parser.add_argument(
            'role-name',
            metavar='<role-name>',
            help='New role name')
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity
        role = identity_client.roles.create(parsed_args.role_name)

        return zip(*sorted(role._info.iteritems()))


class DeleteRole(command.Command):
    """Delete existing role"""

    api = 'identity'
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
        role_id = utils.find_resource(identity_client.roles,
                                      parsed_args.role)
        identity_client.roles.delete(role_id)
        return


class ListRole(lister.Lister):
    """List roles"""

    api = 'identity'
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


class SetRole(command.Command):
    """Set role command"""

    api = 'identity'
    log = logging.getLogger(__name__ + '.SetRole')

    def get_parser(self, prog_name):
        parser = super(SetRole, self).get_parser(prog_name)
        parser.add_argument(
            'role',
            metavar='<role>',
            help='Name or ID of role to change',
        )
        parser.add_argument(
            '--name',
            metavar='<new-role-name>',
            help='New role name',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity
        role_id = utils.find_resource(identity_client.roles,
                                      parsed_args.role)

        if not parsed_args.name:
            sys.stdout.write("Role not updated, no arguments present")
            return

        identity_client.roles.update(role_id, parsed_args.name)
        return


class ShowRole(show.ShowOne):
    """Show single role"""

    api = 'identity'
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
        role = utils.find_resource(identity_client.roles,
                                   parsed_args.role)

        return zip(*sorted(role._info.iteritems()))
