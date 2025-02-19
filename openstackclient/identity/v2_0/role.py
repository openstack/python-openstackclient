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

from keystoneauth1 import exceptions as ks_exc
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _


LOG = logging.getLogger(__name__)


class AddRole(command.ShowOne):
    _description = _("Add role to project:user")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
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
        return zip(*sorted(info.items()))


class CreateRole(command.ShowOne):
    _description = _("Create new role")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
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

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        try:
            role = identity_client.roles.create(parsed_args.role_name)
        except ks_exc.Conflict:
            if parsed_args.or_show:
                role = utils.find_resource(
                    identity_client.roles,
                    parsed_args.role_name,
                )
                LOG.info(_('Returning existing role %s'), role.name)
            else:
                raise

        info = {}
        info.update(role._info)
        return zip(*sorted(info.items()))


class DeleteRole(command.Command):
    _description = _("Delete role(s)")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'roles',
            metavar='<role>',
            nargs="+",
            help=_('Role(s) to delete (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        errors = 0
        for role in parsed_args.roles:
            try:
                role_obj = utils.find_resource(
                    identity_client.roles,
                    role,
                )
                identity_client.roles.delete(role_obj.id)
            except Exception as e:
                errors += 1
                LOG.error(
                    _(
                        "Failed to delete role with "
                        "name or ID '%(role)s': %(e)s"
                    ),
                    {'role': role, 'e': e},
                )

        if errors > 0:
            total = len(parsed_args.roles)
            msg = _("%(errors)s of %(total)s roles failed to delete.") % {
                'errors': errors,
                'total': total,
            }
            raise exceptions.CommandError(msg)


class ListRole(command.Lister):
    _description = _("List roles")

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        columns = ('ID', 'Name')
        data = identity_client.roles.list()

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


class RemoveRole(command.Command):
    _description = _("Remove role from project : user")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
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

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        role = utils.find_resource(identity_client.roles, parsed_args.role)
        project = utils.find_resource(
            identity_client.tenants,
            parsed_args.project,
        )
        user = utils.find_resource(identity_client.users, parsed_args.user)
        identity_client.roles.remove_user_role(user.id, role.id, project.id)


class ShowRole(command.ShowOne):
    _description = _("Display role details")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'role',
            metavar='<role>',
            help=_('Role to display (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        role = utils.find_resource(identity_client.roles, parsed_args.role)

        info = {}
        info.update(role._info)
        return zip(*sorted(info.items()))
