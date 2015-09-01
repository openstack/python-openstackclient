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
import six
import sys

from cliff import command
from cliff import lister
from cliff import show

from openstackclient.common import utils


class CreateCredential(show.ShowOne):
    """Create credential command"""

    log = logging.getLogger(__name__ + '.CreateCredential')

    def get_parser(self, prog_name):
        parser = super(CreateCredential, self).get_parser(prog_name)
        parser.add_argument(
            'user',
            metavar='<user>',
            help='Name or ID of user that owns the credential',
        )
        parser.add_argument(
            '--type',
            default="cert",
            metavar='<type>',
            choices=['ec2', 'cert'],
            help='New credential type',
        )
        parser.add_argument(
            'data',
            metavar='<data>',
            help='New credential data',
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help='Project name or ID which limits the scope of the credential',
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        user_id = utils.find_resource(identity_client.users,
                                      parsed_args.user).id
        if parsed_args.project:
            project = utils.find_resource(identity_client.projects,
                                          parsed_args.project).id
        else:
            project = None
        credential = identity_client.credentials.create(
            user=user_id,
            type=parsed_args.type,
            blob=parsed_args.data,
            project=project)

        credential._info.pop('links')
        return zip(*sorted(six.iteritems(credential._info)))


class DeleteCredential(command.Command):
    """Delete credential command"""

    log = logging.getLogger(__name__ + '.DeleteCredential')

    def get_parser(self, prog_name):
        parser = super(DeleteCredential, self).get_parser(prog_name)
        parser.add_argument(
            'credential',
            metavar='<credential-id>',
            help='ID of credential to delete',
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        identity_client.credentials.delete(parsed_args.credential)
        return


class ListCredential(lister.Lister):
    """List credential command"""

    log = logging.getLogger(__name__ + '.ListCredential')

    @utils.log_method(log)
    def take_action(self, parsed_args):
        columns = ('ID', 'Type', 'User ID', 'Blob', 'Project ID')
        column_headers = ('ID', 'Type', 'User ID', 'Data', 'Project ID')
        data = self.app.client_manager.identity.credentials.list()
        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                    formatters={},
                ) for s in data))


class SetCredential(command.Command):
    """Set credential command"""

    log = logging.getLogger(__name__ + '.SetCredential')

    def get_parser(self, prog_name):
        parser = super(SetCredential, self).get_parser(prog_name)
        parser.add_argument(
            'credential',
            metavar='<credential-id>',
            help='ID of credential to change',
        )
        parser.add_argument(
            '--user',
            metavar='<user>',
            help='Name or ID of user that owns the credential',
        )
        parser.add_argument(
            '--type',
            metavar='<type>',
            choices=['ec2', 'cert'],
            help='New credential type',
        )
        parser.add_argument(
            '--data',
            metavar='<data>',
            help='New credential data',
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help='Project name or ID which limits the scope of the credential',
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        kwargs = {}
        if parsed_args.user:
            user_id = utils.find_resource(identity_client.users,
                                          parsed_args.user).id
            if user_id:
                kwargs['user'] = user_id
        if parsed_args.type:
            kwargs['type'] = parsed_args.type
        if parsed_args.data:
            kwargs['data'] = parsed_args.data
        if parsed_args.project:
            project = utils.find_resource(identity_client.projects,
                                          parsed_args.project).id
            kwargs['project'] = project

        if not kwargs:
            sys.stdout.write("Credential not updated, no arguments present")
            return
        identity_client.credentials.update(parsed_args.credential, **kwargs)
        return


class ShowCredential(show.ShowOne):
    """Show credential command"""

    log = logging.getLogger(__name__ + '.ShowCredential')

    def get_parser(self, prog_name):
        parser = super(ShowCredential, self).get_parser(prog_name)
        parser.add_argument(
            'credential',
            metavar='<credential-id>',
            help='ID of credential to display',
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        credential = utils.find_resource(identity_client.credentials,
                                         parsed_args.credential)

        credential._info.pop('links')
        return zip(*sorted(six.iteritems(credential._info)))
