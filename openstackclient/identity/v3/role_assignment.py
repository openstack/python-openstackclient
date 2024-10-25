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

from openstack import exceptions as sdk_exceptions
from osc_lib.command import command

from openstackclient.i18n import _
from openstackclient.identity import common


def _format_role_assignment_(assignment, include_names):
    def _get_names(attr):
        return (
            (
                attr['name']
                + (
                    "@" + domain['name']
                    if (domain := attr.get('domain'))
                    else ''
                )
            )
            or ''
            if attr
            else ''
        )

    def _get_ids(attr):
        return attr['id'] or '' if attr else ''

    func = _get_names if include_names else _get_ids
    return (
        func(assignment.role),
        func(assignment.user),
        func(assignment.group),
        func(assignment.scope.get('project')),
        func(assignment.scope.get('domain')),
        'all' if assignment.scope.get("system") else '',
        assignment.scope.get("OS-INHERIT:inherited_to") == 'projects',
    )


def _find_sdk_id(find_command, name_or_id, **kwargs):
    try:
        return find_command(
            name_or_id=name_or_id, ignore_missing=False, **kwargs
        ).id
    except sdk_exceptions.ForbiddenException:
        return name_or_id


class ListRoleAssignment(command.Lister):
    _description = _("List role assignments")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--effective',
            action="store_true",
            default=None,
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

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.sdk_connection.identity
        auth_ref = self.app.client_manager.auth_ref

        role_id = None
        role_domain_id = None
        if parsed_args.role_domain:
            role_domain_id = _find_sdk_id(
                identity_client.find_domain,
                name_or_id=parsed_args.role_domain,
            )
        if parsed_args.role:
            role_id = _find_sdk_id(
                identity_client.find_role,
                name_or_id=parsed_args.role,
                domain_id=role_domain_id,
            )

        user_domain_id = None
        if parsed_args.user_domain:
            user_domain_id = _find_sdk_id(
                identity_client.find_domain,
                name_or_id=parsed_args.user_domain,
            )

        user_id = None
        if parsed_args.user:
            user_id = _find_sdk_id(
                identity_client.find_user,
                name_or_id=parsed_args.user,
                domain_id=user_domain_id,
            )
        elif parsed_args.authuser:
            if auth_ref:
                user_id = _find_sdk_id(
                    identity_client.find_user,
                    name_or_id=auth_ref.user_id,
                )

        system = None
        if parsed_args.system:
            system = parsed_args.system

        domain_id = None
        if parsed_args.domain:
            domain_id = _find_sdk_id(
                identity_client.find_domain,
                name_or_id=parsed_args.domain,
            )

        project_domain_id = None
        if parsed_args.project_domain:
            project_domain_id = _find_sdk_id(
                identity_client.find_domain,
                name_or_id=parsed_args.project_domain,
            )

        project_id = None
        if parsed_args.project:
            project_id = _find_sdk_id(
                identity_client.find_project,
                name_or_id=common._get_token_resource(
                    identity_client, 'project', parsed_args.project
                ),
                domain_id=project_domain_id,
            )
        elif parsed_args.authproject:
            if auth_ref:
                project_id = _find_sdk_id(
                    identity_client.find_project,
                    name_or_id=auth_ref.project_id,
                )

        group_domain_id = None
        if parsed_args.group_domain:
            group_domain_id = _find_sdk_id(
                identity_client.find_domain,
                name_or_id=parsed_args.group_domain,
            )

        group_id = None
        if parsed_args.group:
            group_id = _find_sdk_id(
                identity_client.find_group,
                name_or_id=parsed_args.group,
                domain_id=group_domain_id,
            )

        include_names = True if parsed_args.names else None
        columns = (
            'Role',
            'User',
            'Group',
            'Project',
            'Domain',
            'System',
            'Inherited',
        )

        inherited_to = 'projects' if parsed_args.inherited else None

        data = identity_client.role_assignments(
            role_id=role_id,
            user_id=user_id,
            group_id=group_id,
            scope_project_id=project_id,
            scope_domain_id=domain_id,
            scope_system=system,
            effective=parsed_args.effective,
            include_names=include_names,
            inherited_to=inherited_to,
        )

        data_parsed = []
        for assignment in data:
            data_parsed.append(
                _format_role_assignment_(assignment, include_names)
            )

        return columns, tuple(data_parsed)
