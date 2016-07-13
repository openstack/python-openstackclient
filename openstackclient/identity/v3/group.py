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
import sys

from keystoneauth1 import exceptions as ks_exc
from osc_lib.command import command
from osc_lib import utils
import six

from openstackclient.i18n import _
from openstackclient.identity import common


LOG = logging.getLogger(__name__)


class AddUserToGroup(command.Command):
    """Add user to group"""

    def get_parser(self, prog_name):
        parser = super(AddUserToGroup, self).get_parser(prog_name)
        parser.add_argument(
            'group',
            metavar='<group>',
            help=_('Group to contain <user> (name or ID)'),
        )
        parser.add_argument(
            'user',
            metavar='<user>',
            help=_('User to add to <group> (name or ID)'),
        )
        common.add_group_domain_option_to_parser(parser)
        common.add_user_domain_option_to_parser(parser)
        return parser

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
            msg = _("%(user)s not added to group %(group)s\n") % {
                'user': parsed_args.user,
                'group': parsed_args.group,
            }
            sys.stderr.write(msg)
        else:
            msg = _("%(user)s added to group %(group)s\n") % {
                'user': parsed_args.user,
                'group': parsed_args.group,
            }
            sys.stdout.write(msg)


class CheckUserInGroup(command.Command):
    """Check user membership in group"""

    def get_parser(self, prog_name):
        parser = super(CheckUserInGroup, self).get_parser(prog_name)
        parser.add_argument(
            'group',
            metavar='<group>',
            help=_('Group to check (name or ID)'),
        )
        parser.add_argument(
            'user',
            metavar='<user>',
            help=_('User to check (name or ID)'),
        )
        common.add_group_domain_option_to_parser(parser)
        common.add_user_domain_option_to_parser(parser)
        return parser

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
            msg = _("%(user)s not in group %(group)s\n") % {
                'user': parsed_args.user,
                'group': parsed_args.group,
            }
            sys.stderr.write(msg)
        else:
            msg = _("%(user)s in group %(group)s\n") % {
                'user': parsed_args.user,
                'group': parsed_args.group,
            }
            sys.stdout.write(msg)


class CreateGroup(command.ShowOne):
    """Create new group"""

    def get_parser(self, prog_name):
        parser = super(CreateGroup, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<group-name>',
            help=_('New group name'),
        )
        parser.add_argument(
            '--domain',
            metavar='<domain>',
            help=_('Domain to contain new group (name or ID)'),
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('New group description'),
        )
        parser.add_argument(
            '--or-show',
            action='store_true',
            help=_('Return existing group'),
        )
        return parser

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
        except ks_exc.Conflict:
            if parsed_args.or_show:
                group = utils.find_resource(identity_client.groups,
                                            parsed_args.name,
                                            domain_id=domain)
                LOG.info(_('Returning existing group %s'), group.name)
            else:
                raise

        group._info.pop('links')
        return zip(*sorted(six.iteritems(group._info)))


class DeleteGroup(command.Command):
    """Delete group(s)"""

    def get_parser(self, prog_name):
        parser = super(DeleteGroup, self).get_parser(prog_name)
        parser.add_argument(
            'groups',
            metavar='<group>',
            nargs="+",
            help=_('Group(s) to delete (name or ID)'),
        )
        parser.add_argument(
            '--domain',
            metavar='<domain>',
            help=_('Domain containing group(s) (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        for group in parsed_args.groups:
            group_obj = common.find_group(identity_client,
                                          group,
                                          parsed_args.domain)
            identity_client.groups.delete(group_obj.id)


class ListGroup(command.Lister):
    """List groups"""

    def get_parser(self, prog_name):
        parser = super(ListGroup, self).get_parser(prog_name)
        parser.add_argument(
            '--domain',
            metavar='<domain>',
            help=_('Filter group list by <domain> (name or ID)'),
        )
        parser.add_argument(
            '--user',
            metavar='<user>',
            help=_('Filter group list by <user> (name or ID)'),
        )
        common.add_user_domain_option_to_parser(parser)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_('List additional fields in output'),
        )
        return parser

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

    def get_parser(self, prog_name):
        parser = super(RemoveUserFromGroup, self).get_parser(prog_name)
        parser.add_argument(
            'group',
            metavar='<group>',
            help=_('Group containing <user> (name or ID)'),
        )
        parser.add_argument(
            'user',
            metavar='<user>',
            help=_('User to remove from <group> (name or ID)'),
        )
        common.add_group_domain_option_to_parser(parser)
        common.add_user_domain_option_to_parser(parser)
        return parser

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
            msg = _("%(user)s not removed from group %(group)s\n") % {
                'user': parsed_args.user,
                'group': parsed_args.group,
            }
            sys.stderr.write(msg)
        else:
            msg = _("%(user)s removed from group %(group)s\n") % {
                'user': parsed_args.user,
                'group': parsed_args.group,
            }
            sys.stdout.write(msg)


class SetGroup(command.Command):
    """Set group properties"""

    def get_parser(self, prog_name):
        parser = super(SetGroup, self).get_parser(prog_name)
        parser.add_argument(
            'group',
            metavar='<group>',
            help=_('Group to modify (name or ID)'),
        )
        parser.add_argument(
            '--domain',
            metavar='<domain>',
            help=_('Domain containing <group> (name or ID)'),
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('New group name'),
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('New group description'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        group = common.find_group(identity_client, parsed_args.group,
                                  parsed_args.domain)
        kwargs = {}
        if parsed_args.name:
            kwargs['name'] = parsed_args.name
        if parsed_args.description:
            kwargs['description'] = parsed_args.description

        identity_client.groups.update(group.id, **kwargs)


class ShowGroup(command.ShowOne):
    """Display group details"""

    def get_parser(self, prog_name):
        parser = super(ShowGroup, self).get_parser(prog_name)
        parser.add_argument(
            'group',
            metavar='<group>',
            help=_('Group to display (name or ID)'),
        )
        parser.add_argument(
            '--domain',
            metavar='<domain>',
            help=_('Domain containing <group> (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        group = common.find_group(identity_client,
                                  parsed_args.group,
                                  domain_name_or_id=parsed_args.domain)

        group._info.pop('links')
        return zip(*sorted(six.iteritems(group._info)))
