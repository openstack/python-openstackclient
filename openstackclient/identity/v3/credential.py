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
import six

from openstackclient.i18n import _


LOG = logging.getLogger(__name__)


class CreateCredential(command.ShowOne):
    """Create new credential"""

    def get_parser(self, prog_name):
        parser = super(CreateCredential, self).get_parser(prog_name)
        parser.add_argument(
            'user',
            metavar='<user>',
            help=_('user that owns the credential (name or ID)'),
        )
        parser.add_argument(
            '--type',
            default="cert",
            metavar='<type>',
            choices=['ec2', 'cert'],
            help=_('New credential type'),
        )
        parser.add_argument(
            'data',
            metavar='<data>',
            help=_('New credential data'),
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_('Project which limits the scope of '
                   'the credential (name or ID)'),
        )
        return parser

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
    """Delete credential(s)"""

    def get_parser(self, prog_name):
        parser = super(DeleteCredential, self).get_parser(prog_name)
        parser.add_argument(
            'credential',
            metavar='<credential-id>',
            nargs='+',
            help=_('ID of credential(s) to delete'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        result = 0
        for i in parsed_args.credential:
            try:
                identity_client.credentials.delete(i)
            except Exception as e:
                result += 1
                LOG.error(_("Failed to delete credentials with "
                          "ID '%(credential)s': %(e)s")
                          % {'credential': i, 'e': e})

        if result > 0:
            total = len(parsed_args.credential)
            msg = (_("%(result)s of %(total)s credential failed "
                   "to delete.") % {'result': result, 'total': total})
            raise exceptions.CommandError(msg)


class ListCredential(command.Lister):
    """List credentials"""

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
    """Set credential properties"""

    def get_parser(self, prog_name):
        parser = super(SetCredential, self).get_parser(prog_name)
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
            choices=['ec2', 'cert'],
            required=True,
            help=_('New credential type'),
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
            help=_('Project which limits the scope of '
                   'the credential (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        user_id = utils.find_resource(identity_client.users,
                                      parsed_args.user).id

        if parsed_args.project:
            project = utils.find_resource(identity_client.projects,
                                          parsed_args.project).id
        else:
            project = None

        identity_client.credentials.update(parsed_args.credential,
                                           user=user_id,
                                           type=parsed_args.type,
                                           blob=parsed_args.data,
                                           project=project)


class ShowCredential(command.ShowOne):
    """Display credential details"""

    def get_parser(self, prog_name):
        parser = super(ShowCredential, self).get_parser(prog_name)
        parser.add_argument(
            'credential',
            metavar='<credential-id>',
            help=_('ID of credential to display'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        credential = utils.find_resource(identity_client.credentials,
                                         parsed_args.credential)

        credential._info.pop('links')
        return zip(*sorted(six.iteritems(credential._info)))
