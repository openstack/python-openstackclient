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

from keystoneauth1 import exceptions as ks_exc
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils
import six

from openstackclient.i18n import _
from openstackclient.identity import common


LOG = logging.getLogger(__name__)


def _add_identity_and_resource_options_to_parser(parser):
    system_or_domain_or_project = parser.add_mutually_exclusive_group()
    system_or_domain_or_project.add_argument(
        '--system',
        metavar='<system>',
        help=_('Include <system> (all)'),
    )
    system_or_domain_or_project.add_argument(
        '--domain',
        metavar='<domain>',
        help=_('Include <domain> (name or ID)'),
    )
    system_or_domain_or_project.add_argument(
        '--project',
        metavar='<project>',
        help=_('Include <project> (name or ID)'),
    )
    user_or_group = parser.add_mutually_exclusive_group()
    user_or_group.add_argument(
        '--user',
        metavar='<user>',
        help=_('Include <user> (name or ID)'),
    )
    user_or_group.add_argument(
        '--group',
        metavar='<group>',
        help=_('Include <group> (name or ID)'),
    )
    common.add_group_domain_option_to_parser(parser)
    common.add_project_domain_option_to_parser(parser)
    common.add_user_domain_option_to_parser(parser)
    common.add_inherited_option_to_parser(parser)


def _process_identity_and_resource_options(parsed_args,
                                           identity_client_manager):
    kwargs = {}
    if parsed_args.user and parsed_args.system:
        kwargs['user'] = common.find_user(
            identity_client_manager,
            parsed_args.user,
            parsed_args.user_domain,
        ).id
        kwargs['system'] = parsed_args.system
    elif parsed_args.user and parsed_args.domain:
        kwargs['user'] = common.find_user(
            identity_client_manager,
            parsed_args.user,
            parsed_args.user_domain,
        ).id
        kwargs['domain'] = common.find_domain(
            identity_client_manager,
            parsed_args.domain,
        ).id
    elif parsed_args.user and parsed_args.project:
        kwargs['user'] = common.find_user(
            identity_client_manager,
            parsed_args.user,
            parsed_args.user_domain,
        ).id
        kwargs['project'] = common.find_project(
            identity_client_manager,
            parsed_args.project,
            parsed_args.project_domain,
        ).id
    elif parsed_args.group and parsed_args.system:
        kwargs['group'] = common.find_group(
            identity_client_manager,
            parsed_args.group,
            parsed_args.group_domain,
        ).id
        kwargs['system'] = parsed_args.system
    elif parsed_args.group and parsed_args.domain:
        kwargs['group'] = common.find_group(
            identity_client_manager,
            parsed_args.group,
            parsed_args.group_domain,
        ).id
        kwargs['domain'] = common.find_domain(
            identity_client_manager,
            parsed_args.domain,
        ).id
    elif parsed_args.group and parsed_args.project:
        kwargs['group'] = common.find_group(
            identity_client_manager,
            parsed_args.group,
            parsed_args.group_domain,
        ).id
        kwargs['project'] = common.find_project(
            identity_client_manager,
            parsed_args.project,
            parsed_args.project_domain,
        ).id
    kwargs['os_inherit_extension_inherited'] = parsed_args.inherited
    return kwargs


class AddRole(command.Command):
    _description = _("Adds a role assignment to a user or group on the "
                     "system, a domain, or a project")

    def get_parser(self, prog_name):
        parser = super(AddRole, self).get_parser(prog_name)
        parser.add_argument(
            'role',
            metavar='<role>',
            help=_('Role to add to <user> (name or ID)'),
        )
        _add_identity_and_resource_options_to_parser(parser)
        common.add_role_domain_option_to_parser(parser)
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        if (not parsed_args.user and not parsed_args.domain and
                not parsed_args.group and not parsed_args.project):
            msg = _("Role not added, incorrect set of arguments "
                    "provided. See openstack --help for more details")
            raise exceptions.CommandError(msg)

        domain_id = None
        if parsed_args.role_domain:
            domain_id = common.find_domain(identity_client,
                                           parsed_args.role_domain).id
        role = utils.find_resource(
            identity_client.roles,
            parsed_args.role,
            domain_id=domain_id
        )

        kwargs = _process_identity_and_resource_options(
            parsed_args, self.app.client_manager.identity)

        identity_client.roles.grant(role.id, **kwargs)


class CreateRole(command.ShowOne):
    _description = _("Create new role")

    def get_parser(self, prog_name):
        parser = super(CreateRole, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<role-name>',
            help=_('New role name'),
        )
        parser.add_argument(
            '--domain',
            metavar='<domain>',
            help=_('Domain the role belongs to (name or ID)'),
        )
        parser.add_argument(
            '--or-show',
            action='store_true',
            help=_('Return existing role'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        domain_id = None
        if parsed_args.domain:
            domain_id = common.find_domain(identity_client,
                                           parsed_args.domain).id

        try:
            role = identity_client.roles.create(
                name=parsed_args.name, domain=domain_id)

        except ks_exc.Conflict:
            if parsed_args.or_show:
                role = utils.find_resource(identity_client.roles,
                                           parsed_args.name,
                                           domain_id=domain_id)
                LOG.info(_('Returning existing role %s'), role.name)
            else:
                raise

        role._info.pop('links')
        return zip(*sorted(six.iteritems(role._info)))


class DeleteRole(command.Command):
    _description = _("Delete role(s)")

    def get_parser(self, prog_name):
        parser = super(DeleteRole, self).get_parser(prog_name)
        parser.add_argument(
            'roles',
            metavar='<role>',
            nargs="+",
            help=_('Role(s) to delete (name or ID)'),
        )
        parser.add_argument(
            '--domain',
            metavar='<domain>',
            help=_('Domain the role belongs to (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        domain_id = None
        if parsed_args.domain:
            domain_id = common.find_domain(identity_client,
                                           parsed_args.domain).id
        errors = 0
        for role in parsed_args.roles:
            try:
                role_obj = utils.find_resource(
                    identity_client.roles,
                    role,
                    domain_id=domain_id
                )
                identity_client.roles.delete(role_obj.id)
            except Exception as e:
                errors += 1
                LOG.error(_("Failed to delete role with "
                          "name or ID '%(role)s': %(e)s"),
                          {'role': role, 'e': e})

        if errors > 0:
            total = len(parsed_args.roles)
            msg = (_("%(errors)s of %(total)s roles failed "
                   "to delete.") % {'errors': errors, 'total': total})
            raise exceptions.CommandError(msg)


class ListRole(command.Lister):
    _description = _("List roles")

    def get_parser(self, prog_name):
        parser = super(ListRole, self).get_parser(prog_name)
        parser.add_argument(
            '--domain',
            metavar='<domain>',
            help=_('Include <domain> (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        if parsed_args.domain:
            domain = common.find_domain(
                identity_client,
                parsed_args.domain,
            )
            columns = ('ID', 'Name', 'Domain')
            data = identity_client.roles.list(domain_id=domain.id)
            for role in data:
                role.domain = domain.name
        else:
            columns = ('ID', 'Name')
            data = identity_client.roles.list()

        return (columns,
                (utils.get_item_properties(
                    s, columns,
                    formatters={},
                ) for s in data))


class RemoveRole(command.Command):
    _description = _("Removes a role assignment from system/domain/project : "
                     "user/group")

    def get_parser(self, prog_name):
        parser = super(RemoveRole, self).get_parser(prog_name)
        parser.add_argument(
            'role',
            metavar='<role>',
            help=_('Role to remove (name or ID)'),
        )
        _add_identity_and_resource_options_to_parser(parser)
        common.add_role_domain_option_to_parser(parser)

        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        if (not parsed_args.user and not parsed_args.domain and
                not parsed_args.group and not parsed_args.project):
            msg = _("Incorrect set of arguments provided. "
                    "See openstack --help for more details")
            raise exceptions.CommandError(msg)

        domain_id = None
        if parsed_args.role_domain:
            domain_id = common.find_domain(identity_client,
                                           parsed_args.role_domain).id
        role = utils.find_resource(
            identity_client.roles,
            parsed_args.role,
            domain_id=domain_id
        )

        kwargs = _process_identity_and_resource_options(
            parsed_args, self.app.client_manager.identity)
        identity_client.roles.revoke(role.id, **kwargs)


class SetRole(command.Command):
    _description = _("Set role properties")

    def get_parser(self, prog_name):
        parser = super(SetRole, self).get_parser(prog_name)
        parser.add_argument(
            'role',
            metavar='<role>',
            help=_('Role to modify (name or ID)'),
        )
        parser.add_argument(
            '--domain',
            metavar='<domain>',
            help=_('Domain the role belongs to (name or ID)'),
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('Set role name'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        domain_id = None
        if parsed_args.domain:
            domain_id = common.find_domain(identity_client,
                                           parsed_args.domain).id

        role = utils.find_resource(identity_client.roles,
                                   parsed_args.role,
                                   domain_id=domain_id)

        identity_client.roles.update(role.id, name=parsed_args.name)


class ShowRole(command.ShowOne):
    _description = _("Display role details")

    def get_parser(self, prog_name):
        parser = super(ShowRole, self).get_parser(prog_name)
        parser.add_argument(
            'role',
            metavar='<role>',
            help=_('Role to display (name or ID)'),
        )
        parser.add_argument(
            '--domain',
            metavar='<domain>',
            help=_('Domain the role belongs to (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        domain_id = None
        if parsed_args.domain:
            domain_id = common.find_domain(identity_client,
                                           parsed_args.domain).id

        role = utils.find_resource(identity_client.roles,
                                   parsed_args.role,
                                   domain_id=domain_id)

        role._info.pop('links')
        return zip(*sorted(six.iteritems(role._info)))
