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
import typing as ty

from openstack import exceptions as sdk_exc
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _
from openstackclient.identity import common


LOG = logging.getLogger(__name__)


def _format_user(user):
    columns = (
        'default_project_id',
        'domain_id',
        'email',
        'is_enabled',
        'id',
        'name',
        'description',
        'password_expires_at',
    )
    column_headers = (
        'default_project_id',
        'domain_id',
        'email',
        'enabled',
        'id',
        'name',
        'description',
        'password_expires_at',
    )
    return (
        column_headers,
        utils.get_item_properties(user, columns),
    )


def _get_options_for_user(identity_client, parsed_args):
    options: dict[str, ty.Any] = {}
    if parsed_args.ignore_lockout_failure_attempts:
        options['ignore_lockout_failure_attempts'] = True
    if parsed_args.no_ignore_lockout_failure_attempts:
        options['ignore_lockout_failure_attempts'] = False
    if parsed_args.ignore_password_expiry:
        options['ignore_password_expiry'] = True
    if parsed_args.no_ignore_password_expiry:
        options['ignore_password_expiry'] = False
    if parsed_args.ignore_change_password_upon_first_use:
        options['ignore_change_password_upon_first_use'] = True
    if parsed_args.no_ignore_change_password_upon_first_use:
        options['ignore_change_password_upon_first_use'] = False
    if parsed_args.enable_lock_password:
        options['lock_password'] = True
    if parsed_args.disable_lock_password:
        options['lock_password'] = False
    if parsed_args.enable_multi_factor_auth:
        options['multi_factor_auth_enabled'] = True
    if parsed_args.disable_multi_factor_auth:
        options['multi_factor_auth_enabled'] = False
    if parsed_args.multi_factor_auth_rule:
        auth_rules = [
            rule.split(",") for rule in parsed_args.multi_factor_auth_rule
        ]
        if auth_rules:
            options['multi_factor_auth_rules'] = auth_rules
    return options


def _add_user_options(parser):
    # Add additional user options

    parser.add_argument(
        '--ignore-lockout-failure-attempts',
        action="store_true",
        help=_(
            'Opt into ignoring the number of times a user has '
            'authenticated and locking out the user as a result'
        ),
    )
    parser.add_argument(
        '--no-ignore-lockout-failure-attempts',
        action="store_true",
        help=_(
            'Opt out of ignoring the number of times a user has '
            'authenticated and locking out the user as a result'
        ),
    )
    parser.add_argument(
        '--ignore-password-expiry',
        action="store_true",
        help=_(
            'Opt into allowing user to continue using passwords that '
            'may be expired'
        ),
    )
    parser.add_argument(
        '--no-ignore-password-expiry',
        action="store_true",
        help=_(
            'Opt out of allowing user to continue using passwords '
            'that may be expired'
        ),
    )
    parser.add_argument(
        '--ignore-change-password-upon-first-use',
        action="store_true",
        help=_(
            'Control if a user should be forced to change their password '
            'immediately after they log into keystone for the first time. '
            'Opt into ignoring the user to change their password during '
            'first time login in keystone'
        ),
    )
    parser.add_argument(
        '--no-ignore-change-password-upon-first-use',
        action="store_true",
        help=_(
            'Control if a user should be forced to change their password '
            'immediately after they log into keystone for the first time. '
            'Opt out of ignoring the user to change their password during '
            'first time login in keystone'
        ),
    )
    parser.add_argument(
        '--enable-lock-password',
        action="store_true",
        help=_(
            'Disables the ability for a user to change its password '
            'through self-service APIs'
        ),
    )
    parser.add_argument(
        '--disable-lock-password',
        action="store_true",
        help=_(
            'Enables the ability for a user to change its password '
            'through self-service APIs'
        ),
    )
    parser.add_argument(
        '--enable-multi-factor-auth',
        action="store_true",
        help=_('Enables the MFA (Multi Factor Auth)'),
    )
    parser.add_argument(
        '--disable-multi-factor-auth',
        action="store_true",
        help=_('Disables the MFA (Multi Factor Auth)'),
    )
    parser.add_argument(
        '--multi-factor-auth-rule',
        metavar='<rule>',
        action="append",
        default=[],
        help=_(
            'Set multi-factor auth rules. For example, to set a rule '
            'requiring the "password" and "totp" auth methods to be '
            'provided, use: "--multi-factor-auth-rule password,totp". '
            'May be provided multiple times to set different rule '
            'combinations.'
        ),
    )


class CreateUser(command.ShowOne):
    _description = _("Create new user")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
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
        _add_user_options(parser)

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
        identity_client = self.app.client_manager.sdk_connection.identity

        kwargs = {}

        domain_id = None
        if parsed_args.domain:
            domain_id = identity_client.find_domain(
                parsed_args.domain,
                ignore_missing=False,
            ).id
            kwargs['domain_id'] = domain_id

        if parsed_args.project:
            project_domain_id = None
            if parsed_args.project_domain:
                project_domain_id = identity_client.find_domain(
                    parsed_args.project_domain,
                    ignore_missing=False,
                ).id
            kwargs['default_project_id'] = identity_client.find_project(
                parsed_args.project,
                ignore_missing=False,
                domain_id=project_domain_id,
            ).id

        if parsed_args.description:
            kwargs['description'] = parsed_args.description

        if parsed_args.email:
            kwargs['email'] = parsed_args.email

        is_enabled = True
        if parsed_args.disable:
            is_enabled = False

        password = None
        if parsed_args.password:
            password = parsed_args.password
        elif parsed_args.password_prompt:
            password = utils.get_password(self.app.stdin)

        if not parsed_args.password:
            LOG.warning(
                _(
                    "No password was supplied, authentication will fail "
                    "when a user does not have a password."
                )
            )
        options = _get_options_for_user(identity_client, parsed_args)
        if options:
            kwargs['options'] = options

        try:
            user = identity_client.create_user(
                is_enabled=is_enabled,
                name=parsed_args.name,
                password=password,
                **kwargs,
            )
        except sdk_exc.ConflictException:
            if parsed_args.or_show:
                kwargs = {}
                if domain_id:
                    kwargs['domain_id'] = domain_id

                user = identity_client.find_user(
                    parsed_args.name,
                    ignore_missing=False,
                    **kwargs,
                )
                LOG.info(_('Returning existing user %s'), user.name)
            else:
                raise

        return _format_user(user)


class DeleteUser(command.Command):
    _description = _("Delete user(s)")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
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
        identity_client = self.app.client_manager.sdk_connection.identity

        domain = None
        if parsed_args.domain:
            domain = identity_client.find_domain(
                name_or_id=parsed_args.domain,
                ignore_missing=True,
            )
        errors = 0
        for user in parsed_args.users:
            try:
                if domain is not None:
                    user_obj = identity_client.find_user(
                        name_or_id=user,
                        domain_id=domain.id,
                        ignore_missing=False,
                    )
                else:
                    user_obj = identity_client.find_user(
                        name_or_id=user, ignore_missing=False
                    )
                identity_client.delete_user(user_obj.id, ignore_missing=False)
            except Exception as e:
                errors += 1
                LOG.error(
                    _(
                        "Failed to delete user with "
                        "name or ID '%(user)s': %(e)s"
                    ),
                    {'user': user, 'e': e},
                )

        if errors > 0:
            total = len(parsed_args.users)
            msg = _("%(errors)s of %(total)s users failed to delete.") % {
                'errors': errors,
                'total': total,
            }
            raise exceptions.CommandError(msg)


class ListUser(command.Lister):
    _description = _("List users")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
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
        identity_client = self.app.client_manager.sdk_connection.identity

        domain = None
        if parsed_args.domain:
            domain = identity_client.find_domain(
                name_or_id=parsed_args.domain,
            ).id

        group = None
        if parsed_args.group:
            group = identity_client.find_group(
                name_or_id=parsed_args.group,
                domain_id=parsed_args.domain,
                ignore_missing=False,
            ).id

        if parsed_args.project:
            if domain is not None:
                project = identity_client.find_project(
                    name_or_id=parsed_args.project,
                    domain_id=domain,
                    ignore_missing=False,
                ).id
            else:
                project = identity_client.find_project(
                    name_or_id=parsed_args.project,
                    ignore_missing=False,
                ).id

            assignments = identity_client.role_assignments_filter(
                project=project
            )

            # NOTE(stevemar): If a user has more than one role on a project
            # then they will have two entries in the returned data. Since we
            # are looking for any role, let's just track unique user IDs.
            user_ids = set()
            for assignment in assignments:
                if assignment.user:
                    user_ids.add(assignment.user['id'])

            # NOTE(stevemar): Call find_resource once we have unique IDs, so
            # it's fewer trips to the Identity API, then collect the data.
            data = []
            for user_id in user_ids:
                user = identity_client.find_user(user_id, ignore_missing=False)
                data.append(user)

        elif parsed_args.group:
            data = identity_client.group_users(
                domain_id=domain,
                group=group,
            )
        else:
            data = identity_client.users(
                domain_id=domain,
            )

        # Column handling
        if parsed_args.long:
            columns = [
                'ID',
                'Name',
                'Default Project Id',
                'Domain Id',
                'Description',
                'Email',
                'Is Enabled',
            ]
            column_headers = copy.deepcopy(columns)
            column_headers[2] = 'Project'
            column_headers[3] = 'Domain'
            column_headers[6] = 'Enabled'
        else:
            columns = ['ID', 'Name']
            column_headers = columns

        return (
            column_headers,
            (
                utils.get_item_properties(
                    s,
                    columns,
                    formatters={},
                )
                for s in data
            ),
        )


class SetUser(command.Command):
    _description = _("Set user properties")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
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
            help=_(
                'Domain the user belongs to (name or ID). This can be '
                'used in case collisions between user names exist.'
            ),
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
        _add_user_options(parser)

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
        identity_client = self.app.client_manager.sdk_connection.identity

        if parsed_args.password_prompt:
            parsed_args.password = utils.get_password(self.app.stdin)

        if '' == parsed_args.password:
            LOG.warning(
                _(
                    "No password was supplied, authentication will fail "
                    "when a user does not have a password."
                )
            )

        user_str = common._get_token_resource(
            identity_client, 'user', parsed_args.user, parsed_args.domain
        )
        if parsed_args.domain:
            domain = identity_client.find_domain(
                name_or_id=parsed_args.domain,
                ignore_missing=False,
            )
            user = identity_client.find_user(
                name_or_id=user_str,
                domain_id=domain.id,
                ignore_missing=False,
            )
        else:
            user = identity_client.find_user(
                name_or_id=parsed_args.user,
                ignore_missing=False,
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
            project_domain_id = None
            if parsed_args.project_domain:
                project_domain_id = identity_client.find_domain(
                    name_or_id=parsed_args.project_domain,
                    ignore_missing=False,
                ).id
            project_id = identity_client.find_project(
                name_or_id=parsed_args.project,
                ignore_missing=False,
                domain_id=project_domain_id,
            ).id
            kwargs['default_project_id'] = project_id
        kwargs['is_enabled'] = user.is_enabled
        if parsed_args.enable:
            kwargs['is_enabled'] = True
        if parsed_args.disable:
            kwargs['is_enabled'] = False

        options = _get_options_for_user(identity_client, parsed_args)
        if options:
            kwargs['options'] = options

        identity_client.update_user(user=user, **kwargs)


class SetPasswordUser(command.Command):
    _description = _("Change current user password")

    required_scope = False

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
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
        identity_client = self.app.client_manager.sdk_connection.identity

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
                self.app.stdin, prompt="Current Password:", confirm=False
            )

        password = parsed_args.password
        if password is None:
            password = utils.get_password(
                self.app.stdin, prompt="New Password:"
            )

        if '' == password:
            LOG.warning(
                _(
                    "No password was supplied, authentication will fail "
                    "when a user does not have a password."
                )
            )

        identity_client.update_user(
            current_password=current_password, password=password
        )


class ShowUser(command.ShowOne):
    _description = _("Display user details")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
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
        identity_client = self.app.client_manager.sdk_connection.identity

        user_str = common._get_token_resource(
            identity_client, 'user', parsed_args.user, parsed_args.domain
        )

        domain = None
        if parsed_args.domain:
            domain = identity_client.find_domain(
                name_or_id=parsed_args.domain,
                ignore_missing=True,
            )
        if domain:
            user = identity_client.find_user(
                name_or_id=user_str,
                domain_id=domain.id,
                ignore_missing=False,
            )
        else:
            user = identity_client.find_user(
                name_or_id=user_str,
                ignore_missing=False,
            )

        return _format_user(user)
