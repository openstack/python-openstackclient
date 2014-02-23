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

"""Group action implementations"""

import logging
import six
import sys

from cliff import command
from cliff import lister
from cliff import show

from openstackclient.common import utils


class AddUserToGroup(command.Command):
    """Add user to group"""

    log = logging.getLogger(__name__ + '.AddUserToGroup')

    def get_parser(self, prog_name):
        parser = super(AddUserToGroup, self).get_parser(prog_name)
        parser.add_argument(
            'group',
            metavar='<group>',
            help='Group name or ID that user will be added to',
        )
        parser.add_argument(
            'user',
            metavar='<user>',
            help='User name or ID to add to group',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity

        user_id = utils.find_resource(identity_client.users,
                                      parsed_args.user).id
        group_id = utils.find_resource(identity_client.groups,
                                       parsed_args.group).id

        try:
            identity_client.users.add_to_group(user_id, group_id)
        except Exception:
            sys.stderr.write("%s not added to group %s\n" %
                             (parsed_args.user, parsed_args.group))
        else:
            sys.stdout.write("%s added to group %s\n" %
                             (parsed_args.user, parsed_args.group))


class CheckUserInGroup(command.Command):
    """Checks that user is in a specific group"""

    log = logging.getLogger(__name__ + '.CheckUserInGroup')

    def get_parser(self, prog_name):
        parser = super(CheckUserInGroup, self).get_parser(prog_name)
        parser.add_argument(
            'group',
            metavar='<group>',
            help='Group name or ID that user will be added to',
        )
        parser.add_argument(
            'user',
            metavar='<user>',
            help='User name or ID to add to group',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity

        user_id = utils.find_resource(identity_client.users,
                                      parsed_args.user).id
        group_id = utils.find_resource(identity_client.groups,
                                       parsed_args.group).id

        try:
            identity_client.users.check_in_group(user_id, group_id)
        except Exception:
            sys.stderr.write("%s not in group %s\n" %
                             (parsed_args.user, parsed_args.group))
        else:
            sys.stdout.write("%s in group %s\n" %
                             (parsed_args.user, parsed_args.group))


class CreateGroup(show.ShowOne):
    """Create group command"""

    log = logging.getLogger(__name__ + '.CreateGroup')

    def get_parser(self, prog_name):
        parser = super(CreateGroup, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<group-name>',
            help='New group name')
        parser.add_argument(
            '--description',
            metavar='<group-description>',
            help='New group description')
        parser.add_argument(
            '--domain',
            metavar='<group-domain>',
            help='References the domain ID or name which owns the group')

        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity
        if parsed_args.domain:
            domain = utils.find_resource(identity_client.domains,
                                         parsed_args.domain).id
        else:
            domain = None
        group = identity_client.groups.create(
            parsed_args.name,
            domain=domain,
            description=parsed_args.description)

        info = {}
        info.update(group._info)
        return zip(*sorted(six.iteritems(info)))


class DeleteGroup(command.Command):
    """Delete group command"""

    log = logging.getLogger(__name__ + '.DeleteGroup')

    def get_parser(self, prog_name):
        parser = super(DeleteGroup, self).get_parser(prog_name)
        parser.add_argument(
            'group',
            metavar='<group>',
            help='Name or ID of group to delete')
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity
        group = utils.find_resource(identity_client.groups, parsed_args.group)
        identity_client.groups.delete(group.id)
        return


class ListGroup(lister.Lister):
    """List groups and optionally roles assigned to groups"""

    log = logging.getLogger(__name__ + '.ListGroup')

    def get_parser(self, prog_name):
        parser = super(ListGroup, self).get_parser(prog_name)
        parser.add_argument(
            'group',
            metavar='<group>',
            nargs='?',
            help='Name or ID of group to list [required with --role]',
        )
        parser.add_argument(
            '--role',
            action='store_true',
            default=False,
            help='List the roles assigned to <group>',
        )
        domain_or_project = parser.add_mutually_exclusive_group()
        domain_or_project.add_argument(
            '--domain',
            metavar='<domain>',
            help='Filter list by <domain> [Only valid with --role]',
        )
        domain_or_project.add_argument(
            '--project',
            metavar='<project>',
            help='Filter list by <project> [Only valid with --role]',
        )
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help='List additional fields in output',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity

        if parsed_args.role:
            # List roles belonging to group

            # Group is required here, bail if it is not supplied
            if not parsed_args.group:
                sys.stderr.write('Error: Group must be specified')
                # TODO(dtroyer): This lists the commands...I want it to
                # show the help for _this_ command.
                self.app.DeferredHelpAction(
                    self.app.parser,
                    self.app.parser,
                    None,
                    None,
                )
                return ([], [])

            group = utils.find_resource(
                identity_client.groups,
                parsed_args.group,
            )

            if parsed_args.domain:
                columns = ('ID', 'Name', 'Domain', 'Group')
                domain = utils.find_resource(
                    identity_client.domains,
                    parsed_args.domain,
                )
                data = identity_client.roles.list(
                    group=group,
                    domain=domain,
                )
                for group_role in data:
                    group_role.group = group.name
                    group_role.domain = domain.name
            elif parsed_args.project:
                columns = ('ID', 'Name', 'Project', 'Group')
                project = utils.find_resource(
                    identity_client.projects,
                    parsed_args.project,
                )
                data = identity_client.roles.list(
                    group=group,
                    project=project,
                )
                for group_role in data:
                    group_role.group = group.name
                    group_role.project = project.name
            else:
                # TODO(dtroyer): raise exception here, this really is an error
                sys.stderr.write("Error: Must specify --domain or --project "
                                 "with --role\n")
                return ([], [])
        else:
            # List groups
            if parsed_args.long:
                columns = ('ID', 'Name', 'Domain ID', 'Description')
            else:
                columns = ('ID', 'Name')
            data = identity_client.groups.list()

        return (columns,
                (utils.get_item_properties(
                    s, columns,
                    formatters={},
                ) for s in data))


class RemoveUserFromGroup(command.Command):
    """Remove user to group"""

    log = logging.getLogger(__name__ + '.RemoveUserFromGroup')

    def get_parser(self, prog_name):
        parser = super(RemoveUserFromGroup, self).get_parser(prog_name)
        parser.add_argument(
            'group',
            metavar='<group>',
            help='Group name or ID that user will be removed from',
        )
        parser.add_argument(
            'user',
            metavar='<user>',
            help='User name or ID to remove from group',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity

        user_id = utils.find_resource(identity_client.users,
                                      parsed_args.user).id
        group_id = utils.find_resource(identity_client.groups,
                                       parsed_args.group).id

        try:
            identity_client.users.remove_from_group(user_id, group_id)
        except Exception:
            sys.stderr.write("%s not removed from group %s\n" %
                             (parsed_args.user, parsed_args.group))
        else:
            sys.stdout.write("%s removed from group %s\n" %
                             (parsed_args.user, parsed_args.group))


class SetGroup(command.Command):
    """Set group command"""

    log = logging.getLogger(__name__ + '.SetGroup')

    def get_parser(self, prog_name):
        parser = super(SetGroup, self).get_parser(prog_name)
        parser.add_argument(
            'group',
            metavar='<group>',
            help='Name or ID of group to change')
        parser.add_argument(
            '--name',
            metavar='<new-group-name>',
            help='New group name')
        parser.add_argument(
            '--domain',
            metavar='<group-domain>',
            help='New domain name or ID that will now own the group')
        parser.add_argument(
            '--description',
            metavar='<group-description>',
            help='New group description')
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity
        group = utils.find_resource(identity_client.groups, parsed_args.group)
        kwargs = {}
        if parsed_args.name:
            kwargs['name'] = parsed_args.name
        if parsed_args.description:
            kwargs['description'] = parsed_args.description
        if parsed_args.domain:
            domain = utils.find_resource(
                identity_client.domains, parsed_args.domain).id
            kwargs['domain'] = domain

        if not len(kwargs):
            sys.stderr.write("Group not updated, no arguments present")
            return
        identity_client.groups.update(group.id, **kwargs)
        return


class ShowGroup(show.ShowOne):
    """Show group command"""

    log = logging.getLogger(__name__ + '.ShowGroup')

    def get_parser(self, prog_name):
        parser = super(ShowGroup, self).get_parser(prog_name)
        parser.add_argument(
            'group',
            metavar='<group>',
            help='Name or ID of group to display')
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity
        group = utils.find_resource(identity_client.groups, parsed_args.group)

        info = {}
        info.update(group._info)
        return zip(*sorted(six.iteritems(info)))
