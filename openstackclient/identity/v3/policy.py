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
import six
import sys

from cliff import command
from cliff import lister
from cliff import show

from openstackclient.common import utils


class CreatePolicy(show.ShowOne):
    """Create new policy"""

    log = logging.getLogger(__name__ + '.CreatePolicy')

    def get_parser(self, prog_name):
        parser = super(CreatePolicy, self).get_parser(prog_name)
        parser.add_argument(
            '--type',
            metavar='<type>',
            default="application/json",
            help='New MIME type of the policy rules file '
                 '(defaults to application/json)',
        )
        parser.add_argument(
            'rules',
            metavar='<filename>',
            help='New serialized policy rules file',
        )
        return parser

    @utils.log_method(log)
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
    """Delete policy"""

    log = logging.getLogger(__name__ + '.DeletePolicy')

    def get_parser(self, prog_name):
        parser = super(DeletePolicy, self).get_parser(prog_name)
        parser.add_argument(
            'policy',
            metavar='<policy>',
            help='Policy to delete',
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        identity_client.policies.delete(parsed_args.policy)
        return


class ListPolicy(lister.Lister):
    """List policies"""

    log = logging.getLogger(__name__ + '.ListPolicy')

    def get_parser(self, prog_name):
        parser = super(ListPolicy, self).get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help='List additional fields in output',
        )
        return parser

    @utils.log_method(log)
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
    """Set policy properties"""

    log = logging.getLogger(__name__ + '.SetPolicy')

    def get_parser(self, prog_name):
        parser = super(SetPolicy, self).get_parser(prog_name)
        parser.add_argument(
            'policy',
            metavar='<policy>',
            help='Policy to modify',
        )
        parser.add_argument(
            '--type',
            metavar='<type>',
            help='New MIME type of the policy rules file',
        )
        parser.add_argument(
            '--rules',
            metavar='<filename>',
            help='New serialized policy rules file',
        )
        return parser

    @utils.log_method(log)
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

        if not kwargs:
            sys.stdout.write('Policy not updated, no arguments present \n')
            return
        identity_client.policies.update(parsed_args.policy, **kwargs)
        return


class ShowPolicy(show.ShowOne):
    """Display policy details"""

    log = logging.getLogger(__name__ + '.ShowPolicy')

    def get_parser(self, prog_name):
        parser = super(ShowPolicy, self).get_parser(prog_name)
        parser.add_argument(
            'policy',
            metavar='<policy>',
            help='Policy to display',
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        policy = utils.find_resource(identity_client.policies,
                                     parsed_args.policy)

        policy._info.pop('links')
        policy._info.update({'rules': policy._info.pop('blob')})
        return zip(*sorted(six.iteritems(policy._info)))
