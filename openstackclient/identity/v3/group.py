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
from keystoneclient import exceptions as ksc_exc

from openstackclient.common import utils
from openstackclient.i18n import _  # noqa
from openstackclient.identity import common


class AddUserToGroup(command.Command):
    """Add user to group"""

    log = logging.getLogger(__name__ + '.AddUserToGroup')

    def get_parser(self, prog_name):
        parser = super(AddUserToGroup, self).get_parser(prog_name)
        parser.add_argument(
            'group',
            metavar='<group>',
            help='Group to contain <user> (name or ID)',
        )
        parser.add_argument(
            'user',
            metavar='<user>',
            help='User to add to <group> (name or ID)',
        )
        common.add_group_domain_option_to_parser(parser)
        common.add_user_domain_option_to_parser(parser)
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        user_id = common.find_user(identity_client,
                                   parsed_args.user,
                                   parsed_args.user_domain).id
        group_id = common.find_group(identity_client,
                                     parsed_args.group,
                                     parsed_args.group_domain).id

        try:
            identity_client.users.add_to_group(user_id, group_id)
        except Exception:
            sys.stderr.write("%s not added to group %s\n" %
                             (parsed_args.user, parsed_args.group))
        else:
            sys.stdout.write("%s added to group %s\n" %
                             (parsed_args.user, parsed_args.group))


class CheckUserInGroup(command.Command):
    """Check user membership in group"""

    log = logging.getLogger(__name__ + '.CheckUserInGroup')

    def get_parser(self, prog_name):
        parser = super(CheckUserInGroup, self).get_parser(prog_name)
        parser.add_argument(
            'group',
            metavar='<group>',
            help='Group to check (name or ID)',
        )
        parser.add_argument(
            'user',
            metavar='<user>',
            help='User to check (name or ID)',
        )
        common.add_group_domain_option_to_parser(parser)
        common.add_user_domain_option_to_parser(parser)
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        user_id = common.find_user(identity_client,
                                   parsed_args.user,
                                   parsed_args.user_domain).id
        group_id = common.find_group(identity_client,
                                     parsed_args.group,
                                     parsed_args.group_domain).id

        try:
            identity_client.users.check_in_group(user_id, group_id)
        except Exception:
            sys.stderr.write("%s not in group %s\n" %
                             (parsed_args.user, parsed_args.group))
        else:
            sys.stdout.write("%s in group %s\n" %
                             (parsed_args.user, parsed_args.group))


class CreateGroup(show.ShowOne):
    """Create new group"""

    log = logging.getLogger(__name__ + '.CreateGroup')

    def get_parser(self, prog_name):
        parser = super(CreateGroup, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<group-name>',
            help='New group name',
        )
        parser.add_argument(
            '--domain',
            metavar='<domain>',
            help='Domain to contain new group (name or ID)',
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help='New group description',
        )
        parser.add_argument(
            '--or-show',
            action='store_true',
            help=_('Return existing group'),
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        domain = None
        if parsed_args.domain:
            domain = common.find_domain(identity_client,
                                        parsed_args.domain).id

        try:
            group = identity_client.groups.create(
                name=parsed_args.name,
                domain=domain,
                description=parsed_args.description)
        except ksc_exc.Conflict as e:
            if parsed_args.or_show:
                group = utils.find_resource(identity_client.groups,
                                            parsed_args.name,
                                            domain_id=domain)
                self.log.info('Returning existing group %s', group.name)
            else:
                raise e

        group._info.pop('links')
        return zip(*sorted(six.iteritems(group._info)))


class DeleteGroup(command.Command):
    """Delete group(s)"""

    log = logging.getLogger(__name__ + '.DeleteGroup')

    def get_parser(self, prog_name):
        parser = super(DeleteGroup, self).get_parser(prog_name)
        parser.add_argument(
            'groups',
            metavar='<group>',
            nargs="+",
            help='Group(s) to delete (name or ID)')
        parser.add_argument(
            '--domain',
            metavar='<domain>',
            help='Domain containing group(s) (name or ID)',
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        for group in parsed_args.groups:
            group_obj = common.find_group(identity_client,
                                          group,
                                          parsed_args.domain)
            identity_client.groups.delete(group_obj.id)
        return


class ListGroup(lister.Lister):
    """List groups"""

    log = logging.getLogger(__name__ + '.ListGroup')

    def get_parser(self, prog_name):
        parser = super(ListGroup, self).get_parser(prog_name)
        parser.add_argument(
            '--domain',
            metavar='<domain>',
            help='Filter group list by <domain> (name or ID)',
        )
        parser.add_argument(
            '--user',
            metavar='<user>',
            help='Filter group list by <user> (name or ID)',
        )
        common.add_user_domain_option_to_parser(parser)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help='List additional fields in output',
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        domain = None
        if parsed_args.domain:
            domain = common.find_domain(identity_client,
                                        parsed_args.domain).id

        if parsed_args.user:
            user = common.find_user(
                identity_client,
                parsed_args.user,
                parsed_args.user_domain,
            ).id
        else:
            user = None

        # List groups
        if parsed_args.long:
            columns = ('ID', 'Name', 'Domain ID', 'Description')
        else:
            columns = ('ID', 'Name')
        data = identity_client.groups.list(
            domain=domain,
            user=user,
        )

        return (
            columns,
            (utils.get_item_properties(
                s, columns,
                formatters={},
            ) for s in data)
        )


class RemoveUserFromGroup(command.Command):
    """Remove user from group"""

    log = logging.getLogger(__name__ + '.RemoveUserFromGroup')

    def get_parser(self, prog_name):
        parser = super(RemoveUserFromGroup, self).get_parser(prog_name)
        parser.add_argument(
            'group',
            metavar='<group>',
            help='Group containing <user> (name or ID)',
        )
        parser.add_argument(
            'user',
            metavar='<user>',
            help='User to remove from <group> (name or ID)',
        )
        common.add_group_domain_option_to_parser(parser)
        common.add_user_domain_option_to_parser(parser)
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        user_id = common.find_user(identity_client,
                                   parsed_args.user,
                                   parsed_args.user_domain).id
        group_id = common.find_group(identity_client,
                                     parsed_args.group,
                                     parsed_args.group_domain).id

        try:
            identity_client.users.remove_from_group(user_id, group_id)
        except Exception:
            sys.stderr.write("%s not removed from group %s\n" %
                             (parsed_args.user, parsed_args.group))
        else:
            sys.stdout.write("%s removed from group %s\n" %
                             (parsed_args.user, parsed_args.group))


class SetGroup(command.Command):
    """Set group properties"""

    log = logging.getLogger(__name__ + '.SetGroup')

    def get_parser(self, prog_name):
        parser = super(SetGroup, self).get_parser(prog_name)
        parser.add_argument(
            'group',
            metavar='<group>',
            help='Group to modify (name or ID)')
        parser.add_argument(
            '--domain',
            metavar='<domain>',
            help='Domain containing <group> (name or ID)',
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            help='New group name')
        parser.add_argument(
            '--description',
            metavar='<description>',
            help='New group description')
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        group = common.find_group(identity_client, parsed_args.group,
                                  parsed_args.domain)
        kwargs = {}
        if parsed_args.name:
            kwargs['name'] = parsed_args.name
        if parsed_args.description:
            kwargs['description'] = parsed_args.description

        if not len(kwargs):
            sys.stderr.write("Group not updated, no arguments present")
            return
        identity_client.groups.update(group.id, **kwargs)
        return


class ShowGroup(show.ShowOne):
    """Display group details"""

    log = logging.getLogger(__name__ + '.ShowGroup')

    def get_parser(self, prog_name):
        parser = super(ShowGroup, self).get_parser(prog_name)
        parser.add_argument(
            'group',
            metavar='<group>',
            help='Group to display (name or ID)',
        )
        parser.add_argument(
            '--domain',
            metavar='<domain>',
            help='Domain containing <group> (name or ID)',
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        group = common.find_group(identity_client,
                                  parsed_args.group,
                                  domain_name_or_id=parsed_args.domain)

        group._info.pop('links')
        return zip(*sorted(six.iteritems(group._info)))
