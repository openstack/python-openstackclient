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

"""Identity v3 User action implementations"""

import copy
import logging
import six

from cliff import command
from cliff import lister
from cliff import show
from keystoneclient import exceptions as ksc_exc

from openstackclient.common import utils
from openstackclient.i18n import _  # noqa
from openstackclient.identity import common


class CreateUser(show.ShowOne):
    """Create new user"""

    log = logging.getLogger(__name__ + '.CreateUser')

    def get_parser(self, prog_name):
        parser = super(CreateUser, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<name>',
            help='New user name',
        )
        parser.add_argument(
            '--domain',
            metavar='<domain>',
            help='Default domain (name or ID)',
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help='Default project (name or ID)',
        )
        common.add_project_domain_option_to_parser(parser)
        parser.add_argument(
            '--password',
            metavar='<password>',
            help='Set user password',
        )
        parser.add_argument(
            '--password-prompt',
            dest="password_prompt",
            action="store_true",
            help='Prompt interactively for password',
        )
        parser.add_argument(
            '--email',
            metavar='<email-address>',
            help='Set user email address',
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help='User description',
        )
        enable_group = parser.add_mutually_exclusive_group()
        enable_group.add_argument(
            '--enable',
            action='store_true',
            help='Enable user (default)',
        )
        enable_group.add_argument(
            '--disable',
            action='store_true',
            help='Disable user',
        )
        parser.add_argument(
            '--or-show',
            action='store_true',
            help=_('Return existing user'),
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        project_id = None
        if parsed_args.project:
            project_id = common.find_project(identity_client,
                                             parsed_args.project,
                                             parsed_args.project_domain).id

        domain_id = None
        if parsed_args.domain:
            domain_id = common.find_domain(identity_client,
                                           parsed_args.domain).id

        enabled = True
        if parsed_args.disable:
            enabled = False
        if parsed_args.password_prompt:
            parsed_args.password = utils.get_password(self.app.stdin)

        try:
            user = identity_client.users.create(
                name=parsed_args.name,
                domain=domain_id,
                default_project=project_id,
                password=parsed_args.password,
                email=parsed_args.email,
                description=parsed_args.description,
                enabled=enabled
            )
        except ksc_exc.Conflict as e:
            if parsed_args.or_show:
                user = utils.find_resource(identity_client.users,
                                           parsed_args.name,
                                           domain_id=domain_id)
                self.log.info('Returning existing user %s', user.name)
            else:
                raise e

        user._info.pop('links')
        return zip(*sorted(six.iteritems(user._info)))


class DeleteUser(command.Command):
    """Delete user(s)"""

    log = logging.getLogger(__name__ + '.DeleteUser')

    def get_parser(self, prog_name):
        parser = super(DeleteUser, self).get_parser(prog_name)
        parser.add_argument(
            'users',
            metavar='<user>',
            nargs="+",
            help='User(s) to delete (name or ID)',
        )
        parser.add_argument(
            '--domain',
            metavar='<domain>',
            help='Domain owning <user> (name or ID)',
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        domain = None
        if parsed_args.domain:
            domain = common.find_domain(identity_client, parsed_args.domain)
        for user in parsed_args.users:
            if domain is not None:
                user_obj = utils.find_resource(identity_client.users,
                                               user,
                                               domain_id=domain.id)
            else:
                user_obj = utils.find_resource(identity_client.users,
                                               user)
            identity_client.users.delete(user_obj.id)
        return


class ListUser(lister.Lister):
    """List users"""

    log = logging.getLogger(__name__ + '.ListUser')

    def get_parser(self, prog_name):
        parser = super(ListUser, self).get_parser(prog_name)
        parser.add_argument(
            '--domain',
            metavar='<domain>',
            help='Filter users by <domain> (name or ID)',
        )
        project_or_group = parser.add_mutually_exclusive_group()
        project_or_group.add_argument(
            '--group',
            metavar='<group>',
            help='Filter users by <group> membership (name or ID)',
        )
        project_or_group.add_argument(
            '--project',
            metavar='<project>',
            help='Filter users by <project> (name or ID)',
        )
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

        group = None
        if parsed_args.group:
            group = common.find_group(identity_client,
                                      parsed_args.group,
                                      parsed_args.domain).id

        if parsed_args.project:
            if domain is not None:
                project = utils.find_resource(
                    identity_client.projects,
                    parsed_args.project,
                    domain_id=domain
                ).id
            else:
                project = utils.find_resource(
                    identity_client.projects,
                    parsed_args.project,
                ).id

            assignments = identity_client.role_assignments.list(
                project=project)

            # NOTE(stevemar): If a user has more than one role on a project
            # then they will have two entries in the returned data. Since we
            # are looking for any role, let's just track unique user IDs.
            user_ids = set()
            for assignment in assignments:
                if hasattr(assignment, 'user'):
                    user_ids.add(assignment.user['id'])

            # NOTE(stevemar): Call find_resource once we have unique IDs, so
            # it's fewer trips to the Identity API, then collect the data.
            data = []
            for user_id in user_ids:
                user = utils.find_resource(identity_client.users, user_id)
                data.append(user)

        else:
            data = identity_client.users.list(
                domain=domain,
                group=group,
            )

        # Column handling
        if parsed_args.long:
            columns = ['ID', 'Name', 'Default Project Id', 'Domain Id',
                       'Description', 'Email', 'Enabled']
            column_headers = copy.deepcopy(columns)
            column_headers[2] = 'Project'
            column_headers[3] = 'Domain'
        else:
            columns = ['ID', 'Name']
            column_headers = columns

        return (
            column_headers,
            (utils.get_item_properties(
                s, columns,
                formatters={},
            ) for s in data)
        )


class SetUser(command.Command):
    """Set user properties"""

    log = logging.getLogger(__name__ + '.SetUser')

    def get_parser(self, prog_name):
        parser = super(SetUser, self).get_parser(prog_name)
        parser.add_argument(
            'user',
            metavar='<user>',
            help='User to change (name or ID)',
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            help='Set user name',
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help='Set default project (name or ID)',
        )
        common.add_project_domain_option_to_parser(parser)
        parser.add_argument(
            '--password',
            metavar='<password>',
            help='Set user password',
        )
        parser.add_argument(
            '--password-prompt',
            dest="password_prompt",
            action="store_true",
            help='Prompt interactively for password',
        )
        parser.add_argument(
            '--email',
            metavar='<email-address>',
            help='Set user email address',
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help='Set user description',
        )
        enable_group = parser.add_mutually_exclusive_group()
        enable_group.add_argument(
            '--enable',
            action='store_true',
            help='Enable user (default)',
        )
        enable_group.add_argument(
            '--disable',
            action='store_true',
            help='Disable user',
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        if parsed_args.password_prompt:
            parsed_args.password = utils.get_password(self.app.stdin)

        if (not parsed_args.name
                and not parsed_args.name
                and not parsed_args.password
                and not parsed_args.email
                and not parsed_args.project
                and not parsed_args.description
                and not parsed_args.enable
                and not parsed_args.disable):
            return

        user = utils.find_resource(
            identity_client.users,
            parsed_args.user,
        )

        kwargs = {}
        if parsed_args.name:
            kwargs['name'] = parsed_args.name
        if parsed_args.email:
            kwargs['email'] = parsed_args.email
        if parsed_args.password:
            kwargs['password'] = parsed_args.password
        if parsed_args.description:
            kwargs['description'] = parsed_args.description
        if parsed_args.project:
            project_id = common.find_project(identity_client,
                                             parsed_args.project,
                                             parsed_args.project_domain).id
            kwargs['default_project'] = project_id
        kwargs['enabled'] = user.enabled
        if parsed_args.enable:
            kwargs['enabled'] = True
        if parsed_args.disable:
            kwargs['enabled'] = False

        identity_client.users.update(user.id, **kwargs)
        return


class SetPasswordUser(command.Command):
    """Change current user password"""

    log = logging.getLogger(__name__ + '.SetPasswordUser')

    def get_parser(self, prog_name):
        parser = super(SetPasswordUser, self).get_parser(prog_name)
        parser.add_argument(
            '--password',
            metavar='<new-password>',
            help='New user password'
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        current_password = utils.get_password(
            self.app.stdin, prompt="Current Password:", confirm=False)

        password = parsed_args.password
        if password is None:
            password = utils.get_password(
                self.app.stdin, prompt="New Password:")

        identity_client.users.update_password(current_password, password)


class ShowUser(show.ShowOne):
    """Display user details"""

    log = logging.getLogger(__name__ + '.ShowUser')

    def get_parser(self, prog_name):
        parser = super(ShowUser, self).get_parser(prog_name)
        parser.add_argument(
            'user',
            metavar='<user>',
            help='User to display (name or ID)',
        )
        parser.add_argument(
            '--domain',
            metavar='<domain>',
            help='Domain owning <user> (name or ID)',
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        if parsed_args.domain:
            domain = common.find_domain(identity_client, parsed_args.domain)
            user = utils.find_resource(identity_client.users,
                                       parsed_args.user,
                                       domain_id=domain.id)
        else:
            user = utils.find_resource(identity_client.users,
                                       parsed_args.user)

        user._info.pop('links')
        return zip(*sorted(six.iteritems(user._info)))
