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

"""Identity v3 Policy action implementations"""

import logging

from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils
import six

from openstackclient.i18n import _


LOG = logging.getLogger(__name__)


class CreatePolicy(command.ShowOne):
    _description = _("Create new policy")

    def get_parser(self, prog_name):
        parser = super(CreatePolicy, self).get_parser(prog_name)
        parser.add_argument(
            '--type',
            metavar='<type>',
            default="application/json",
            help=_('New MIME type of the policy rules file '
                   '(defaults to application/json)'),
        )
        parser.add_argument(
            'rules',
            metavar='<filename>',
            help=_('New serialized policy rules file'),
        )
        return parser

    def take_action(self, parsed_args):
        blob = utils.read_blob_file_contents(parsed_args.rules)

        identity_client = self.app.client_manager.identity
        policy = identity_client.policies.create(
            blob=blob, type=parsed_args.type
        )

        policy._info.pop('links')
        policy._info.update({'rules': policy._info.pop('blob')})
        return zip(*sorted(six.iteritems(policy._info)))


class DeletePolicy(command.Command):
    _description = _("Delete policy(s)")

    def get_parser(self, prog_name):
        parser = super(DeletePolicy, self).get_parser(prog_name)
        parser.add_argument(
            'policy',
            metavar='<policy>',
            nargs='+',
            help=_('Policy(s) to delete'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        result = 0
        for i in parsed_args.policy:
            try:
                identity_client.policies.delete(i)
            except Exception as e:
                result += 1
                LOG.error(_("Failed to delete policy with name or "
                          "ID '%(policy)s': %(e)s"), {'policy': i, 'e': e})

        if result > 0:
            total = len(parsed_args.policy)
            msg = (_("%(result)s of %(total)s policys failed "
                   "to delete.") % {'result': result, 'total': total})
            raise exceptions.CommandError(msg)


class ListPolicy(command.Lister):
    _description = _("List policies")

    def get_parser(self, prog_name):
        parser = super(ListPolicy, self).get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_('List additional fields in output'),
        )
        return parser

    def take_action(self, parsed_args):
        if parsed_args.long:
            columns = ('ID', 'Type', 'Blob')
            column_headers = ('ID', 'Type', 'Rules')
        else:
            columns = ('ID', 'Type')
            column_headers = columns
        data = self.app.client_manager.identity.policies.list()
        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                    formatters={},
                ) for s in data))


class SetPolicy(command.Command):
    _description = _("Set policy properties")

    def get_parser(self, prog_name):
        parser = super(SetPolicy, self).get_parser(prog_name)
        parser.add_argument(
            'policy',
            metavar='<policy>',
            help=_('Policy to modify'),
        )
        parser.add_argument(
            '--type',
            metavar='<type>',
            help=_('New MIME type of the policy rules file'),
        )
        parser.add_argument(
            '--rules',
            metavar='<filename>',
            help=_('New serialized policy rules file'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        blob = None

        if parsed_args.rules:
            blob = utils.read_blob_file_contents(parsed_args.rules)

        kwargs = {}
        if blob:
            kwargs['blob'] = blob
        if parsed_args.type:
            kwargs['type'] = parsed_args.type

        identity_client.policies.update(parsed_args.policy, **kwargs)


class ShowPolicy(command.ShowOne):
    _description = _("Display policy details")

    def get_parser(self, prog_name):
        parser = super(ShowPolicy, self).get_parser(prog_name)
        parser.add_argument(
            'policy',
            metavar='<policy>',
            help=_('Policy to display'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        policy = utils.find_resource(identity_client.policies,
                                     parsed_args.policy)

        policy._info.pop('links')
        policy._info.update({'rules': policy._info.pop('blob')})
        return zip(*sorted(six.iteritems(policy._info)))
