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

"""Identity v2 Assignment action implementations"""

from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _  # noqa


class ListRoleAssignment(command.Lister):
    _description = _("List role assignments")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--user',
            metavar='<user>',
            help='User to filter (name or ID)',
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help='Project to filter (name or ID)',
        )
        parser.add_argument(
            '--names',
            action="store_true",
            help='Display names instead of IDs',
        )
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
        identity_client = self.app.client_manager.identity
        auth_ref = self.app.client_manager.auth_ref

        include_names = True if parsed_args.names else False

        user = None
        if parsed_args.user:
            user = utils.find_resource(
                identity_client.users,
                parsed_args.user,
            )
        elif parsed_args.authuser:
            if auth_ref:
                user = utils.find_resource(
                    identity_client.users, auth_ref.user_id
                )

        project = None
        if parsed_args.project:
            project = utils.find_resource(
                identity_client.projects,
                parsed_args.project,
            )
        elif parsed_args.authproject:
            if auth_ref:
                project = utils.find_resource(
                    identity_client.projects, auth_ref.project_id
                )

        # If user or project is not specified, we would ideally list all
        # relevant assignments in the system (to be compatible with v3).
        # However, there is no easy way of doing that in v2.
        if not user or not project:
            msg = _("Project and User must be specified")
            raise exceptions.CommandError(msg)
        else:
            data = identity_client.roles.roles_for_user(user.id, project.id)

        columns = ('Role', 'User', 'Project')
        for user_role in data:
            if include_names:
                setattr(user_role, 'role', user_role.name)
                user_role.user = user.name
                user_role.project = project.name
            else:
                setattr(user_role, 'role', user_role.id)
                user_role.user = user.id
                user_role.project = project.id

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
