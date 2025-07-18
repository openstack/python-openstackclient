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

from cliff import columns as cliff_columns
from osc_lib.command import command
from osc_lib import utils
from osc_lib.utils import tags as _tag

from openstackclient.api import compute_v2
from openstackclient.i18n import _
from openstackclient.identity import common as identity_common
from openstackclient.network import common
from openstackclient.network import utils as network_utils


def _format_network_security_group_rules(sg_rules):
    # For readability and to align with formatting compute security group
    # rules, trim keys with caller known (e.g. security group and tenant ID)
    # or empty values.
    for sg_rule in sg_rules:
        empty_keys = [k for k, v in sg_rule.items() if not v]
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


class NetworkSecurityGroupRulesColumn(cliff_columns.FormattableColumn):
    def human_readable(self):
        return _format_network_security_group_rules(self._value)


class ComputeSecurityGroupRulesColumn(cliff_columns.FormattableColumn):
    def human_readable(self):
        return _format_compute_security_group_rules(self._value)


_formatters_network = {
    'security_group_rules': NetworkSecurityGroupRulesColumn,
}


_formatters_compute = {
    'rules': ComputeSecurityGroupRulesColumn,
}


def _get_columns(item):
    # We still support Nova managed security groups, where we have tenant_id.
    column_map = {
        'security_group_rules': 'rules',
    }
    hidden_columns = ['location', 'tenant_id']
    return utils.get_osc_show_columns_for_sdk_resource(
        item, column_map, hidden_columns
    )


# TODO(abhiraut): Use the SDK resource mapped attribute names once the
# OSC minimum requirements include SDK 1.0.
class CreateSecurityGroup(
    common.NetworkAndComputeShowOne, common.NeutronCommandWithExtraArgs
):
    _description = _("Create a new security group")

    def update_parser_common(self, parser):
        parser.add_argument(
            "name", metavar="<name>", help=_("New security group name")
        )
        parser.add_argument(
            "--description",
            metavar="<description>",
            help=_("Security group description"),
        )
        return parser

    def update_parser_network(self, parser):
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=self.enhance_help_neutron(_("Owner's project (name or ID)")),
        )
        stateful_group = parser.add_mutually_exclusive_group()
        stateful_group.add_argument(
            "--stateful",
            action='store_true',
            default=None,
            help=_("Security group is stateful (default)"),
        )
        stateful_group.add_argument(
            "--stateless",
            action='store_true',
            default=None,
            help=_("Security group is stateless"),
        )
        identity_common.add_project_domain_option_to_parser(
            parser, enhance_help=self.enhance_help_neutron
        )
        _tag.add_tag_option_to_parser_for_create(
            parser, _('security group'), enhance_help=self.enhance_help_neutron
        )
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
        if parsed_args.stateful:
            attrs['stateful'] = True
        if parsed_args.stateless:
            attrs['stateful'] = False
        if parsed_args.project is not None:
            identity_client = self.app.client_manager.identity
            project_id = identity_common.find_project(
                identity_client,
                parsed_args.project,
                parsed_args.project_domain,
            ).id
            attrs['project_id'] = project_id
        attrs.update(
            self._parse_extra_properties(parsed_args.extra_properties)
        )

        # Create the security group and display the results.
        obj = client.create_security_group(**attrs)
        # tags cannot be set when created, so tags need to be set later.
        _tag.update_tags_for_set(client, obj, parsed_args)
        display_columns, property_columns = _get_columns(obj)
        data = utils.get_item_properties(
            obj, property_columns, formatters=_formatters_network
        )
        return (display_columns, data)

    def take_action_compute(self, client, parsed_args):
        description = self._get_description(parsed_args)
        obj = compute_v2.create_security_group(
            client,
            parsed_args.name,
            description,
        )
        display_columns = ('description', 'id', 'name', 'project_id', 'rules')
        property_columns = ('description', 'id', 'name', 'tenant_id', 'rules')
        data = utils.get_dict_properties(
            obj, property_columns, formatters=_formatters_compute
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
        security_group = compute_v2.find_security_group(client, self.r)
        compute_v2.delete_security_group(client, security_group['id'])


# TODO(rauta): Use the SDK resource mapped attribute names once
# the OSC minimum requirements include SDK 1.0.
class ListSecurityGroup(common.NetworkAndComputeLister):
    _description = _("List security groups")
    FIELDS_TO_RETRIEVE = [
        'id',
        'name',
        'description',
        'project_id',
        'tags',
        'shared',
    ]

    def update_parser_network(self, parser):
        if not self.is_docs_build:
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
            help=self.enhance_help_neutron(
                _("List security groups according to the project (name or ID)")
            ),
        )
        identity_common.add_project_domain_option_to_parser(
            parser, enhance_help=self.enhance_help_neutron
        )

        shared_group = parser.add_mutually_exclusive_group()
        shared_group.add_argument(
            '--share',
            action='store_true',
            dest='shared',
            default=None,
            help=_("List security groups shared between projects"),
        )
        shared_group.add_argument(
            '--no-share',
            action='store_false',
            dest='shared',
            default=None,
            help=_("List security groups not shared between projects"),
        )

        _tag.add_tag_filtering_option_to_parser(
            parser, _('security group'), enhance_help=self.enhance_help_neutron
        )
        return parser

    def update_parser_compute(self, parser):
        parser.add_argument(
            '--all-projects',
            action='store_true',
            default=False,
            help=self.enhance_help_nova_network(
                _("Display information from all projects (admin only)")
            ),
        )
        return parser

    def take_action_network(self, client, parsed_args):
        filters = {}
        if parsed_args.project:
            identity_client = self.app.client_manager.identity
            project_id = identity_common.find_project(
                identity_client,
                parsed_args.project,
                parsed_args.project_domain,
            ).id
            filters['project_id'] = project_id

        if parsed_args.shared is not None:
            filters['shared'] = parsed_args.shared

        _tag.get_tag_filtering_args(parsed_args, filters)
        data = client.security_groups(
            fields=self.FIELDS_TO_RETRIEVE, **filters
        )

        columns = (
            "id",
            "name",
            "description",
            "project_id",
            "tags",
            "is_shared",
        )
        column_headers = (
            "ID",
            "Name",
            "Description",
            "Project",
            "Tags",
            "Shared",
        )
        return (
            column_headers,
            (
                utils.get_item_properties(
                    s,
                    columns,
                )
                for s in data
            ),
        )

    def take_action_compute(self, client, parsed_args):
        data = compute_v2.list_security_groups(
            # TODO(dtroyer): add limit, marker
            client,
            all_projects=parsed_args.all_projects,
        )

        columns: tuple[str, ...] = ("id", "name", "description")
        column_headers: tuple[str, ...] = ("ID", "Name", "Description")
        if parsed_args.all_projects:
            columns += ('tenant_id',)
            column_headers += ('Project',)
        return (
            column_headers,
            (
                utils.get_dict_properties(
                    s,
                    columns,
                )
                for s in data
            ),
        )


class SetSecurityGroup(
    common.NetworkAndComputeCommand, common.NeutronCommandWithExtraArgs
):
    _description = _("Set security group properties")

    def update_parser_common(self, parser):
        parser.add_argument(
            'group',
            metavar='<group>',
            help=_("Security group to modify (name or ID)"),
        )
        parser.add_argument(
            '--name', metavar='<new-name>', help=_("New security group name")
        )
        parser.add_argument(
            "--description",
            metavar="<description>",
            help=_("New security group description"),
        )
        stateful_group = parser.add_mutually_exclusive_group()
        stateful_group.add_argument(
            "--stateful",
            action='store_true',
            default=None,
            help=_("Security group is stateful (default)"),
        )
        stateful_group.add_argument(
            "--stateless",
            action='store_true',
            default=None,
            help=_("Security group is stateless"),
        )
        return parser

    def update_parser_network(self, parser):
        _tag.add_tag_option_to_parser_for_set(
            parser, _('security group'), enhance_help=self.enhance_help_neutron
        )
        return parser

    def take_action_network(self, client, parsed_args):
        obj = client.find_security_group(
            parsed_args.group, ignore_missing=False
        )
        attrs = {}
        if parsed_args.name is not None:
            attrs['name'] = parsed_args.name
        if parsed_args.description is not None:
            attrs['description'] = parsed_args.description
        if parsed_args.stateful:
            attrs['stateful'] = True
        if parsed_args.stateless:
            attrs['stateful'] = False
        attrs.update(
            self._parse_extra_properties(parsed_args.extra_properties)
        )
        # NOTE(rtheis): Previous behavior did not raise a CommandError
        # if there were no updates. Maintain this behavior and issue
        # the update.
        client.update_security_group(obj, **attrs)

        # tags is a subresource and it needs to be updated separately.
        _tag.update_tags_for_set(client, obj, parsed_args)

    def take_action_compute(self, client, parsed_args):
        security_group = compute_v2.find_security_group(
            client, parsed_args.group
        )

        params = {}
        if parsed_args.name is not None:
            params['name'] = parsed_args.name
        if parsed_args.description is not None:
            params['description'] = parsed_args.description

        # NOTE(rtheis): Previous behavior did not raise a CommandError
        # if there were no updates. Maintain this behavior and issue
        # the update.
        compute_v2.update_security_group(
            client, security_group['id'], **params
        )


class ShowSecurityGroup(common.NetworkAndComputeShowOne):
    _description = _("Display security group details")

    def update_parser_common(self, parser):
        parser.add_argument(
            'group',
            metavar='<group>',
            help=_("Security group to display (name or ID)"),
        )
        return parser

    def take_action_network(self, client, parsed_args):
        obj = client.find_security_group(
            parsed_args.group, ignore_missing=False
        )
        display_columns, property_columns = _get_columns(obj)
        data = utils.get_item_properties(
            obj, property_columns, formatters=_formatters_network
        )
        return (display_columns, data)

    def take_action_compute(self, client, parsed_args):
        obj = compute_v2.find_security_group(client, parsed_args.group)
        display_columns = ('description', 'id', 'name', 'project_id', 'rules')
        property_columns = ('description', 'id', 'name', 'tenant_id', 'rules')
        data = utils.get_dict_properties(
            obj, property_columns, formatters=_formatters_compute
        )
        return (display_columns, data)


class UnsetSecurityGroup(command.Command):
    _description = _("Unset security group properties")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'group',
            metavar="<group>",
            help=_("Security group to modify (name or ID)"),
        )
        _tag.add_tag_option_to_parser_for_unset(parser, _('security group'))
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        obj = client.find_security_group(
            parsed_args.group, ignore_missing=False
        )

        # tags is a subresource and it needs to be updated separately.
        _tag.update_tags_for_unset(client, obj, parsed_args)
