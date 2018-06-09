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

"""Identity v3 Assignment action implementations"""

from osc_lib.command import command
from osc_lib import utils

from openstackclient.i18n import _
from openstackclient.identity import common


class ListRoleAssignment(command.Lister):
    _description = _("List role assignments")

    def get_parser(self, prog_name):
        parser = super(ListRoleAssignment, self).get_parser(prog_name)
        parser.add_argument(
            '--effective',
            action="store_true",
            default=False,
            help=_('Returns only effective role assignments'),
        )
        parser.add_argument(
            '--role',
            metavar='<role>',
            help=_('Role to filter (name or ID)'),
        )
        common.add_role_domain_option_to_parser(parser)
        parser.add_argument(
            '--names',
            action="store_true",
            help=_('Display names instead of IDs'),
        )
        user_or_group = parser.add_mutually_exclusive_group()
        user_or_group.add_argument(
            '--user',
            metavar='<user>',
            help=_('User to filter (name or ID)'),
        )
        common.add_user_domain_option_to_parser(parser)
        user_or_group.add_argument(
            '--group',
            metavar='<group>',
            help=_('Group to filter (name or ID)'),
        )
        common.add_group_domain_option_to_parser(parser)
        system_or_domain_or_project = parser.add_mutually_exclusive_group()
        system_or_domain_or_project.add_argument(
            '--domain',
            metavar='<domain>',
            help=_('Domain to filter (name or ID)'),
        )
        system_or_domain_or_project.add_argument(
            '--project',
            metavar='<project>',
            help=_('Project to filter (name or ID)'),
        )
        system_or_domain_or_project.add_argument(
            '--system',
            metavar='<system>',
            help=_('Filter based on system role assignments'),
        )
        common.add_project_domain_option_to_parser(parser)
        common.add_inherited_option_to_parser(parser)
        parser.add_argument(
            '--auth-user',
            action="store_true",
            dest='authuser',
            help='Only list assignments for the authenticated user',
        )
        parser.add_argument(
            '--auth-project',
            action="store_true",
            dest='authproject',
            help='Only list assignments for the project to which the '
                 'authenticated user\'s token is scoped',
        )
        return parser

    def _as_tuple(self, assignment):
        return (assignment.role, assignment.user, assignment.group,
                assignment.project, assignment.domain, assignment.system,
                assignment.inherited)

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        auth_ref = self.app.client_manager.auth_ref

        role = None
        role_domain_id = None
        if parsed_args.role_domain:
            role_domain_id = common.find_domain(identity_client,
                                                parsed_args.role_domain).id
        if parsed_args.role:
            role = utils.find_resource(
                identity_client.roles,
                parsed_args.role,
                domain_id=role_domain_id
            )

        user = None
        if parsed_args.user:
            user = common.find_user(
                identity_client,
                parsed_args.user,
                parsed_args.user_domain,
            )
        elif parsed_args.authuser:
            if auth_ref:
                user = common.find_user(
                    identity_client,
                    auth_ref.user_id
                )

        system = None
        if parsed_args.system:
            system = parsed_args.system

        domain = None
        if parsed_args.domain:
            domain = common.find_domain(
                identity_client,
                parsed_args.domain,
            )

        project = None
        if parsed_args.project:
            project = common.find_project(
                identity_client,
                common._get_token_resource(identity_client, 'project',
                                           parsed_args.project),
                parsed_args.project_domain,
            )
        elif parsed_args.authproject:
            if auth_ref:
                project = common.find_project(
                    identity_client,
                    auth_ref.project_id
                )

        group = None
        if parsed_args.group:
            group = common.find_group(
                identity_client,
                parsed_args.group,
                parsed_args.group_domain,
            )

        include_names = True if parsed_args.names else False
        effective = True if parsed_args.effective else False
        columns = (
            'Role', 'User', 'Group', 'Project', 'Domain', 'System', 'Inherited'
        )

        inherited_to = 'projects' if parsed_args.inherited else None
        data = identity_client.role_assignments.list(
            domain=domain,
            user=user,
            group=group,
            project=project,
            system=system,
            role=role,
            effective=effective,
            os_inherit_extension_inherited_to=inherited_to,
            include_names=include_names)

        data_parsed = []
        for assignment in data:
            # Removing the extra "scope" layer in the assignment json
            scope = assignment.scope
            if 'project' in scope:
                if include_names:
                    prj = '@'.join([scope['project']['name'],
                                    scope['project']['domain']['name']])
                    setattr(assignment, 'project', prj)
                else:
                    setattr(assignment, 'project', scope['project']['id'])
                assignment.domain = ''
                assignment.system = ''
            elif 'domain' in scope:
                if include_names:
                    setattr(assignment, 'domain', scope['domain']['name'])
                else:
                    setattr(assignment, 'domain', scope['domain']['id'])
                assignment.project = ''
                assignment.system = ''
            elif 'system' in scope:
                # NOTE(lbragstad): If, or when, keystone supports role
                # assignments on subsets of a system, this will have to evolve
                # to handle that case instead of hardcoding to the entire
                # system.
                setattr(assignment, 'system', 'all')
                assignment.domain = ''
                assignment.project = ''
            else:
                assignment.system = ''
                assignment.domain = ''
                assignment.project = ''

            inherited = scope.get('OS-INHERIT:inherited_to') == 'projects'
            assignment.inherited = inherited

            del assignment.scope

            if hasattr(assignment, 'user'):
                if include_names:
                    usr = '@'.join([assignment.user['name'],
                                    assignment.user['domain']['name']])
                    setattr(assignment, 'user', usr)
                else:
                    setattr(assignment, 'user', assignment.user['id'])
                assignment.group = ''
            elif hasattr(assignment, 'group'):
                if include_names:
                    grp = '@'.join([assignment.group['name'],
                                    assignment.group['domain']['name']])
                    setattr(assignment, 'group', grp)
                else:
                    setattr(assignment, 'group', assignment.group['id'])
                assignment.user = ''
            else:
                assignment.user = ''
                assignment.group = ''

            if hasattr(assignment, 'role'):
                if include_names:
                    # TODO(henry-nash): If this is a domain specific role it
                    # would be good show this as role@domain, although this
                    # domain info is not yet included in the response from the
                    # server. Although we could get it by re-reading the role
                    # from the ID, let's wait until the server does the right
                    # thing.
                    setattr(assignment, 'role', assignment.role['name'])
                else:
                    setattr(assignment, 'role', assignment.role['id'])
            else:
                assignment.role = ''

            # Creating a tuple from data object fields
            # (including the blank ones)
            data_parsed.append(self._as_tuple(assignment))

        return columns, tuple(data_parsed)
