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

"""Security Group action implementations"""

import argparse

from openstackclient.common import utils
from openstackclient.network import common


class DeleteSecurityGroup(common.NetworkAndComputeCommand):
    """Delete a security group"""

    def update_parser_common(self, parser):
        parser.add_argument(
            'group',
            metavar='<group>',
            help='Security group to delete (name or ID)',
        )
        return parser

    def take_action_network(self, client, parsed_args):
        obj = client.find_security_group(parsed_args.group)
        client.delete_security_group(obj)

    def take_action_compute(self, client, parsed_args):
        data = utils.find_resource(
            client.security_groups,
            parsed_args.group,
        )
        client.security_groups.delete(data.id)


class ListSecurityGroup(common.NetworkAndComputeLister):
    """List security groups"""

    def update_parser_network(self, parser):
        # Maintain and hide the argument for backwards compatibility.
        # Network will always return all projects for an admin.
        parser.add_argument(
            '--all-projects',
            action='store_true',
            default=False,
            help=argparse.SUPPRESS,
        )
        return parser

    def update_parser_compute(self, parser):
        parser.add_argument(
            '--all-projects',
            action='store_true',
            default=False,
            help='Display information from all projects (admin only)',
        )
        return parser

    def _get_return_data(self, data, include_project=True):
        columns = (
            "ID",
            "Name",
            "Description",
        )
        column_headers = columns
        if include_project:
            columns = columns + ('Tenant ID',)
            column_headers = column_headers + ('Project',)
        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))

    def take_action_network(self, client, parsed_args):
        return self._get_return_data(client.security_groups())

    def take_action_compute(self, client, parsed_args):
        search = {'all_tenants': parsed_args.all_projects}
        data = client.security_groups.list(search_opts=search)
        return self._get_return_data(data,
                                     include_project=parsed_args.all_projects)


class SetSecurityGroup(common.NetworkAndComputeCommand):
    """Set security group properties"""

    def update_parser_common(self, parser):
        parser.add_argument(
            'group',
            metavar='<group>',
            help='Security group to modify (name or ID)',
        )
        parser.add_argument(
            '--name',
            metavar='<new-name>',
            help='New security group name',
        )
        parser.add_argument(
            "--description",
            metavar="<description>",
            help="New security group description",
        )
        return parser

    def take_action_network(self, client, parsed_args):
        obj = client.find_security_group(parsed_args.group,
                                         ignore_missing=False)
        attrs = {}
        if parsed_args.name is not None:
            attrs['name'] = parsed_args.name
        if parsed_args.description is not None:
            attrs['description'] = parsed_args.description
        # NOTE(rtheis): Previous behavior did not raise a CommandError
        # if there were no updates. Maintain this behavior and issue
        # the update.
        client.update_security_group(obj, **attrs)

    def take_action_compute(self, client, parsed_args):
        data = utils.find_resource(
            client.security_groups,
            parsed_args.group,
        )

        if parsed_args.name is not None:
            data.name = parsed_args.name
        if parsed_args.description is not None:
            data.description = parsed_args.description

        # NOTE(rtheis): Previous behavior did not raise a CommandError
        # if there were no updates. Maintain this behavior and issue
        # the update.
        client.security_groups.update(
            data,
            data.name,
            data.description,
        )
