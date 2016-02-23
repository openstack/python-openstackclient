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
import sys

from keystoneauth1 import exceptions as ks_exc
from osc_lib.command import command
from osc_lib import utils
import six

from openstackclient.i18n import _
from openstackclient.identity import common


LOG = logging.getLogger(__name__)


def _add_identity_and_resource_options_to_parser(parser):
    domain_or_project = parser.add_mutually_exclusive_group()
    domain_or_project.add_argument(
        '--domain',
        metavar='<domain>',
        help=_('Include <domain> (name or ID)'),
    )
    domain_or_project.add_argument(
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
    if parsed_args.user and parsed_args.domain:
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
    """Adds a role assignment to a user or group on a domain or project"""

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

        if (not parsed_args.user and not parsed_args.domain
                and not parsed_args.group and not parsed_args.project):
            return

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
        if not kwargs:
            sys.stderr.write(_("Role not added, incorrect set of arguments "
                               "provided. See openstack --help for more "
                               "details\n"))
            return

        identity_client.roles.grant(role.id, **kwargs)


class CreateRole(command.ShowOne):
    """Create new role"""

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
    """Delete role(s)"""

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

        for role in parsed_args.roles:
            role_obj = utils.find_resource(
                identity_client.roles,
                role,
                domain_id=domain_id
            )
            identity_client.roles.delete(role_obj.id)


class ListRole(command.Lister):
    """List roles"""

    def get_parser(self, prog_name):
        parser = super(ListRole, self).get_parser(prog_name)

        # TODO(henry-nash): The use of the List Role command to list
        # assignments (as well as roles) has been deprecated. In order
        # to support domain specific roles, we are overriding the domain
        # option to allow specification of the domain for the role. This does
        # not conflict with any existing commands, since for the deprecated
        # assignments listing you were never allowed to only specify a domain
        # (you also needed to specify a user).
        #
        # Once we have removed the deprecated options entirely, we must
        # replace the call to _add_identity_and_resource_options_to_parser()
        # below with just adding the domain option into the parser.
        _add_identity_and_resource_options_to_parser(parser)
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        if parsed_args.user:
            user = common.find_user(
                identity_client,
                parsed_args.user,
                parsed_args.user_domain,
            )
        elif parsed_args.group:
            group = common.find_group(
                identity_client,
                parsed_args.group,
                parsed_args.group_domain,
            )

        if parsed_args.domain:
            domain = common.find_domain(
                identity_client,
                parsed_args.domain,
            )
        elif parsed_args.project:
            project = common.find_project(
                identity_client,
                parsed_args.project,
                parsed_args.project_domain,
            )

        # no user or group specified, list all roles in the system
        if not parsed_args.user and not parsed_args.group:
            if not parsed_args.domain:
                columns = ('ID', 'Name')
                data = identity_client.roles.list()
            else:
                columns = ('ID', 'Name', 'Domain')
                data = identity_client.roles.list(domain_id=domain.id)
                for role in data:
                    role.domain = domain.name
        elif parsed_args.user and parsed_args.domain:
            columns = ('ID', 'Name', 'Domain', 'User')
            data = identity_client.roles.list(
                user=user,
                domain=domain,
                os_inherit_extension_inherited=parsed_args.inherited
            )
            for user_role in data:
                user_role.user = user.name
                user_role.domain = domain.name
            self.log.warning(_('Listing assignments using role list is '
                               'deprecated. Use role assignment list --user '
                               '<user-name> --domain <domain-name> --names '
                               'instead.'))
        elif parsed_args.user and parsed_args.project:
            columns = ('ID', 'Name', 'Project', 'User')
            data = identity_client.roles.list(
                user=user,
                project=project,
                os_inherit_extension_inherited=parsed_args.inherited
            )
            for user_role in data:
                user_role.user = user.name
                user_role.project = project.name
            self.log.warning(_('Listing assignments using role list is '
                               'deprecated. Use role assignment list --user '
                               '<user-name> --project <project-name> --names '
                               'instead.'))
        elif parsed_args.user:
            columns = ('ID', 'Name')
            data = identity_client.roles.list(
                user=user,
                domain='default',
                os_inherit_extension_inherited=parsed_args.inherited
            )
            self.log.warning(_('Listing assignments using role list is '
                               'deprecated. Use role assignment list --user '
                               '<user-name> --domain default --names '
                               'instead.'))
        elif parsed_args.group and parsed_args.domain:
            columns = ('ID', 'Name', 'Domain', 'Group')
            data = identity_client.roles.list(
                group=group,
                domain=domain,
                os_inherit_extension_inherited=parsed_args.inherited
            )
            for group_role in data:
                group_role.group = group.name
                group_role.domain = domain.name
            self.log.warning(_('Listing assignments using role list is '
                               'deprecated. Use role assignment list --group '
                               '<group-name> --domain <domain-name> --names '
                               'instead.'))
        elif parsed_args.group and parsed_args.project:
            columns = ('ID', 'Name', 'Project', 'Group')
            data = identity_client.roles.list(
                group=group,
                project=project,
                os_inherit_extension_inherited=parsed_args.inherited
            )
            for group_role in data:
                group_role.group = group.name
                group_role.project = project.name
            self.log.warning(_('Listing assignments using role list is '
                               'deprecated. Use role assignment list --group '
                               '<group-name> --project <project-name> --names '
                               'instead.'))
        else:
            sys.stderr.write(_("Error: If a user or group is specified, "
                               "either --domain or --project must also be "
                               "specified to list role grants.\n"))
            return ([], [])

        return (columns,
                (utils.get_item_properties(
                    s, columns,
                    formatters={},
                ) for s in data))


class RemoveRole(command.Command):
    """Removes a role assignment from domain/project : user/group"""

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

        if (not parsed_args.user and not parsed_args.domain
                and not parsed_args.group and not parsed_args.project):
            sys.stderr.write(_("Incorrect set of arguments provided. "
                               "See openstack --help for more details\n"))
            return

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
        if not kwargs:
            sys.stderr.write(_("Role not removed, incorrect set of arguments "
                               "provided. See openstack --help for more "
                               "details\n"))
            return
        identity_client.roles.revoke(role.id, **kwargs)


class SetRole(command.Command):
    """Set role properties"""

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
    """Display role details"""

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
