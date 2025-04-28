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

from openstack import exceptions as sdk_exc
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _
from openstackclient.identity import common


LOG = logging.getLogger(__name__)


def _format_group(group):
    columns = (
        'description',
        'domain_id',
        'id',
        'name',
    )
    column_headers = (
        'description',
        'domain_id',
        'id',
        'name',
    )
    return (
        column_headers,
        utils.get_item_properties(group, columns),
    )


class AddUserToGroup(command.Command):
    _description = _("Add user to group")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'group',
            metavar='<group>',
            help=_('Group to contain <user> (name or ID)'),
        )
        parser.add_argument(
            'user',
            metavar='<user>',
            nargs='+',
            help=_(
                'User(s) to add to <group> (name or ID) '
                '(repeat option to add multiple users)'
            ),
        )
        common.add_group_domain_option_to_parser(parser)
        common.add_user_domain_option_to_parser(parser)
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.sdk_connection.identity

        group_id = common.find_group_id_sdk(
            identity_client, parsed_args.group, parsed_args.group_domain
        )

        result = 0
        for i in parsed_args.user:
            try:
                user_id = common.find_user_id_sdk(
                    identity_client, i, parsed_args.user_domain
                )
                identity_client.add_user_to_group(user_id, group_id)
            except Exception as e:
                result += 1
                msg = _("%(user)s not added to group %(group)s: %(e)s") % {
                    'user': i,
                    'group': parsed_args.group,
                    'e': e,
                }
                LOG.error(msg)
        if result > 0:
            total = len(parsed_args.user)
            msg = (
                _(
                    "%(result)s of %(total)s users not added to group "
                    "%(group)s."
                )
            ) % {
                'result': result,
                'total': total,
                'group': parsed_args.group,
            }
            raise exceptions.CommandError(msg)


class CheckUserInGroup(command.Command):
    _description = _("Check user membership in group")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
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
        identity_client = self.app.client_manager.sdk_connection.identity

        user_id = common.find_user_id_sdk(
            identity_client,
            parsed_args.user,
            parsed_args.user_domain,
            validate_actor_existence=False,
        )
        group_id = common.find_group_id_sdk(
            identity_client,
            parsed_args.group,
            parsed_args.group_domain,
            validate_actor_existence=False,
        )

        user_in_group = False
        try:
            user_in_group = identity_client.check_user_in_group(
                user_id, group_id
            )
        except sdk_exc.ForbiddenException:
            # Assume False if forbidden
            pass
        if user_in_group:
            msg = _("%(user)s in group %(group)s\n") % {
                'user': parsed_args.user,
                'group': parsed_args.group,
            }
            self.app.stdout.write(msg)
        else:
            msg = _("%(user)s not in group %(group)s\n") % {
                'user': parsed_args.user,
                'group': parsed_args.group,
            }
            self.app.stderr.write(msg)


class CreateGroup(command.ShowOne):
    _description = _("Create new group")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
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
        identity_client = self.app.client_manager.sdk_connection.identity

        kwargs = {}
        if parsed_args.name:
            kwargs['name'] = parsed_args.name
        if parsed_args.description:
            kwargs['description'] = parsed_args.description
        if parsed_args.domain:
            kwargs['domain_id'] = common.find_domain_id_sdk(
                identity_client, parsed_args.domain
            )

        try:
            group = identity_client.create_group(**kwargs)
        except sdk_exc.ConflictException:
            if parsed_args.or_show:
                if parsed_args.domain:
                    group = identity_client.find_group(
                        parsed_args.name, domain_id=parsed_args.domain
                    )
                else:
                    group = identity_client.find_group(parsed_args.name)
                LOG.info(_('Returning existing group %s'), group.name)
            else:
                raise

        return _format_group(group)


class DeleteGroup(command.Command):
    _description = _("Delete group(s)")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
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
        identity_client = self.app.client_manager.sdk_connection.identity

        errors = 0
        for group in parsed_args.groups:
            try:
                group_id = common.find_group_id_sdk(
                    identity_client, group, parsed_args.domain
                )
                identity_client.delete_group(group_id)
            except Exception as e:
                errors += 1
                LOG.error(
                    _(
                        "Failed to delete group with "
                        "name or ID '%(group)s': %(e)s"
                    ),
                    {'group': group, 'e': e},
                )

        if errors > 0:
            total = len(parsed_args.groups)
            msg = _("%(errors)s of %(total)s groups failed to delete.") % {
                'errors': errors,
                'total': total,
            }
            raise exceptions.CommandError(msg)


class ListGroup(command.Lister):
    _description = _("List groups")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
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
        identity_client = self.app.client_manager.sdk_connection.identity

        domain = None
        if parsed_args.domain:
            domain = common.find_domain_id_sdk(
                identity_client, parsed_args.domain
            )

        data = []
        if parsed_args.user:
            user = common.find_user_id_sdk(
                identity_client,
                parsed_args.user,
                parsed_args.user_domain,
            )
            if domain:
                # NOTE(0weng): The API doesn't actually support filtering additionally by domain_id,
                # so this doesn't really do anything.
                data = identity_client.user_groups(user, domain_id=domain)
            else:
                data = identity_client.user_groups(user)
        else:
            if domain:
                data = identity_client.groups(domain_id=domain)
            else:
                data = identity_client.groups()

        # List groups
        columns: tuple[str, ...] = ('ID', 'Name')
        if parsed_args.long:
            columns += ('Domain ID', 'Description')

        return (
            columns,
            (
                utils.get_item_properties(
                    s,
                    columns,
                    formatters={},
                )
                for s in data
            ),
        )


class RemoveUserFromGroup(command.Command):
    _description = _("Remove user from group")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'group',
            metavar='<group>',
            help=_('Group containing <user> (name or ID)'),
        )
        parser.add_argument(
            'user',
            metavar='<user>',
            nargs='+',
            help=_(
                'User(s) to remove from <group> (name or ID) '
                '(repeat option to remove multiple users)'
            ),
        )
        common.add_group_domain_option_to_parser(parser)
        common.add_user_domain_option_to_parser(parser)
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.sdk_connection.identity

        group_id = common.find_group_id_sdk(
            identity_client, parsed_args.group, parsed_args.group_domain
        )

        result = 0
        for i in parsed_args.user:
            try:
                user_id = common.find_user_id_sdk(
                    identity_client, i, parsed_args.user_domain
                )
                identity_client.remove_user_from_group(user_id, group_id)
            except Exception as e:
                result += 1
                msg = _("%(user)s not removed from group %(group)s: %(e)s") % {
                    'user': i,
                    'group': parsed_args.group,
                    'e': e,
                }
                LOG.error(msg)
        if result > 0:
            total = len(parsed_args.user)
            msg = (
                _(
                    "%(result)s of %(total)s users not removed from group "
                    "%(group)s."
                )
            ) % {
                'result': result,
                'total': total,
                'group': parsed_args.group,
            }
            raise exceptions.CommandError(msg)


class SetGroup(command.Command):
    _description = _("Set group properties")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
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
        identity_client = self.app.client_manager.sdk_connection.identity
        group = common.find_group_id_sdk(
            identity_client, parsed_args.group, parsed_args.domain
        )
        kwargs = {}
        if parsed_args.name:
            kwargs['name'] = parsed_args.name
        if parsed_args.description:
            kwargs['description'] = parsed_args.description

        identity_client.update_group(group, **kwargs)


class ShowGroup(command.ShowOne):
    _description = _("Display group details")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
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
        identity_client = self.app.client_manager.sdk_connection.identity

        if parsed_args.domain:
            domain = common.find_domain_id_sdk(
                identity_client, parsed_args.domain
            )
            group = identity_client.find_group(
                parsed_args.group, domain_id=domain, ignore_missing=False
            )
        else:
            group = identity_client.find_group(
                parsed_args.group, ignore_missing=False
            )

        return _format_group(group)
