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
from keystoneclient import exceptions as ksc_exc

from openstackclient.common import utils
from openstackclient.i18n import _  # noqa
from openstackclient.identity import common


def _add_identity_and_resource_options_to_parser(parser):
    domain_or_project = parser.add_mutually_exclusive_group()
    domain_or_project.add_argument(
        '--domain',
        metavar='<domain>',
        help='Include <domain> (name or ID)',
    )
    domain_or_project.add_argument(
        '--project',
        metavar='<project>',
        help='Include <project> (name or ID)',
    )
    user_or_group = parser.add_mutually_exclusive_group()
    user_or_group.add_argument(
        '--user',
        metavar='<user>',
        help='Include <user> (name or ID)',
    )
    user_or_group.add_argument(
        '--group',
        metavar='<group>',
        help='Include <group> (name or ID)',
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
    """Adds a role to a user or group on a domain or project"""

    log = logging.getLogger(__name__ + '.AddRole')

    def get_parser(self, prog_name):
        parser = super(AddRole, self).get_parser(prog_name)
        parser.add_argument(
            'role',
            metavar='<role>',
            help='Role to add to <user> (name or ID)',
        )
        _add_identity_and_resource_options_to_parser(parser)
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        if (not parsed_args.user and not parsed_args.domain
                and not parsed_args.group and not parsed_args.project):
            return

        role = utils.find_resource(
            identity_client.roles,
            parsed_args.role,
        )

        kwargs = _process_identity_and_resource_options(
            parsed_args, self.app.client_manager.identity)
        if not kwargs:
            sys.stderr.write("Role not added, incorrect set of arguments "
                             "provided. See openstack --help for more "
                             "details\n")
            return

        identity_client.roles.grant(role.id, **kwargs)
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
            role = identity_client.roles.create(name=parsed_args.name)
        except ksc_exc.Conflict as e:
            if parsed_args.or_show:
                role = utils.find_resource(identity_client.roles,
                                           parsed_args.name)
                self.log.info('Returning existing role %s', role.name)
            else:
                raise e

        role._info.pop('links')
        return zip(*sorted(six.iteritems(role._info)))


class DeleteRole(command.Command):
    """Delete role(s)"""

    log = logging.getLogger(__name__ + '.DeleteRole')

    def get_parser(self, prog_name):
        parser = super(DeleteRole, self).get_parser(prog_name)
        parser.add_argument(
            'roles',
            metavar='<role>',
            nargs="+",
            help='Role(s) to delete (name or ID)',
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
        _add_identity_and_resource_options_to_parser(parser)
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
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
    """Remove role from domain/project : user/group"""

    log = logging.getLogger(__name__ + '.RemoveRole')

    def get_parser(self, prog_name):
        parser = super(RemoveRole, self).get_parser(prog_name)
        parser.add_argument(
            'role',
            metavar='<role>',
            help='Role to remove (name or ID)',
        )
        _add_identity_and_resource_options_to_parser(parser)
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        if (not parsed_args.user and not parsed_args.domain
                and not parsed_args.group and not parsed_args.project):
            return

        role = utils.find_resource(
            identity_client.roles,
            parsed_args.role,
        )

        kwargs = _process_identity_and_resource_options(
            parsed_args, self.app.client_manager.identity)
        if not kwargs:
            sys.stderr.write("Role not removed, incorrect set of arguments \
            provided. See openstack --help for more details\n")
            return

        identity_client.roles.revoke(role.id, **kwargs)
        return


class SetRole(command.Command):
    """Set role properties"""

    log = logging.getLogger(__name__ + '.SetRole')

    def get_parser(self, prog_name):
        parser = super(SetRole, self).get_parser(prog_name)
        parser.add_argument(
            'role',
            metavar='<role>',
            help='Role to modify (name or ID)',
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            help='Set role name',
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
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
    """Display role details"""

    log = logging.getLogger(__name__ + '.ShowRole')

    def get_parser(self, prog_name):
        parser = super(ShowRole, self).get_parser(prog_name)
        parser.add_argument(
            'role',
            metavar='<role>',
            help='Role to display (name or ID)',
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        role = utils.find_resource(
            identity_client.roles,
            parsed_args.role,
        )

        role._info.pop('links')
        return zip(*sorted(six.iteritems(role._info)))
