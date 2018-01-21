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
import logging

from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils
import six

from openstackclient.i18n import _
from openstackclient.identity import common


LOG = logging.getLogger(__name__)


class CreateApplicationCredential(command.ShowOne):
    _description = _("Create new application credential")

    def get_parser(self, prog_name):
        parser = super(CreateApplicationCredential, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<name>',
            help=_('Name of the application credential'),
        )
        parser.add_argument(
            '--secret',
            metavar='<secret>',
            help=_('Secret to use for authentication (if not provided, one'
                   ' will be generated)'),
        )
        parser.add_argument(
            '--role',
            metavar='<role>',
            action='append',
            default=[],
            help=_('Roles to authorize (name or ID) (repeat option to set'
                   ' multiple values)'),
        )
        parser.add_argument(
            '--expiration',
            metavar='<expiration>',
            help=_('Sets an expiration date for the application credential,'
                   ' format of YYYY-mm-ddTHH:MM:SS (if not provided, the'
                   ' application credential will not expire)'),
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('Application credential description'),
        )
        parser.add_argument(
            '--unrestricted',
            action="store_true",
            help=_('Enable application credential to create and delete other'
                   ' application credentials and trusts (this is potentially'
                   ' dangerous behavior and is disabled by default)'),
        )
        parser.add_argument(
            '--restricted',
            action="store_true",
            help=_('Prohibit application credential from creating and deleting'
                   ' other application credentials and trusts (this is the'
                   ' default behavior)'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        role_ids = []
        for role in parsed_args.role:
            # A user can only create an application credential for themself,
            # not for another user even as an admin, and only on the project to
            # which they are currently scoped with a subset of the role
            # assignments they have on that project. Don't bother trying to
            # look up roles via keystone, just introspect the token.
            role_id = common._get_token_resource(identity_client, "roles",
                                                 role)
            role_ids.append(role_id)

        expires_at = None
        if parsed_args.expiration:
            expires_at = datetime.datetime.strptime(parsed_args.expiration,
                                                    '%Y-%m-%dT%H:%M:%S')

        if parsed_args.restricted:
            unrestricted = False
        else:
            unrestricted = parsed_args.unrestricted

        app_cred_manager = identity_client.application_credentials
        application_credential = app_cred_manager.create(
            parsed_args.name,
            roles=role_ids,
            expires_at=expires_at,
            description=parsed_args.description,
            secret=parsed_args.secret,
            unrestricted=unrestricted,
        )

        application_credential._info.pop('links', None)

        # Format roles into something sensible
        roles = application_credential._info.pop('roles')
        msg = ' '.join(r['name'] for r in roles)
        application_credential._info['roles'] = msg

        return zip(*sorted(six.iteritems(application_credential._info)))


class DeleteApplicationCredential(command.Command):
    _description = _("Delete application credentials(s)")

    def get_parser(self, prog_name):
        parser = super(DeleteApplicationCredential, self).get_parser(prog_name)
        parser.add_argument(
            'application_credential',
            metavar='<application-credential>',
            nargs="+",
            help=_('Application credentials(s) to delete (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        errors = 0
        for ac in parsed_args.application_credential:
            try:
                app_cred = utils.find_resource(
                    identity_client.application_credentials, ac)
                identity_client.application_credentials.delete(app_cred.id)
            except Exception as e:
                errors += 1
                LOG.error(_("Failed to delete application credential with "
                          "name or ID '%(ac)s': %(e)s"),
                          {'ac': ac, 'e': e})

        if errors > 0:
            total = len(parsed_args.application_credential)
            msg = (_("%(errors)s of %(total)s application credentials failed "
                   "to delete.") % {'errors': errors, 'total': total})
            raise exceptions.CommandError(msg)


class ListApplicationCredential(command.Lister):
    _description = _("List application credentials")

    def get_parser(self, prog_name):
        parser = super(ListApplicationCredential, self).get_parser(prog_name)
        parser.add_argument(
            '--user',
            metavar='<user>',
            help=_('User whose application credentials to list (name or ID)'),
        )
        common.add_user_domain_option_to_parser(parser)
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        if parsed_args.user:
            user_id = common.find_user(identity_client,
                                       parsed_args.user,
                                       parsed_args.user_domain).id
        else:
            user_id = None

        columns = ('ID', 'Name', 'Project ID', 'Description', 'Expires At')
        data = identity_client.application_credentials.list(
            user=user_id)
        return (columns,
                (utils.get_item_properties(
                    s, columns,
                    formatters={},
                ) for s in data))


class ShowApplicationCredential(command.ShowOne):
    _description = _("Display application credential details")

    def get_parser(self, prog_name):
        parser = super(ShowApplicationCredential, self).get_parser(prog_name)
        parser.add_argument(
            'application_credential',
            metavar='<application-credential>',
            help=_('Application credential to display (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        app_cred = utils.find_resource(identity_client.application_credentials,
                                       parsed_args.application_credential)

        app_cred._info.pop('links', None)

        # Format roles into something sensible
        roles = app_cred._info.pop('roles')
        msg = ' '.join(r['name'] for r in roles)
        app_cred._info['roles'] = msg

        return zip(*sorted(six.iteritems(app_cred._info)))
