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

"""Identity v3 Implied Role action implementations"""

import logging

from osc_lib.command import command
import six

from openstackclient.i18n import _


LOG = logging.getLogger(__name__)


def _get_role_ids(identity_client, parsed_args):
    """Return prior and implied role id(s)

    If prior and implied role id(s) are retrievable from identity
    client, return tuple containing them.
    """
    role_id = None
    implied_role_id = None

    roles = identity_client.roles.list()

    for role in roles:
        role_id_or_name = (role.name, role.id)

        if parsed_args.role in role_id_or_name:
            role_id = role.id
        elif parsed_args.implied_role in role_id_or_name:
            implied_role_id = role.id

    return (role_id, implied_role_id)


class CreateImpliedRole(command.ShowOne):

    _description = _("Creates an association between prior and implied roles")

    def get_parser(self, prog_name):
        parser = super(CreateImpliedRole, self).get_parser(prog_name)
        parser.add_argument(
            'role',
            metavar='<role>',
            help=_('Role (name or ID) that implies another role'),
        )
        parser.add_argument(
            '--implied-role',
            metavar='<role>',
            help='<role> (name or ID) implied by another role',
            required=True,
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        (prior_role_id, implied_role_id) = _get_role_ids(
            identity_client, parsed_args)
        response = identity_client.inference_rules.create(
            prior_role_id, implied_role_id)
        response._info.pop('links', None)
        return zip(*sorted([(k, v['id'])
                            for k, v in six.iteritems(response._info)]))


class DeleteImpliedRole(command.Command):

    _description = _("Deletes an association between prior and implied roles")

    def get_parser(self, prog_name):
        parser = super(DeleteImpliedRole, self).get_parser(prog_name)
        parser.add_argument(
            'role',
            metavar='<role>',
            help=_('Role (name or ID) that implies another role'),
        )
        parser.add_argument(
            '--implied-role',
            metavar='<role>',
            help='<role> (name or ID) implied by another role',
            required=True,
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        (prior_role_id, implied_role_id) = _get_role_ids(
            identity_client, parsed_args)
        identity_client.inference_rules.delete(
            prior_role_id, implied_role_id)


class ListImpliedRole(command.Lister):

    _description = _("List implied roles")
    _COLUMNS = ['Prior Role ID', 'Prior Role Name',
                'Implied Role ID', 'Implied Role Name']

    def get_parser(self, prog_name):
        parser = super(ListImpliedRole, self).get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        def _list_implied(response):
            for rule in response:
                for implies in rule.implies:
                    yield (rule.prior_role['id'],
                           rule.prior_role['name'],
                           implies['id'],
                           implies['name'])

        identity_client = self.app.client_manager.identity
        response = identity_client.inference_rules.list_inference_roles()
        return (self._COLUMNS, _list_implied(response))
