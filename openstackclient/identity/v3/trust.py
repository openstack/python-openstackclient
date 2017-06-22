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
import logging

from keystoneclient import exceptions as identity_exc
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils
import six

from openstackclient.i18n import _
from openstackclient.identity import common


LOG = logging.getLogger(__name__)


class CreateTrust(command.ShowOne):
    _description = _("Create new trust")

    def get_parser(self, prog_name):
        parser = super(CreateTrust, self).get_parser(prog_name)
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
            action='append',
            default=[],
            help=_('Roles to authorize (name or ID) '
                   '(repeat option to set multiple values, required)'),
            required=True
        )
        parser.add_argument(
            '--impersonate',
            dest='impersonate',
            action='store_true',
            default=False,
            help=_('Tokens generated from the trust will represent <trustor>'
                   ' (defaults to False)'),
        )
        parser.add_argument(
            '--expiration',
            metavar='<expiration>',
            help=_('Sets an expiration date for the trust'
                   ' (format of YYYY-mm-ddTHH:MM:SS)'),
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
        identity_client = self.app.client_manager.identity

        # NOTE(stevemar): Find the two users, project and roles that
        # are necessary for making a trust usable, the API dictates that
        # trustee, project and role are optional, but that makes the trust
        # pointless, and trusts are immutable, so let's enforce it at the
        # client level.
        trustor_id = common.find_user(identity_client,
                                      parsed_args.trustor,
                                      parsed_args.trustor_domain).id
        trustee_id = common.find_user(identity_client,
                                      parsed_args.trustee,
                                      parsed_args.trustee_domain).id
        project_id = common.find_project(identity_client,
                                         parsed_args.project,
                                         parsed_args.project_domain).id

        role_ids = []
        for role in parsed_args.role:
            try:
                role_id = utils.find_resource(
                    identity_client.roles,
                    role,
                ).id
            except identity_exc.Forbidden:
                role_id = role
            role_ids.append(role_id)

        expires_at = None
        if parsed_args.expiration:
            expires_at = datetime.datetime.strptime(parsed_args.expiration,
                                                    '%Y-%m-%dT%H:%M:%S')

        trust = identity_client.trusts.create(
            trustee_id, trustor_id,
            impersonation=parsed_args.impersonate,
            project=project_id,
            role_ids=role_ids,
            expires_at=expires_at,
        )

        trust._info.pop('roles_links', None)
        trust._info.pop('links', None)

        # Format roles into something sensible
        roles = trust._info.pop('roles')
        msg = ' '.join(r['name'] for r in roles)
        trust._info['roles'] = msg

        return zip(*sorted(six.iteritems(trust._info)))


class DeleteTrust(command.Command):
    _description = _("Delete trust(s)")

    def get_parser(self, prog_name):
        parser = super(DeleteTrust, self).get_parser(prog_name)
        parser.add_argument(
            'trust',
            metavar='<trust>',
            nargs="+",
            help=_('Trust(s) to delete'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        errors = 0
        for trust in parsed_args.trust:
            try:
                trust_obj = utils.find_resource(identity_client.trusts,
                                                trust)
                identity_client.trusts.delete(trust_obj.id)
            except Exception as e:
                errors += 1
                LOG.error(_("Failed to delete trust with "
                          "name or ID '%(trust)s': %(e)s"),
                          {'trust': trust, 'e': e})

        if errors > 0:
            total = len(parsed_args.trust)
            msg = (_("%(errors)s of %(total)s trusts failed "
                   "to delete.") % {'errors': errors, 'total': total})
            raise exceptions.CommandError(msg)


class ListTrust(command.Lister):
    _description = _("List trusts")

    def take_action(self, parsed_args):
        columns = ('ID', 'Expires At', 'Impersonation', 'Project ID',
                   'Trustee User ID', 'Trustor User ID')
        data = self.app.client_manager.identity.trusts.list()
        return (columns,
                (utils.get_item_properties(
                    s, columns,
                    formatters={},
                ) for s in data))


class ShowTrust(command.ShowOne):
    _description = _("Display trust details")

    def get_parser(self, prog_name):
        parser = super(ShowTrust, self).get_parser(prog_name)
        parser.add_argument(
            'trust',
            metavar='<trust>',
            help=_('Trust to display'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        trust = utils.find_resource(identity_client.trusts,
                                    parsed_args.trust)

        trust._info.pop('roles_links', None)
        trust._info.pop('links', None)

        # Format roles into something sensible
        roles = trust._info.pop('roles')
        msg = ' '.join(r['name'] for r in roles)
        trust._info['roles'] = msg

        return zip(*sorted(six.iteritems(trust._info)))
