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

"""Identity v2.0 User action implementations"""

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
                identity_client.tenants,
                parsed_args.project,
            ).id
        else:
            project_id = None

        enabled = True
        if parsed_args.disable:
            enabled = False
        if parsed_args.password_prompt:
            parsed_args.password = utils.get_password(self.app.stdin)

        user = identity_client.users.create(
            parsed_args.name,
            parsed_args.password,
            parsed_args.email,
            tenant_id=project_id,
            enabled=enabled,
        )
        # NOTE(dtroyer): The users.create() method wants 'tenant_id' but
        #                the returned resource has 'tenantId'.  Sigh.
        #                We're using project_id now inside OSC so there.
        user._info.update(
            {'project_id': user._info.pop('tenantId')}
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
            '--project',
            metavar='<project>',
            help='Filter users by project (name or ID)',
        )
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help='List additional fields in output')
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)', parsed_args)
        identity_client = self.app.client_manager.identity

        def _format_project(project):
            if not project:
                return ""
            if project in project_cache.keys():
                return project_cache[project].name
            else:
                return project

        project = None
        if parsed_args.project:
            project = utils.find_resource(
                identity_client.tenants,
                parsed_args.project,
            )
            project = project.id

        if parsed_args.long:
            columns = (
                'ID',
                'Name',
                'tenantId',
                'Email',
                'Enabled',
            )
            column_headers = (
                'ID',
                'Name',
                'Project',
                'Email',
                'Enabled',
            )
            # Cache the project list
            project_cache = {}
            try:
                for p in identity_client.tenants.list():
                    project_cache[p.id] = p
            except Exception:
                # Just forget it if there's any trouble
                pass
        else:
            columns = column_headers = ('ID', 'Name')
        data = identity_client.users.list(tenant_id=project)

        if parsed_args.project:
            d = {}
            for s in data:
                d[s.id] = s
            data = d.values()

        if parsed_args.long:
            # FIXME(dtroyer): Sometimes user objects have 'tenant_id' instead
            #                 of 'tenantId'.  Why?  Dunno yet, but until that
            #                 is fixed we need to handle it; auth_token.py
            #                 only looks for 'tenantId'.
            for d in data:
                if 'tenant_id' in d._info:
                    d._info['tenantId'] = d._info.pop('tenant_id')
                    d._add_details(d._info)

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                    mixed_case_fields=('tenantId',),
                    formatters={'tenantId': _format_project},
                ) for s in data))


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
            '--project',
            metavar='<project>',
            help='New default project (name or ID)',
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
                and not parsed_args.project
                and not parsed_args.enable
                and not parsed_args.disable):
            return

        user = utils.find_resource(
            identity_client.users,
            parsed_args.user,
        )

        if parsed_args.password:
            identity_client.users.update_password(
                user.id,
                parsed_args.password,
            )

        if parsed_args.project:
            project = utils.find_resource(
                identity_client.tenants,
                parsed_args.project,
            )
            identity_client.users.update_tenant(
                user.id,
                project.id,
            )

        kwargs = {}
        if parsed_args.name:
            kwargs['name'] = parsed_args.name
        if parsed_args.email:
            kwargs['email'] = parsed_args.email
        kwargs['enabled'] = user.enabled
        if parsed_args.enable:
            kwargs['enabled'] = True
        if parsed_args.disable:
            kwargs['enabled'] = False

        identity_client.users.update(user.id, **kwargs)
        return


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

        if 'tenantId' in user._info:
            user._info.update(
                {'project_id': user._info.pop('tenantId')}
            )
        if 'tenant_id' in user._info:
            user._info.update(
                {'project_id': user._info.pop('tenant_id')}
            )

        info = {}
        info.update(user._info)
        return zip(*sorted(six.iteritems(info)))
