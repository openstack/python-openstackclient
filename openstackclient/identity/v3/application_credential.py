#   Copyright 2018 SUSE Linux GmbH
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

"""Identity v3 Application Credential action implementations"""

import datetime
import json
import logging
import uuid

from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _
from openstackclient.identity import common


LOG = logging.getLogger(__name__)


# TODO(stephenfin): Move this to osc_lib since it's useful elsewhere
def is_uuid_like(value) -> bool:
    """Returns validation of a value as a UUID.

    :param val: Value to verify
    :type val: string
    :returns: bool

    .. versionchanged:: 1.1.1
       Support non-lowercase UUIDs.
    """
    try:
        formatted_value = (
            value.replace('urn:', '')
            .replace('uuid:', '')
            .strip('{}')
            .replace('-', '')
            .lower()
        )
        return str(uuid.UUID(value)).replace('-', '') == formatted_value
    except (TypeError, ValueError, AttributeError):
        return False


class CreateApplicationCredential(command.ShowOne):
    _description = _("Create new application credential")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<name>',
            help=_('Name of the application credential'),
        )
        parser.add_argument(
            '--secret',
            metavar='<secret>',
            help=_(
                'Secret to use for authentication (if not provided, one'
                ' will be generated)'
            ),
        )
        parser.add_argument(
            '--role',
            metavar='<role>',
            action='append',
            default=[],
            help=_(
                'Roles to authorize (name or ID) (repeat option to set'
                ' multiple values)'
            ),
        )
        parser.add_argument(
            '--expiration',
            metavar='<expiration>',
            help=_(
                'Sets an expiration date for the application credential,'
                ' format of YYYY-mm-ddTHH:MM:SS (if not provided, the'
                ' application credential will not expire)'
            ),
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('Application credential description'),
        )
        parser.add_argument(
            '--unrestricted',
            action="store_true",
            help=_(
                'Enable application credential to create and delete other'
                ' application credentials and trusts (this is potentially'
                ' dangerous behavior and is disabled by default)'
            ),
        )
        parser.add_argument(
            '--restricted',
            action="store_true",
            help=_(
                'Prohibit application credential from creating and deleting'
                ' other application credentials and trusts (this is the'
                ' default behavior)'
            ),
        )
        parser.add_argument(
            '--access-rules',
            metavar='<access-rules>',
            help=_(
                'Either a string or file path containing a JSON-formatted '
                'list of access rules, each containing a request method, '
                'path, and service, for example '
                '\'[{"method": "GET", '
                '"path": "/v2.1/servers", '
                '"service": "compute"}]\''
            ),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.sdk_connection.identity
        conn = self.app.client_manager.sdk_connection
        user_id = conn.config.get_auth().get_user_id(conn.identity)

        role_ids = []
        for role in parsed_args.role:
            if is_uuid_like(role):
                role_ids.append({'id': role})
            else:
                role_ids.append({'name': role})

        expires_at = None
        if parsed_args.expiration:
            expires_at = datetime.datetime.strptime(
                parsed_args.expiration, '%Y-%m-%dT%H:%M:%S'
            )

        if parsed_args.restricted:
            unrestricted = False
        else:
            unrestricted = parsed_args.unrestricted

        if parsed_args.access_rules:
            try:
                access_rules = json.loads(parsed_args.access_rules)
            except ValueError:
                try:
                    with open(parsed_args.access_rules) as f:
                        access_rules = json.load(f)
                except OSError:
                    msg = _(
                        "Access rules is not valid JSON string or file does"
                        " not exist."
                    )
                    raise exceptions.CommandError(msg)
        else:
            access_rules = []

        application_credential = identity_client.create_application_credential(
            user_id,
            parsed_args.name,
            roles=role_ids,
            expires_at=expires_at,
            description=parsed_args.description,
            secret=parsed_args.secret,
            unrestricted=unrestricted,
            access_rules=access_rules,
        )

        # Format roles into something sensible
        if application_credential['roles']:
            roles = application_credential['roles']
            msg = ' '.join(r['name'] for r in roles)
            application_credential['roles'] = msg

        columns = (
            'id',
            'name',
            'description',
            'project_id',
            'roles',
            'unrestricted',
            'access_rules',
            'expires_at',
            'secret',
        )
        return (
            columns,
            (
                utils.get_dict_properties(
                    application_credential,
                    columns,
                )
            ),
        )


class DeleteApplicationCredential(command.Command):
    _description = _("Delete application credentials(s)")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'application_credential',
            metavar='<application-credential>',
            nargs="+",
            help=_('Application credentials(s) to delete (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.sdk_connection.identity
        conn = self.app.client_manager.sdk_connection
        user_id = conn.config.get_auth().get_user_id(conn.identity)

        errors = 0
        for ac in parsed_args.application_credential:
            try:
                app_cred = identity_client.find_application_credential(
                    user_id, ac
                )
                identity_client.delete_application_credential(
                    user_id, app_cred.id
                )
            except Exception as e:
                errors += 1
                LOG.error(
                    _(
                        "Failed to delete application credential with "
                        "name or ID '%(ac)s': %(e)s"
                    ),
                    {'ac': ac, 'e': e},
                )

        if errors > 0:
            total = len(parsed_args.application_credential)
            msg = _(
                "%(errors)s of %(total)s application credentials failed "
                "to delete."
            ) % {'errors': errors, 'total': total}
            raise exceptions.CommandError(msg)


class ListApplicationCredential(command.Lister):
    _description = _("List application credentials")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--user',
            metavar='<user>',
            help=_('User whose application credentials to list (name or ID)'),
        )
        common.add_user_domain_option_to_parser(parser)
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.sdk_connection.identity
        if parsed_args.user:
            user_id = common.find_user(
                identity_client, parsed_args.user, parsed_args.user_domain
            ).id
        else:
            conn = self.app.client_manager.sdk_connection
            user_id = conn.config.get_auth().get_user_id(conn.identity)

        data = identity_client.application_credentials(user=user_id)

        data_formatted = []
        for ac in data:
            # Format roles into something sensible
            roles = ac['roles']
            msg = ' '.join(r['name'] for r in roles)
            ac['roles'] = msg

            data_formatted.append(ac)

        columns = (
            'ID',
            'Name',
            'Description',
            'Project ID',
            'Roles',
            'Unrestricted',
            'Access Rules',
            'Expires At',
        )
        return (
            columns,
            (
                utils.get_item_properties(
                    s,
                    columns,
                    formatters={},
                )
                for s in data_formatted
            ),
        )


class ShowApplicationCredential(command.ShowOne):
    _description = _("Display application credential details")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'application_credential',
            metavar='<application-credential>',
            help=_('Application credential to display (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.sdk_connection.identity
        conn = self.app.client_manager.sdk_connection
        user_id = conn.config.get_auth().get_user_id(conn.identity)

        app_cred = identity_client.find_application_credential(
            user_id, parsed_args.application_credential
        )

        # Format roles into something sensible
        roles = app_cred['roles']
        msg = ' '.join(r['name'] for r in roles)
        app_cred['roles'] = msg

        columns = (
            'id',
            'name',
            'description',
            'project_id',
            'roles',
            'unrestricted',
            'access_rules',
            'expires_at',
        )
        return (
            columns,
            (
                utils.get_dict_properties(
                    app_cred,
                    columns,
                )
            ),
        )
