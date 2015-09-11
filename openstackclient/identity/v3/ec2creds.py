# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""Identity v3 EC2 Credentials action implementations"""

import logging
import six

from cliff import command
from cliff import lister
from cliff import show

from openstackclient.common import utils
from openstackclient.i18n import _  # noqa
from openstackclient.identity import common


def _determine_ec2_user(parsed_args, client_manager):
    """Determine a user several different ways.

    Assumes parsed_args has user and user_domain arguments. Attempts to find
    the user if domain scoping is provided, otherwise revert to a basic user
    call. Lastly use the currently authenticated user.

    """

    user_domain = None
    if parsed_args.user_domain:
        user_domain = common.find_domain(client_manager.identity,
                                         parsed_args.user_domain)
    if parsed_args.user:
        if user_domain is not None:
            user = utils.find_resource(client_manager.identity.users,
                                       parsed_args.user,
                                       domain_id=user_domain.id).id
        else:
            user = utils.find_resource(
                client_manager.identity.users,
                parsed_args.user).id
    else:
        # Get the user from the current auth
        user = client_manager.auth_ref.user_id
    return user


class CreateEC2Creds(show.ShowOne):
    """Create EC2 credentials"""

    log = logging.getLogger(__name__ + ".CreateEC2Creds")

    def get_parser(self, prog_name):
        parser = super(CreateEC2Creds, self).get_parser(prog_name)
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_(
                'Create credentials in project '
                '(name or ID; default: current authenticated project)'
            ),
        )
        parser.add_argument(
            '--user',
            metavar='<user>',
            help=_(
                'Create credentials for user '
                '(name or ID; default: current authenticated user)'
            ),
        )
        common.add_user_domain_option_to_parser(parser)
        common.add_project_domain_option_to_parser(parser)
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        client_manager = self.app.client_manager
        user = _determine_ec2_user(parsed_args, client_manager)

        project_domain = None
        if parsed_args.project_domain:
            project_domain = common.find_domain(identity_client,
                                                parsed_args.project_domain)

        if parsed_args.project:
            if project_domain is not None:
                project = utils.find_resource(identity_client.projects,
                                              parsed_args.project,
                                              domain_id=project_domain.id).id
            else:
                project = utils.find_resource(
                    identity_client.projects,
                    parsed_args.project).id
        else:
            # Get the project from the current auth
            project = self.app.client_manager.auth_ref.project_id

        creds = identity_client.ec2.create(user, project)

        info = {}
        info.update(creds._info)

        if 'tenant_id' in info:
            info.update(
                {'project_id': info.pop('tenant_id')}
            )

        return zip(*sorted(six.iteritems(info)))


class DeleteEC2Creds(command.Command):
    """Delete EC2 credentials"""

    log = logging.getLogger(__name__ + '.DeleteEC2Creds')

    def get_parser(self, prog_name):
        parser = super(DeleteEC2Creds, self).get_parser(prog_name)
        parser.add_argument(
            'access_key',
            metavar='<access-key>',
            help=_('Credentials access key'),
        )
        parser.add_argument(
            '--user',
            metavar='<user>',
            help=_('Delete credentials for user (name or ID)'),
        )
        common.add_user_domain_option_to_parser(parser)
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
        client_manager = self.app.client_manager
        user = _determine_ec2_user(parsed_args, client_manager)
        client_manager.identity.ec2.delete(user, parsed_args.access_key)


class ListEC2Creds(lister.Lister):
    """List EC2 credentials"""

    log = logging.getLogger(__name__ + '.ListEC2Creds')

    def get_parser(self, prog_name):
        parser = super(ListEC2Creds, self).get_parser(prog_name)
        parser.add_argument(
            '--user',
            metavar='<user>',
            help=_('Filter list by user (name or ID)'),
        )
        common.add_user_domain_option_to_parser(parser)
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
        client_manager = self.app.client_manager
        user = _determine_ec2_user(parsed_args, client_manager)

        columns = ('access', 'secret', 'tenant_id', 'user_id')
        column_headers = ('Access', 'Secret', 'Project ID', 'User ID')
        data = client_manager.identity.ec2.list(user)

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                    formatters={},
                ) for s in data))


class ShowEC2Creds(show.ShowOne):
    """Display EC2 credentials details"""

    log = logging.getLogger(__name__ + '.ShowEC2Creds')

    def get_parser(self, prog_name):
        parser = super(ShowEC2Creds, self).get_parser(prog_name)
        parser.add_argument(
            'access_key',
            metavar='<access-key>',
            help=_('Credentials access key'),
        )
        parser.add_argument(
            '--user',
            metavar='<user>',
            help=_('Show credentials for user (name or ID)'),
        )
        common.add_user_domain_option_to_parser(parser)
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
        client_manager = self.app.client_manager
        user = _determine_ec2_user(parsed_args, client_manager)
        creds = client_manager.identity.ec2.get(user, parsed_args.access_key)

        info = {}
        info.update(creds._info)

        if 'tenant_id' in info:
            info.update(
                {'project_id': info.pop('tenant_id')}
            )

        return zip(*sorted(six.iteritems(info)))
