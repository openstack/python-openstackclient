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

import logging
import six

from cliff import command
from cliff import lister
from cliff import show

from openstackclient.common import utils


class CreateUser(show.ShowOne):
    """Create new user"""

    log = logging.getLogger(__name__ + '.CreateUser')

    def get_parser(self, prog_name):
        parser = super(CreateUser, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<user-name>',
            help='New user name',
        )
        parser.add_argument(
            '--password',
            metavar='<user-password>',
            help='New user password',
        )
        parser.add_argument(
            '--password-prompt',
            dest="password_prompt",
            action="store_true",
            help='Prompt interactively for password',
        )
        parser.add_argument(
            '--email',
            metavar='<user-email>',
            help='New user email address',
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help='Set default project (name or ID)',
        )
        parser.add_argument(
            '--domain',
            metavar='<domain>',
            help='New default domain name or ID',
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help='Description for new user',
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

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)', parsed_args)
        identity_client = self.app.client_manager.identity

        if parsed_args.project:
            project_id = utils.find_resource(
                identity_client.projects,
                parsed_args.project,
            ).id
        else:
            project_id = None

        if parsed_args.domain:
            domain_id = utils.find_resource(
                identity_client.domains, parsed_args.domain).id
        else:
            domain_id = None

        enabled = True
        if parsed_args.disable:
            enabled = False
        if parsed_args.password_prompt:
            parsed_args.password = utils.get_password(self.app.stdin)

        user = identity_client.users.create(
            name=parsed_args.name,
            domain=domain_id,
            default_project=project_id,
            password=parsed_args.password,
            email=parsed_args.email,
            description=parsed_args.description,
            enabled=enabled
        )

        info = {}
        info.update(user._info)
        return zip(*sorted(six.iteritems(info)))


class DeleteUser(command.Command):
    """Delete user"""

    log = logging.getLogger(__name__ + '.DeleteUser')

    def get_parser(self, prog_name):
        parser = super(DeleteUser, self).get_parser(prog_name)
        parser.add_argument(
            'user',
            metavar='<user>',
            help='User to delete (name or ID)',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)', parsed_args)
        identity_client = self.app.client_manager.identity

        user = utils.find_resource(
            identity_client.users,
            parsed_args.user,
        )

        identity_client.users.delete(user.id)
        return


class ListUser(lister.Lister):
    """List users"""

    log = logging.getLogger(__name__ + '.ListUser')

    def get_parser(self, prog_name):
        parser = super(ListUser, self).get_parser(prog_name)
        parser.add_argument(
            '--domain',
            metavar='<domain>',
            help='Filter group list by <domain>',
        )
        parser.add_argument(
            '--group',
            metavar='<group>',
            help='List memberships of <group> (name or ID)',
        )
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help='List additional fields in output',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)', parsed_args)
        identity_client = self.app.client_manager.identity

        if parsed_args.domain:
            domain = utils.find_resource(
                identity_client.domains,
                parsed_args.domain,
            ).id
        else:
            domain = None

        if parsed_args.group:
            group = utils.find_resource(
                identity_client.groups,
                parsed_args.group,
            ).id
        else:
            group = None

        # List users
        if parsed_args.long:
            columns = ('ID', 'Name', 'Project Id', 'Domain Id',
                       'Description', 'Email', 'Enabled')
        else:
            columns = ('ID', 'Name')
        data = identity_client.users.list(
            domain=domain,
            group=group,
        )

        return (
            columns,
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
            metavar='<new-user-name>',
            help='New user name',
        )
        parser.add_argument(
            '--password',
            metavar='<user-password>',
            help='New user password',
        )
        parser.add_argument(
            '--password-prompt',
            dest="password_prompt",
            action="store_true",
            help='Prompt interactively for password',
        )
        parser.add_argument(
            '--email',
            metavar='<user-email>',
            help='New user email address',
        )
        parser.add_argument(
            '--domain',
            metavar='<domain>',
            help='New domain name or ID',
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help='New project name or ID',
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help='New description',
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

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)', parsed_args)
        identity_client = self.app.client_manager.identity

        if parsed_args.password_prompt:
            parsed_args.password = utils.get_password(self.app.stdin)

        if (not parsed_args.name
                and not parsed_args.name
                and not parsed_args.password
                and not parsed_args.email
                and not parsed_args.domain
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
            project_id = utils.find_resource(
                identity_client.projects, parsed_args.project).id
            kwargs['projectId'] = project_id
        if parsed_args.domain:
            domain_id = utils.find_resource(
                identity_client.domains, parsed_args.domain).id
            kwargs['domainId'] = domain_id
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

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)', parsed_args)
        identity_client = self.app.client_manager.identity

        current_password = utils.get_password(
            self.app.stdin, prompt="Current Password:", confirm=False)

        password = parsed_args.password
        if password is None:
            password = utils.get_password(
                self.app.stdin, prompt="New Password:")

        identity_client.users.update_password(current_password, password)


class ShowUser(show.ShowOne):
    """Show user details"""

    log = logging.getLogger(__name__ + '.ShowUser')

    def get_parser(self, prog_name):
        parser = super(ShowUser, self).get_parser(prog_name)
        parser.add_argument(
            'user',
            metavar='<user>',
            help='User to display (name or ID)',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)', parsed_args)
        identity_client = self.app.client_manager.identity

        user = utils.find_resource(
            identity_client.users,
            parsed_args.user,
        )

        info = {}
        info.update(user._info)
        return zip(*sorted(six.iteritems(info)))
