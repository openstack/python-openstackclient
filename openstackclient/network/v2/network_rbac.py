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

"""RBAC action implementations"""

import logging

from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _
from openstackclient.identity import common as identity_common
from openstackclient.network import common

LOG = logging.getLogger(__name__)


def _get_columns(item):
    column_map = {
        'target_tenant': 'target_project_id',
    }
    hidden_columns = ['location', 'name', 'tenant_id']
    return utils.get_osc_show_columns_for_sdk_resource(
        item, column_map, hidden_columns
    )


def _get_attrs(client_manager, parsed_args):
    attrs = {}
    attrs['object_type'] = parsed_args.type
    attrs['action'] = parsed_args.action

    network_client = client_manager.network
    if parsed_args.type == 'network':
        object_id = network_client.find_network(
            parsed_args.rbac_object, ignore_missing=False
        ).id
    if parsed_args.type == 'qos_policy':
        object_id = network_client.find_qos_policy(
            parsed_args.rbac_object, ignore_missing=False
        ).id
    if parsed_args.type == 'security_group':
        object_id = network_client.find_security_group(
            parsed_args.rbac_object, ignore_missing=False
        ).id
    if parsed_args.type == 'address_scope':
        object_id = network_client.find_address_scope(
            parsed_args.rbac_object, ignore_missing=False
        ).id
    if parsed_args.type == 'subnetpool':
        object_id = network_client.find_subnet_pool(
            parsed_args.rbac_object, ignore_missing=False
        ).id
    if parsed_args.type == 'address_group':
        object_id = network_client.find_address_group(
            parsed_args.rbac_object, ignore_missing=False
        ).id

    attrs['object_id'] = object_id

    identity_client = client_manager.identity
    if parsed_args.target_project is not None:
        project_id = identity_common.find_project(
            identity_client,
            parsed_args.target_project,
            parsed_args.target_project_domain,
        ).id
    elif parsed_args.target_all_projects:
        project_id = '*'
    attrs['target_tenant'] = project_id
    if parsed_args.project is not None:
        project_id = identity_common.find_project(
            identity_client,
            parsed_args.project,
            parsed_args.project_domain,
        ).id
        attrs['project_id'] = project_id

    return attrs


# TODO(abhiraut): Use the SDK resource mapped attribute names once the
# OSC minimum requirements include SDK 1.0.
class CreateNetworkRBAC(command.ShowOne, common.NeutronCommandWithExtraArgs):
    _description = _("Create network RBAC policy")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'rbac_object',
            metavar="<rbac-object>",
            help=_(
                "The object to which this RBAC policy affects (name or ID)"
            ),
        )
        parser.add_argument(
            '--type',
            metavar="<type>",
            required=True,
            choices=[
                'address_group',
                'address_scope',
                'security_group',
                'subnetpool',
                'qos_policy',
                'network',
            ],
            help=_(
                'Type of the object that RBAC policy '
                'affects ("address_group", "address_scope", '
                '"security_group", "subnetpool", "qos_policy" or '
                '"network")'
            ),
        )
        parser.add_argument(
            '--action',
            metavar="<action>",
            required=True,
            choices=['access_as_external', 'access_as_shared'],
            help=_(
                'Action for the RBAC policy '
                '("access_as_external" or "access_as_shared")'
            ),
        )
        target_project_group = parser.add_mutually_exclusive_group(
            required=True
        )
        target_project_group.add_argument(
            '--target-project',
            metavar="<target-project>",
            help=_(
                'The project to which the RBAC policy '
                'will be enforced (name or ID)'
            ),
        )
        target_project_group.add_argument(
            '--target-all-projects',
            action='store_true',
            help=_('Allow creating RBAC policy for all projects'),
        )
        parser.add_argument(
            '--target-project-domain',
            metavar='<target-project-domain>',
            help=_(
                'Domain the target project belongs to (name or ID). '
                'This can be used in case collisions between project names '
                'exist.'
            ),
        )
        parser.add_argument(
            '--project',
            metavar="<project>",
            help=_('The owner project (name or ID)'),
        )
        identity_common.add_project_domain_option_to_parser(parser)
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        attrs = _get_attrs(self.app.client_manager, parsed_args)
        attrs.update(
            self._parse_extra_properties(parsed_args.extra_properties)
        )
        obj = client.create_rbac_policy(**attrs)
        display_columns, columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns)
        return display_columns, data


class DeleteNetworkRBAC(command.Command):
    _description = _("Delete network RBAC policy(s)")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'rbac_policy',
            metavar="<rbac-policy>",
            nargs='+',
            help=_("RBAC policy(s) to delete (ID only)"),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        result = 0

        for rbac in parsed_args.rbac_policy:
            try:
                obj = client.find_rbac_policy(rbac, ignore_missing=False)
                client.delete_rbac_policy(obj)
            except Exception as e:
                result += 1
                LOG.error(
                    _(
                        "Failed to delete RBAC policy with "
                        "ID '%(rbac)s': %(e)s"
                    ),
                    {'rbac': rbac, 'e': e},
                )

        if result > 0:
            total = len(parsed_args.rbac_policy)
            msg = _(
                "%(result)s of %(total)s RBAC policies failed to delete."
            ) % {'result': result, 'total': total}
            raise exceptions.CommandError(msg)


class ListNetworkRBAC(command.Lister):
    _description = _("List network RBAC policies")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--type',
            metavar='<type>',
            choices=[
                'address_group',
                'address_scope',
                'security_group',
                'subnetpool',
                'qos_policy',
                'network',
            ],
            help=_(
                'List network RBAC policies according to '
                'given object type ("address_group", "address_scope", '
                '"security_group", "subnetpool", "qos_policy" or '
                '"network")'
            ),
        )
        parser.add_argument(
            '--action',
            metavar='<action>',
            choices=['access_as_external', 'access_as_shared'],
            help=_(
                'List network RBAC policies according to given '
                'action ("access_as_external" or "access_as_shared")'
            ),
        )
        parser.add_argument(
            '--target-project',
            metavar='<target-project>',
            help=_('List network RBAC policies for a specific target project'),
        )
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_("List additional fields in output"),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network

        columns: tuple[str, ...] = (
            'id',
            'object_type',
            'object_id',
        )
        column_headers: tuple[str, ...] = (
            'ID',
            'Object Type',
            'Object ID',
        )

        query = {}
        if parsed_args.long:
            columns += ('action',)
            column_headers += ('Action',)
        if parsed_args.type is not None:
            query['object_type'] = parsed_args.type
        if parsed_args.action is not None:
            query['action'] = parsed_args.action
        if parsed_args.target_project is not None:
            project_id = "*"

            if parsed_args.target_project != "*":
                identity_client = self.app.client_manager.identity
                project_id = identity_common.find_project(
                    identity_client,
                    parsed_args.target_project,
                ).id
            query['target_project_id'] = project_id

        data = client.rbac_policies(**query)

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


# TODO(abhiraut): Use the SDK resource mapped attribute names once the
# OSC minimum requirements include SDK 1.0.
class SetNetworkRBAC(common.NeutronCommandWithExtraArgs):
    _description = _("Set network RBAC policy properties")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'rbac_policy',
            metavar="<rbac-policy>",
            help=_("RBAC policy to be modified (ID only)"),
        )
        parser.add_argument(
            '--target-project',
            metavar="<target-project>",
            help=_(
                'The project to which the RBAC policy '
                'will be enforced (name or ID)'
            ),
        )
        parser.add_argument(
            '--target-project-domain',
            metavar='<target-project-domain>',
            help=_(
                'Domain the target project belongs to (name or ID). '
                'This can be used in case collisions between project names '
                'exist.'
            ),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        obj = client.find_rbac_policy(
            parsed_args.rbac_policy, ignore_missing=False
        )
        attrs = {}
        if parsed_args.target_project:
            identity_client = self.app.client_manager.identity
            project_id = identity_common.find_project(
                identity_client,
                parsed_args.target_project,
                parsed_args.target_project_domain,
            ).id
            attrs['target_tenant'] = project_id
        attrs.update(
            self._parse_extra_properties(parsed_args.extra_properties)
        )
        client.update_rbac_policy(obj, **attrs)


class ShowNetworkRBAC(command.ShowOne):
    _description = _("Display network RBAC policy details")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'rbac_policy',
            metavar="<rbac-policy>",
            help=_("RBAC policy (ID only)"),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        obj = client.find_rbac_policy(
            parsed_args.rbac_policy, ignore_missing=False
        )
        display_columns, columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns)
        return display_columns, data
