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

from osc_lib import utils
import six

from openstackclient.i18n import _
from openstackclient.identity import common as identity_common
from openstackclient.network import common
from openstackclient.network import sdk_utils
from openstackclient.network import utils as network_utils


def _format_network_security_group_rules(sg_rules):
    # For readability and to align with formatting compute security group
    # rules, trim keys with caller known (e.g. security group and tenant ID)
    # or empty values.
    for sg_rule in sg_rules:
        empty_keys = [k for k, v in six.iteritems(sg_rule) if not v]
        for key in empty_keys:
            sg_rule.pop(key)
        sg_rule.pop('security_group_id', None)
        sg_rule.pop('tenant_id', None)
        sg_rule.pop('project_id', None)
    return utils.format_list_of_dicts(sg_rules)


def _format_compute_security_group_rule(sg_rule):
    info = network_utils.transform_compute_security_group_rule(sg_rule)
    # Trim parent security group ID since caller has this information.
    info.pop('parent_group_id', None)
    # Trim keys with empty string values.
    keys_to_trim = [
        'ip_protocol',
        'ip_range',
        'port_range',
        'remote_security_group',
    ]
    for key in keys_to_trim:
        if key in info and not info[key]:
            info.pop(key)
    return utils.format_dict(info)


def _format_compute_security_group_rules(sg_rules):
    rules = []
    for sg_rule in sg_rules:
        rules.append(_format_compute_security_group_rule(sg_rule))
    return utils.format_list(rules, separator='\n')


_formatters_network = {
    'security_group_rules': _format_network_security_group_rules,
}


_formatters_compute = {
    'rules': _format_compute_security_group_rules,
}


def _get_columns(item):
    column_map = {
        'security_group_rules': 'rules',
        'tenant_id': 'project_id',
    }
    return sdk_utils.get_osc_show_columns_for_sdk_resource(item, column_map)


# TODO(abhiraut): Use the SDK resource mapped attribute names once the
# OSC minimum requirements include SDK 1.0.
class CreateSecurityGroup(common.NetworkAndComputeShowOne):
    _description = _("Create a new security group")

    def update_parser_common(self, parser):
        parser.add_argument(
            "name",
            metavar="<name>",
            help=_("New security group name")
        )
        parser.add_argument(
            "--description",
            metavar="<description>",
            help=_("Security group description")
        )
        return parser

    def update_parser_network(self, parser):
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_("Owner's project (name or ID)")
        )
        identity_common.add_project_domain_option_to_parser(parser)
        return parser

    def _get_description(self, parsed_args):
        if parsed_args.description is not None:
            return parsed_args.description
        else:
            return parsed_args.name

    def take_action_network(self, client, parsed_args):
        # Build the create attributes.
        attrs = {}
        attrs['name'] = parsed_args.name
        attrs['description'] = self._get_description(parsed_args)
        if parsed_args.project is not None:
            identity_client = self.app.client_manager.identity
            project_id = identity_common.find_project(
                identity_client,
                parsed_args.project,
                parsed_args.project_domain,
            ).id
            attrs['tenant_id'] = project_id

        # Create the security group and display the results.
        obj = client.create_security_group(**attrs)
        display_columns, property_columns = _get_columns(obj)
        data = utils.get_item_properties(
            obj,
            property_columns,
            formatters=_formatters_network
        )
        return (display_columns, data)

    def take_action_compute(self, client, parsed_args):
        description = self._get_description(parsed_args)
        obj = client.security_groups.create(
            parsed_args.name,
            description,
        )
        display_columns, property_columns = _get_columns(obj)
        data = utils.get_dict_properties(
            obj._info,
            property_columns,
            formatters=_formatters_compute
        )
        return (display_columns, data)


class DeleteSecurityGroup(common.NetworkAndComputeDelete):
    _description = _("Delete security group(s)")

    # Used by base class to find resources in parsed_args.
    resource = 'group'
    r = None

    def update_parser_common(self, parser):
        parser.add_argument(
            'group',
            metavar='<group>',
            nargs="+",
            help=_("Security group(s) to delete (name or ID)"),
        )
        return parser

    def take_action_network(self, client, parsed_args):
        obj = client.find_security_group(self.r, ignore_missing=False)
        client.delete_security_group(obj)

    def take_action_compute(self, client, parsed_args):
        data = utils.find_resource(client.security_groups, self.r)
        client.security_groups.delete(data.id)


# TODO(rauta): Use the SDK resource mapped attribute names once
# the OSC minimum requirements include SDK 1.0.
class ListSecurityGroup(common.NetworkAndComputeLister):
    _description = _("List security groups")

    def update_parser_network(self, parser):
        # Maintain and hide the argument for backwards compatibility.
        # Network will always return all projects for an admin.
        parser.add_argument(
            '--all-projects',
            action='store_true',
            default=False,
            help=argparse.SUPPRESS,
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_("List security groups according to the project "
                   "(name or ID)")
        )
        identity_common.add_project_domain_option_to_parser(parser)
        return parser

    def update_parser_compute(self, parser):
        parser.add_argument(
            '--all-projects',
            action='store_true',
            default=False,
            help=_("Display information from all projects (admin only)")
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
        filters = {}
        if parsed_args.project:
            identity_client = self.app.client_manager.identity
            project_id = identity_common.find_project(
                identity_client,
                parsed_args.project,
                parsed_args.project_domain,
            ).id
            filters['tenant_id'] = project_id
            filters['project_id'] = project_id
        return self._get_return_data(client.security_groups(**filters))

    def take_action_compute(self, client, parsed_args):
        search = {'all_tenants': parsed_args.all_projects}
        data = client.security_groups.list(search_opts=search)
        return self._get_return_data(data,
                                     include_project=parsed_args.all_projects)


class SetSecurityGroup(common.NetworkAndComputeCommand):
    _description = _("Set security group properties")

    def update_parser_common(self, parser):
        parser.add_argument(
            'group',
            metavar='<group>',
            help=_("Security group to modify (name or ID)")
        )
        parser.add_argument(
            '--name',
            metavar='<new-name>',
            help=_("New security group name")
        )
        parser.add_argument(
            "--description",
            metavar="<description>",
            help=_("New security group description")
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


class ShowSecurityGroup(common.NetworkAndComputeShowOne):
    _description = _("Display security group details")

    def update_parser_common(self, parser):
        parser.add_argument(
            'group',
            metavar='<group>',
            help=_("Security group to display (name or ID)")
        )
        return parser

    def take_action_network(self, client, parsed_args):
        obj = client.find_security_group(parsed_args.group,
                                         ignore_missing=False)
        display_columns, property_columns = _get_columns(obj)
        data = utils.get_item_properties(
            obj,
            property_columns,
            formatters=_formatters_network
        )
        return (display_columns, data)

    def take_action_compute(self, client, parsed_args):
        obj = utils.find_resource(
            client.security_groups,
            parsed_args.group,
        )
        display_columns, property_columns = _get_columns(obj)
        data = utils.get_dict_properties(
            obj._info,
            property_columns,
            formatters=_formatters_compute
        )
        return (display_columns, data)
