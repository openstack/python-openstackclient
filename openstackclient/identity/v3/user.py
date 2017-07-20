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

from keystoneauth1 import exceptions as ks_exc
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils
import six

from openstackclient.i18n import _
from openstackclient.identity import common


LOG = logging.getLogger(__name__)


class CreateUser(command.ShowOne):
    _description = _("Create new user")

    def get_parser(self, prog_name):
        parser = super(CreateUser, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<name>',
            help=_('New user name'),
        )
        parser.add_argument(
            '--domain',
            metavar='<domain>',
            help=_('Default domain (name or ID)'),
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_('Default project (name or ID)'),
        )
        common.add_project_domain_option_to_parser(parser)
        parser.add_argument(
            '--password',
            metavar='<password>',
            help=_('Set user password'),
        )
        parser.add_argument(
            '--password-prompt',
            dest="password_prompt",
            action="store_true",
            help=_('Prompt interactively for password'),
        )
        parser.add_argument(
            '--email',
            metavar='<email-address>',
            help=_('Set user email address'),
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('User description'),
        )
        enable_group = parser.add_mutually_exclusive_group()
        enable_group.add_argument(
            '--enable',
            action='store_true',
            help=_('Enable user (default)'),
        )
        enable_group.add_argument(
            '--disable',
            action='store_true',
            help=_('Disable user'),
        )
        parser.add_argument(
            '--or-show',
            action='store_true',
            help=_('Return existing user'),
        )
        return parser

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

        if not parsed_args.password:
            LOG.warning(_("No password was supplied, authentication will fail "
                          "when a user does not have a password."))

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
        except ks_exc.Conflict:
            if parsed_args.or_show:
                user = utils.find_resource(identity_client.users,
                                           parsed_args.name,
                                           domain_id=domain_id)
                LOG.info(_('Returning existing user %s'), user.name)
            else:
                raise

        user._info.pop('links')
        return zip(*sorted(six.iteritems(user._info)))


class DeleteUser(command.Command):
    _description = _("Delete user(s)")

    def get_parser(self, prog_name):
        parser = super(DeleteUser, self).get_parser(prog_name)
        parser.add_argument(
            'users',
            metavar='<user>',
            nargs="+",
            help=_('User(s) to delete (name or ID)'),
        )
        parser.add_argument(
            '--domain',
            metavar='<domain>',
            help=_('Domain owning <user> (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        domain = None
        if parsed_args.domain:
            domain = common.find_domain(identity_client, parsed_args.domain)
        errors = 0
        for user in parsed_args.users:
            try:
                if domain is not None:
                    user_obj = utils.find_resource(identity_client.users,
                                                   user,
                                                   domain_id=domain.id)
                else:
                    user_obj = utils.find_resource(identity_client.users,
                                                   user)
                identity_client.users.delete(user_obj.id)
            except Exception as e:
                errors += 1
                LOG.error(_("Failed to delete user with "
                          "name or ID '%(user)s': %(e)s"),
                          {'user': user, 'e': e})

        if errors > 0:
            total = len(parsed_args.users)
            msg = (_("%(errors)s of %(total)s users failed "
                   "to delete.") % {'errors': errors, 'total': total})
            raise exceptions.CommandError(msg)


class ListUser(command.Lister):
    _description = _("List users")

    def get_parser(self, prog_name):
        parser = super(ListUser, self).get_parser(prog_name)
        parser.add_argument(
            '--domain',
            metavar='<domain>',
            help=_('Filter users by <domain> (name or ID)'),
        )
        project_or_group = parser.add_mutually_exclusive_group()
        project_or_group.add_argument(
            '--group',
            metavar='<group>',
            help=_('Filter users by <group> membership (name or ID)'),
        )
        project_or_group.add_argument(
            '--project',
            metavar='<project>',
            help=_('Filter users by <project> (name or ID)'),
        )
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_('List additional fields in output'),
        )
        return parser

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
    _description = _("Set user properties")

    def get_parser(self, prog_name):
        parser = super(SetUser, self).get_parser(prog_name)
        parser.add_argument(
            'user',
            metavar='<user>',
            help=_('User to modify (name or ID)'),
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('Set user name'),
        )
        parser.add_argument(
            '--domain',
            metavar='<domain>',
            help=_('Domain the user belongs to (name or ID). This can be '
                   'used in case collisions between user names exist.'),
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_('Set default project (name or ID)'),
        )
        common.add_project_domain_option_to_parser(parser)
        parser.add_argument(
            '--password',
            metavar='<password>',
            help=_('Set user password'),
        )
        parser.add_argument(
            '--password-prompt',
            dest="password_prompt",
            action="store_true",
            help=_('Prompt interactively for password'),
        )
        parser.add_argument(
            '--email',
            metavar='<email-address>',
            help=_('Set user email address'),
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('Set user description'),
        )
        enable_group = parser.add_mutually_exclusive_group()
        enable_group.add_argument(
            '--enable',
            action='store_true',
            help=_('Enable user (default)'),
        )
        enable_group.add_argument(
            '--disable',
            action='store_true',
            help=_('Disable user'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        if parsed_args.password_prompt:
            parsed_args.password = utils.get_password(self.app.stdin)

        if '' == parsed_args.password:
            LOG.warning(_("No password was supplied, authentication will fail "
                          "when a user does not have a password."))

        user_str = common._get_token_resource(identity_client, 'user',
                                              parsed_args.user,
                                              parsed_args.domain)
        if parsed_args.domain:
            domain = common.find_domain(identity_client, parsed_args.domain)
            user = utils.find_resource(identity_client.users,
                                       user_str,
                                       domain_id=domain.id)
        else:
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


class SetPasswordUser(command.Command):
    _description = _("Change current user password")

    required_scope = False

    def get_parser(self, prog_name):
        parser = super(SetPasswordUser, self).get_parser(prog_name)
        parser.add_argument(
            '--password',
            metavar='<new-password>',
            help=_('New user password'),
        )
        parser.add_argument(
            '--original-password',
            metavar='<original-password>',
            help=_('Original user password'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        # FIXME(gyee): there are two scenarios:
        #
        # 1. user update password for himself
        # 2. admin update password on behalf of the user. This is an unlikely
        #    scenario because that will require admin knowing the user's
        #    original password which is forbidden under most security
        #    policies.
        #
        # Of the two scenarios above, user either authenticate using its
        # original password or an authentication token. For scenario #1,
        # if user is authenticating with its original password (i.e. passing
        # --os-password argument), we can just make use of it instead of using
        # --original-password or prompting. For scenario #2, admin will need
        # to specify --original-password option or this won't work because
        # --os-password is the admin's own password. In the future if we stop
        # supporting scenario #2 then we can just do this.
        #
        # current_password = (parsed_args.original_password or
        #                     self.app.cloud.password)
        #
        current_password = parsed_args.original_password
        if current_password is None:
            current_password = utils.get_password(
                self.app.stdin, prompt="Current Password:", confirm=False)

        password = parsed_args.password
        if password is None:
            password = utils.get_password(
                self.app.stdin, prompt="New Password:")

        if '' == password:
            LOG.warning(_("No password was supplied, authentication will fail "
                          "when a user does not have a password."))

        identity_client.users.update_password(current_password, password)


class ShowUser(command.ShowOne):
    _description = _("Display user details")

    def get_parser(self, prog_name):
        parser = super(ShowUser, self).get_parser(prog_name)
        parser.add_argument(
            'user',
            metavar='<user>',
            help=_('User to display (name or ID)'),
        )
        parser.add_argument(
            '--domain',
            metavar='<domain>',
            help=_('Domain owning <user> (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        user_str = common._get_token_resource(identity_client, 'user',
                                              parsed_args.user,
                                              parsed_args.domain)
        if parsed_args.domain:
            domain = common.find_domain(identity_client, parsed_args.domain)
            user = utils.find_resource(identity_client.users,
                                       user_str,
                                       domain_id=domain.id)
        else:
            user = utils.find_resource(identity_client.users,
                                       user_str)

        user._info.pop('links')
        return zip(*sorted(six.iteritems(user._info)))
