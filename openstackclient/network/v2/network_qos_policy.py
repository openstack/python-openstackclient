# Copyright (c) 2016, Intel Corporation.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import logging

from cliff import columns as cliff_columns
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _
from openstackclient.identity import common as identity_common
from openstackclient.network import common

LOG = logging.getLogger(__name__)


class RulesColumn(cliff_columns.FormattableColumn):
    def human_readable(self):
        return '\n'.join(str(v) for v in self._value)


_formatters = {
    'rules': RulesColumn,
}


def _get_columns(item):
    column_map = {
        'is_shared': 'shared',
    }
    hidden_columns = ['location', 'tenant_id']
    return utils.get_osc_show_columns_for_sdk_resource(
        item, column_map, hidden_columns
    )


def _get_attrs(client_manager, parsed_args):
    attrs = {}
    if 'name' in parsed_args and parsed_args.name is not None:
        attrs['name'] = parsed_args.name
    if 'description' in parsed_args and parsed_args.description is not None:
        attrs['description'] = parsed_args.description
    if parsed_args.share:
        attrs['shared'] = True
    if parsed_args.no_share:
        attrs['shared'] = False
    # NOTE(ralonsoh): 'default' and 'no_default' parameters are defined only in
    #                create and set commands context only.
    if 'default' in parsed_args and parsed_args.default:
        attrs['is_default'] = True
    if 'no_default' in parsed_args and parsed_args.no_default:
        attrs['is_default'] = False
    # NOTE(ralonsoh): 'project' parameter is defined only in create and list
    #                commands context only.
    if 'project' in parsed_args and parsed_args.project is not None:
        identity_client = client_manager.identity
        project_id = identity_common.find_project(
            identity_client,
            parsed_args.project,
            parsed_args.project_domain,
        ).id
        attrs['project_id'] = project_id

    return attrs


# TODO(abhiraut): Use the SDK resource mapped attribute names once the
# OSC minimum requirements include SDK 1.0.
class CreateNetworkQosPolicy(
    command.ShowOne, common.NeutronCommandWithExtraArgs
):
    _description = _("Create a QoS policy")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'name', metavar='<name>', help=_("Name of QoS policy to create")
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_("Description of the QoS policy"),
        )
        share_group = parser.add_mutually_exclusive_group()
        share_group.add_argument(
            '--share',
            action='store_true',
            default=None,
            help=_("Make the QoS policy accessible by other projects"),
        )
        share_group.add_argument(
            '--no-share',
            action='store_true',
            help=_(
                "Make the QoS policy not accessible by other projects "
                "(default)"
            ),
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_("Owner's project (name or ID)"),
        )
        identity_common.add_project_domain_option_to_parser(parser)
        default_group = parser.add_mutually_exclusive_group()
        default_group.add_argument(
            '--default',
            action='store_true',
            help=_("Set this as a default network QoS policy"),
        )
        default_group.add_argument(
            '--no-default',
            action='store_true',
            help=_("Set this as a non-default network QoS policy"),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        attrs = _get_attrs(self.app.client_manager, parsed_args)
        attrs.update(
            self._parse_extra_properties(parsed_args.extra_properties)
        )
        obj = client.create_qos_policy(**attrs)
        display_columns, columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns, formatters={})
        return (display_columns, data)


class DeleteNetworkQosPolicy(command.Command):
    _description = _("Delete Qos Policy(s)")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'policy',
            metavar="<qos-policy>",
            nargs="+",
            help=_("QoS policy(s) to delete (name or ID)"),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        result = 0

        for policy in parsed_args.policy:
            try:
                obj = client.find_qos_policy(policy, ignore_missing=False)
                client.delete_qos_policy(obj)
            except Exception as e:
                result += 1
                LOG.error(
                    _(
                        "Failed to delete QoS policy "
                        "name or ID '%(qos_policy)s': %(e)s"
                    ),
                    {'qos_policy': policy, 'e': e},
                )

        if result > 0:
            total = len(parsed_args.policy)
            msg = _(
                "%(result)s of %(total)s QoS policies failed to delete."
            ) % {'result': result, 'total': total}
            raise exceptions.CommandError(msg)


# TODO(abhiraut): Use only the SDK resource mapped attribute names once the
# OSC minimum requirements include SDK 1.0.
class ListNetworkQosPolicy(command.Lister):
    _description = _("List QoS policies")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_(
                "List QoS policies according to their project (name or ID)"
            ),
        )
        identity_common.add_project_domain_option_to_parser(parser)
        shared_group = parser.add_mutually_exclusive_group()
        shared_group.add_argument(
            '--share',
            action='store_true',
            help=_("List QoS policies shared between projects"),
        )
        shared_group.add_argument(
            '--no-share',
            action='store_true',
            help=_("List QoS policies not shared between projects"),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        columns = (
            'id',
            'name',
            'is_shared',
            'is_default',
            'project_id',
        )
        column_headers = (
            'ID',
            'Name',
            'Shared',
            'Default',
            'Project',
        )
        attrs = _get_attrs(self.app.client_manager, parsed_args)
        data = client.qos_policies(**attrs)
        return (
            column_headers,
            (
                utils.get_item_properties(
                    s,
                    columns,
                    formatters={},
                )
                for s in data
            ),
        )


# TODO(abhiraut): Use the SDK resource mapped attribute names once the
# OSC minimum requirements include SDK 1.0.
class SetNetworkQosPolicy(common.NeutronCommandWithExtraArgs):
    _description = _("Set QoS policy properties")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'policy',
            metavar="<qos-policy>",
            help=_("QoS policy to modify (name or ID)"),
        )
        parser.add_argument(
            '--name', metavar="<name>", help=_('Set QoS policy name')
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_("Description of the QoS policy"),
        )
        enable_group = parser.add_mutually_exclusive_group()
        enable_group.add_argument(
            '--share',
            action='store_true',
            help=_('Make the QoS policy accessible by other projects'),
        )
        enable_group.add_argument(
            '--no-share',
            action='store_true',
            help=_('Make the QoS policy not accessible by other projects'),
        )
        default_group = parser.add_mutually_exclusive_group()
        default_group.add_argument(
            '--default',
            action='store_true',
            help=_("Set this as a default network QoS policy"),
        )
        default_group.add_argument(
            '--no-default',
            action='store_true',
            help=_("Set this as a non-default network QoS policy"),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        obj = client.find_qos_policy(parsed_args.policy, ignore_missing=False)
        attrs = _get_attrs(self.app.client_manager, parsed_args)
        attrs.update(
            self._parse_extra_properties(parsed_args.extra_properties)
        )
        client.update_qos_policy(obj, **attrs)


class ShowNetworkQosPolicy(command.ShowOne):
    _description = _("Display QoS policy details")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'policy',
            metavar="<qos-policy>",
            help=_("QoS policy to display (name or ID)"),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        obj = client.find_qos_policy(parsed_args.policy, ignore_missing=False)
        display_columns, columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns, formatters=_formatters)
        return (display_columns, data)
