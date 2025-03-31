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

"""Identity v3 Credential action implementations"""

import logging

from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _
from openstackclient.identity import common


LOG = logging.getLogger(__name__)


def _format_credential(credential):
    columns = (
        'blob',
        'id',
        'project_id',
        'type',
        'user_id',
    )
    return (
        columns,
        utils.get_item_properties(
            credential,
            columns,
        ),
    )


class CreateCredential(command.ShowOne):
    _description = _("Create new credential")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'user',
            metavar='<user>',
            help=_('user that owns the credential (name or ID)'),
        )
        parser.add_argument(
            '--type',
            default="cert",
            metavar='<type>',
            help=_('New credential type: cert, ec2, totp and so on'),
        )
        parser.add_argument(
            'data',
            metavar='<data>',
            help=_('New credential data'),
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_(
                'Project which limits the scope of the credential (name or ID)'
            ),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.sdk_connection.identity
        user_id = identity_client.find_user(
            parsed_args.user, ignore_missing=False
        ).id
        if parsed_args.project:
            project = identity_client.find_project(
                parsed_args.project, ignore_missing=False
            ).id
        else:
            project = None
        credential = identity_client.create_credential(
            user_id=user_id,
            type=parsed_args.type,
            blob=parsed_args.data,
            project_id=project,
        )

        return _format_credential(credential)


class DeleteCredential(command.Command):
    _description = _("Delete credential(s)")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'credential',
            metavar='<credential-id>',
            nargs='+',
            help=_('ID of credential(s) to delete'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.sdk_connection.identity
        result = 0
        for i in parsed_args.credential:
            try:
                identity_client.delete_credential(i)
            except Exception as e:
                result += 1
                LOG.error(
                    _(
                        "Failed to delete credentials with "
                        "ID '%(credential)s': %(e)s"
                    ),
                    {'credential': i, 'e': e},
                )

        if result > 0:
            total = len(parsed_args.credential)
            msg = _("%(result)s of %(total)s credential failed to delete.") % {
                'result': result,
                'total': total,
            }
            raise exceptions.CommandError(msg)


class ListCredential(command.Lister):
    _description = _("List credentials")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--user',
            metavar='<user>',
            help=_('Filter credentials by <user> (name or ID)'),
        )
        common.add_user_domain_option_to_parser(parser)
        parser.add_argument(
            '--type',
            metavar='<type>',
            help=_('Filter credentials by type: cert, ec2, totp and so on'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.sdk_connection.identity

        kwargs = {}
        if parsed_args.user:
            domain_id = None
            if parsed_args.user_domain:
                domain_id = identity_client.find_domain(
                    parsed_args.user_domain, ignore_missing=False
                )
            user_id = identity_client.find_user(
                parsed_args.user, domain_id=domain_id, ignore_missing=False
            ).id
            kwargs["user_id"] = user_id

        if parsed_args.type:
            kwargs["type"] = parsed_args.type

        columns = ('ID', 'Type', 'User ID', 'Blob', 'Project ID')
        column_headers = ('ID', 'Type', 'User ID', 'Data', 'Project ID')
        data = identity_client.credentials(**kwargs)

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


class SetCredential(command.Command):
    _description = _("Set credential properties")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'credential',
            metavar='<credential-id>',
            help=_('ID of credential to change'),
        )
        parser.add_argument(
            '--user',
            metavar='<user>',
            required=True,
            help=_('User that owns the credential (name or ID)'),
        )
        parser.add_argument(
            '--type',
            metavar='<type>',
            required=True,
            help=_('New credential type: cert, ec2, totp and so on'),
        )
        parser.add_argument(
            '--data',
            metavar='<data>',
            required=True,
            help=_('New credential data'),
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_(
                'Project which limits the scope of the credential (name or ID)'
            ),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.sdk_connection.identity

        user_id = identity_client.find_user(
            parsed_args.user, ignore_missing=False
        ).id

        if parsed_args.project:
            project = identity_client.find_project(
                parsed_args.project, ignore_missing=False
            ).id
        else:
            project = None

        identity_client.update_credential(
            parsed_args.credential,
            user=user_id,
            type=parsed_args.type,
            blob=parsed_args.data,
            project=project,
        )


class ShowCredential(command.ShowOne):
    _description = _("Display credential details")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'credential',
            metavar='<credential-id>',
            help=_('ID of credential to display'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.sdk_connection.identity
        credential = identity_client.get_credential(parsed_args.credential)

        return _format_credential(credential)
