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

"""Identity v3 Trust action implementations"""

import datetime
import itertools
import logging

from openstack import exceptions as sdk_exceptions
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _
from openstackclient.identity import common


LOG = logging.getLogger(__name__)


def _format_trust(trust):
    columns = (
        'expires_at',
        'id',
        'is_impersonation',
        'project_id',
        'redelegated_trust_id',
        'redelegation_count',
        'remaining_uses',
        'roles',
        'trustee_user_id',
        'trustor_user_id',
    )
    return (
        columns,
        utils.get_item_properties(trust, columns),
    )


class CreateTrust(command.ShowOne):
    _description = _("Create new trust")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'trustor',
            metavar='<trustor-user>',
            help=_('User that is delegating authorization (name or ID)'),
        )
        parser.add_argument(
            'trustee',
            metavar='<trustee-user>',
            help=_('User that is assuming authorization (name or ID)'),
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            required=True,
            help=_('Project being delegated (name or ID) (required)'),
        )
        parser.add_argument(
            '--role',
            metavar='<role>',
            dest='roles',
            action='append',
            default=[],
            help=_(
                'Roles to authorize (name or ID) '
                '(repeat option to set multiple values, required)'
            ),
            required=True,
        )
        parser.add_argument(
            '--impersonate',
            dest='is_impersonation',
            action='store_true',
            default=False,
            help=_(
                'Tokens generated from the trust will represent <trustor>'
                ' (defaults to False)'
            ),
        )
        parser.add_argument(
            '--expiration',
            metavar='<expiration>',
            help=_(
                'Sets an expiration date for the trust'
                ' (format of YYYY-mm-ddTHH:MM:SS)'
            ),
        )
        common.add_project_domain_option_to_parser(parser)
        parser.add_argument(
            '--trustor-domain',
            metavar='<trustor-domain>',
            help=_('Domain that contains <trustor> (name or ID)'),
        )
        parser.add_argument(
            '--trustee-domain',
            metavar='<trustee-domain>',
            help=_('Domain that contains <trustee> (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.sdk_connection.identity

        kwargs = {}

        # NOTE(stevemar): Find the two users, project and roles that
        # are necessary for making a trust usable, the API dictates that
        # trustee, project and role are optional, but that makes the trust
        # pointless, and trusts are immutable, so let's enforce it at the
        # client level.
        try:
            if parsed_args.trustor_domain:
                trustor_domain_id = identity_client.find_domain(
                    parsed_args.trustor_domain, ignore_missing=False
                ).id
                trustor_id = identity_client.find_user(
                    parsed_args.trustor,
                    ignore_missing=False,
                    domain_id=trustor_domain_id,
                ).id
            else:
                trustor_id = identity_client.find_user(
                    parsed_args.trustor, ignore_missing=False
                ).id
            kwargs['trustor_user_id'] = trustor_id
        except sdk_exceptions.ForbiddenException:
            kwargs['trustor_user_id'] = parsed_args.trustor

        try:
            if parsed_args.trustee_domain:
                trustee_domain_id = identity_client.find_domain(
                    parsed_args.trustee_domain, ignore_missing=False
                ).id
                trustee_id = identity_client.find_user(
                    parsed_args.trustee,
                    ignore_missing=False,
                    domain_id=trustee_domain_id,
                ).id
            else:
                trustee_id = identity_client.find_user(
                    parsed_args.trustee, ignore_missing=False
                ).id
            kwargs['trustee_user_id'] = trustee_id
        except sdk_exceptions.ForbiddenException:
            kwargs['trustee_user_id'] = parsed_args.trustee

        try:
            if parsed_args.project_domain:
                project_domain_id = identity_client.find_domain(
                    parsed_args.project_domain, ignore_missing=False
                ).id
                project_id = identity_client.find_project(
                    parsed_args.project,
                    ignore_missing=False,
                    domain_id=project_domain_id,
                ).id
            else:
                project_id = identity_client.find_project(
                    parsed_args.project, ignore_missing=False
                ).id
            kwargs['project_id'] = project_id
        except sdk_exceptions.ForbiddenException:
            kwargs['project_id'] = parsed_args.project

        roles = []
        for role in parsed_args.roles:
            try:
                role_id = identity_client.find_role(role).id
            except sdk_exceptions.ForbiddenException:
                role_id = role
            roles.append({"id": role_id})
        kwargs['roles'] = roles

        if parsed_args.expiration:
            expires_at = datetime.datetime.strptime(
                parsed_args.expiration, '%Y-%m-%dT%H:%M:%S'
            )
            kwargs['expires_at'] = expires_at

        kwargs['impersonation'] = bool(parsed_args.is_impersonation)

        trust = identity_client.create_trust(**kwargs)

        return _format_trust(trust)


class DeleteTrust(command.Command):
    _description = _("Delete trust(s)")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'trust',
            metavar='<trust>',
            nargs="+",
            help=_('Trust(s) to delete'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.sdk_connection.identity

        errors = 0
        for trust in parsed_args.trust:
            try:
                trust_obj = identity_client.find_trust(
                    trust, ignore_missing=False
                )
                identity_client.delete_trust(trust_obj.id)
            except Exception as e:
                errors += 1
                LOG.error(
                    _(
                        "Failed to delete trust with "
                        "name or ID '%(trust)s': %(e)s"
                    ),
                    {'trust': trust, 'e': e},
                )

        if errors > 0:
            total = len(parsed_args.trust)
            msg = _("%(errors)s of %(total)s trusts failed to delete.") % {
                'errors': errors,
                'total': total,
            }
            raise exceptions.CommandError(msg)


class ListTrust(command.Lister):
    _description = _("List trusts")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--trustor',
            metavar='<trustor-user>',
            help=_('Trustor user to filter (name or ID)'),
        )
        parser.add_argument(
            '--trustee',
            metavar='<trustee-user>',
            help=_('Trustee user to filter (name or ID)'),
        )
        parser.add_argument(
            '--trustor-domain',
            metavar='<trustor-domain>',
            help=_('Domain that contains <trustor> (name or ID)'),
        )
        parser.add_argument(
            '--trustee-domain',
            metavar='<trustee-domain>',
            help=_('Domain that contains <trustee> (name or ID)'),
        )
        parser.add_argument(
            '--auth-user',
            action="store_true",
            dest='authuser',
            help=_('Only list trusts related to the authenticated user'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.sdk_connection.identity
        auth_ref = self.app.client_manager.auth_ref

        if parsed_args.authuser and any(
            [
                parsed_args.trustor,
                parsed_args.trustor_domain,
                parsed_args.trustee,
                parsed_args.trustee_domain,
            ]
        ):
            msg = _("--authuser cannot be used with --trustee or --trustor")
            raise exceptions.CommandError(msg)

        if parsed_args.trustee_domain and not parsed_args.trustee:
            msg = _("Using --trustee-domain mandates the use of --trustee")
            raise exceptions.CommandError(msg)

        if parsed_args.trustor_domain and not parsed_args.trustor:
            msg = _("Using --trustor-domain mandates the use of --trustor")
            raise exceptions.CommandError(msg)

        if parsed_args.authuser:
            # We need two calls here as we want trusts with
            # either the trustor or the trustee set to current user
            # using a single call would give us trusts with both
            # trustee and trustor set to current user
            data = list(
                {
                    x.id: x
                    for x in itertools.chain(
                        identity_client.trusts(
                            trustor_user_id=auth_ref.user_id
                        ),
                        identity_client.trusts(
                            trustee_user_id=auth_ref.user_id
                        ),
                    )
                }.values()
            )
        else:
            trustor = None
            if parsed_args.trustor:
                try:
                    if parsed_args.trustor_domain:
                        trustor_domain_id = identity_client.find_domain(
                            parsed_args.trustor_domain, ignore_missing=False
                        ).id
                        trustor_id = identity_client.find_user(
                            parsed_args.trustor,
                            ignore_missing=False,
                            domain_id=trustor_domain_id,
                        ).id
                    else:
                        trustor_id = identity_client.find_user(
                            parsed_args.trustor, ignore_missing=False
                        ).id
                    trustor = trustor_id
                except sdk_exceptions.ForbiddenException:
                    trustor = parsed_args.trustor

            trustee = None
            if parsed_args.trustee:
                try:
                    if parsed_args.trustee_domain:
                        trustee_domain_id = identity_client.find_domain(
                            parsed_args.trustee_domain, ignore_missing=False
                        ).id
                        trustee_id = identity_client.find_user(
                            parsed_args.trustee,
                            ignore_missing=False,
                            domain_id=trustee_domain_id,
                        ).id
                    else:
                        trustee_id = identity_client.find_user(
                            parsed_args.trustee, ignore_missing=False
                        ).id
                    trustee = trustee_id
                except sdk_exceptions.ForbiddenException:
                    trustee = parsed_args.trustee

            data = identity_client.trusts(
                trustor_user_id=trustor,
                trustee_user_id=trustee,
            )

        column_headers = (
            'ID',
            'Expires At',
            'Impersonation',
            'Project ID',
            'Trustee User ID',
            'Trustor User ID',
        )
        columns = (
            'id',
            'expires_at',
            'is_impersonation',
            'project_id',
            'trustee_user_id',
            'trustor_user_id',
        )

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


class ShowTrust(command.ShowOne):
    _description = _("Display trust details")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'trust',
            metavar='<trust>',
            help=_('Trust to display'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.sdk_connection.identity
        trust = identity_client.find_trust(
            parsed_args.trust, ignore_missing=False
        )

        return _format_trust(trust)
