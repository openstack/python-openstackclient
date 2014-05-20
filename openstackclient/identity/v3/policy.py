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
    """Create policy command"""

    log = logging.getLogger(__name__ + '.CreatePolicy')

    def get_parser(self, prog_name):
        parser = super(CreatePolicy, self).get_parser(prog_name)
        parser.add_argument(
            '--type',
            metavar='<policy-type>',
            default="application/json",
            help='New MIME type of the policy blob - i.e.: application/json',
        )
        parser.add_argument(
            'blob_file',
            metavar='<blob-file>',
            help='New policy rule set itself, as a serialized blob, in a file',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)', parsed_args)
        blob = utils.read_blob_file_contents(parsed_args.blob_file)

        identity_client = self.app.client_manager.identity
        policy = identity_client.policies.create(
            blob=blob, type=parsed_args.type
        )

        return zip(*sorted(six.iteritems(policy._info)))


class DeletePolicy(command.Command):
    """Delete policy command"""

    log = logging.getLogger(__name__ + '.DeletePolicy')

    def get_parser(self, prog_name):
        parser = super(DeletePolicy, self).get_parser(prog_name)
        parser.add_argument(
            'policy',
            metavar='<policy-id>',
            help='ID of policy to delete',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)', parsed_args)
        identity_client = self.app.client_manager.identity
        identity_client.policies.delete(parsed_args.policy)
        return


class ListPolicy(lister.Lister):
    """List policy command"""

    log = logging.getLogger(__name__ + '.ListPolicy')

    def get_parser(self, prog_name):
        parser = super(ListPolicy, self).get_parser(prog_name)
        parser.add_argument(
            '--include-blob',
            action='store_true',
            default=False,
            help='Additional fields are listed in output',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)', parsed_args)
        if parsed_args.include_blob:
            columns = ('ID', 'Type', 'Blob')
        else:
            columns = ('ID', 'Type')
        data = self.app.client_manager.identity.policies.list()
        return (columns,
                (utils.get_item_properties(
                    s, columns,
                    formatters={},
                ) for s in data))


class SetPolicy(command.Command):
    """Set policy command"""

    log = logging.getLogger(__name__ + '.SetPolicy')

    def get_parser(self, prog_name):
        parser = super(SetPolicy, self).get_parser(prog_name)
        parser.add_argument(
            'policy',
            metavar='<policy-id>',
            help='ID of policy to change',
        )
        parser.add_argument(
            '--type',
            metavar='<policy-type>',
            help='New MIME Type of the policy blob - i.e.: application/json',
        )
        parser.add_argument(
            '--blob-file',
            metavar='<blob_file>',
            help='New policy rule set itself, as a serialized blob, in a file',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)', parsed_args)
        identity_client = self.app.client_manager.identity
        blob = None

        if parsed_args.blob_file:
            blob = utils.read_blob_file_contents(parsed_args.blob_file)

        kwargs = {}
        if blob:
            kwargs['blob'] = blob
        if parsed_args.type:
            kwargs['type'] = parsed_args.type

        if not kwargs:
            sys.stdout.write("Policy not updated, no arguments present \n")
            return
        identity_client.policies.update(parsed_args.policy, **kwargs)
        return


class ShowPolicy(show.ShowOne):
    """Show policy command"""

    log = logging.getLogger(__name__ + '.ShowPolicy')

    def get_parser(self, prog_name):
        parser = super(ShowPolicy, self).get_parser(prog_name)
        parser.add_argument(
            'policy',
            metavar='<policy-id>',
            help='ID of policy to display',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)', parsed_args)
        identity_client = self.app.client_manager.identity
        policy = utils.find_resource(identity_client.policies,
                                     parsed_args.policy)

        return zip(*sorted(six.iteritems(policy._info)))
