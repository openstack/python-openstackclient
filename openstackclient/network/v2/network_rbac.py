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


LOG = logging.getLogger(__name__)


def _get_columns(item):
    columns = list(item.keys())
    if 'tenant_id' in columns:
        columns.remove('tenant_id')
        columns.append('project_id')
    if 'target_tenant' in columns:
        columns.remove('target_tenant')
        columns.append('target_project_id')
    return tuple(sorted(columns))


def _get_attrs(client_manager, parsed_args):
    attrs = {}
    attrs['object_type'] = parsed_args.type
    attrs['action'] = parsed_args.action

    network_client = client_manager.network
    if parsed_args.type == 'network':
        object_id = network_client.find_network(
            parsed_args.rbac_object, ignore_missing=False).id
    if parsed_args.type == 'qos_policy':
        # TODO(Huanxuan Ao): Support finding a object ID by obejct name
        # after qos policy finding supported in SDK.
        object_id = parsed_args.rbac_object
    attrs['object_id'] = object_id

    identity_client = client_manager.identity
    project_id = identity_common.find_project(
        identity_client,
        parsed_args.target_project,
        parsed_args.target_project_domain,
    ).id
    attrs['target_tenant'] = project_id
    if parsed_args.project is not None:
        project_id = identity_common.find_project(
            identity_client,
            parsed_args.project,
            parsed_args.project_domain,
        ).id
        attrs['tenant_id'] = project_id

    return attrs


class CreateNetworkRBAC(command.ShowOne):
    """Create network RBAC policy"""

    def get_parser(self, prog_name):
        parser = super(CreateNetworkRBAC, self).get_parser(prog_name)
        parser.add_argument(
            'rbac_object',
            metavar="<rbac-object>",
            help=_("The object to which this RBAC policy affects (name or "
                   "ID for network objects, ID only for QoS policy objects)")
        )
        parser.add_argument(
            '--type',
            metavar="<type>",
            required=True,
            choices=['qos_policy', 'network'],
            help=_('Type of the object that RBAC policy '
                   'affects ("qos_policy" or "network")')
        )
        parser.add_argument(
            '--action',
            metavar="<action>",
            required=True,
            choices=['access_as_external', 'access_as_shared'],
            help=_('Action for the RBAC policy '
                   '("access_as_external" or "access_as_shared")')
        )
        parser.add_argument(
            '--target-project',
            required=True,
            metavar="<target-project>",
            help=_('The project to which the RBAC policy '
                   'will be enforced (name or ID)')
        )
        parser.add_argument(
            '--target-project-domain',
            metavar='<target-project-domain>',
            help=_('Domain the target project belongs to (name or ID). '
                   'This can be used in case collisions between project names '
                   'exist.'),
        )
        parser.add_argument(
            '--project',
            metavar="<project>",
            help=_('The owner project (name or ID)')
        )
        identity_common.add_project_domain_option_to_parser(parser)
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        attrs = _get_attrs(self.app.client_manager, parsed_args)
        obj = client.create_rbac_policy(**attrs)
        columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns)
        return columns, data


class DeleteNetworkRBAC(command.Command):
    """Delete network RBAC policy(s)"""

    def get_parser(self, prog_name):
        parser = super(DeleteNetworkRBAC, self).get_parser(prog_name)
        parser.add_argument(
            'rbac_policy',
            metavar="<rbac-policy>",
            nargs='+',
            help=_("RBAC policy(s) to delete (ID only)")
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
                LOG.error(_("Failed to delete RBAC policy with "
                            "ID '%(rbac)s': %(e)s"),
                          {'rbac': rbac, 'e': e})

        if result > 0:
            total = len(parsed_args.rbac_policy)
            msg = (_("%(result)s of %(total)s RBAC policies failed "
                   "to delete.") % {'result': result, 'total': total})
            raise exceptions.CommandError(msg)


class ListNetworkRBAC(command.Lister):
    """List network RBAC policies"""

    def take_action(self, parsed_args):
        client = self.app.client_manager.network

        columns = (
            'id',
            'object_type',
            'object_id',
        )
        column_headers = (
            'ID',
            'Object Type',
            'Object ID',
        )

        data = client.rbac_policies()
        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class SetNetworkRBAC(command.Command):
    """Set network RBAC policy properties"""

    def get_parser(self, prog_name):
        parser = super(SetNetworkRBAC, self).get_parser(prog_name)
        parser.add_argument(
            'rbac_policy',
            metavar="<rbac-policy>",
            help=_("RBAC policy to be modified (ID only)")
        )
        parser.add_argument(
            '--target-project',
            metavar="<target-project>",
            help=_('The project to which the RBAC policy '
                   'will be enforced (name or ID)')
        )
        parser.add_argument(
            '--target-project-domain',
            metavar='<target-project-domain>',
            help=_('Domain the target project belongs to (name or ID). '
                   'This can be used in case collisions between project names '
                   'exist.'),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        obj = client.find_rbac_policy(parsed_args.rbac_policy,
                                      ignore_missing=False)
        attrs = {}
        if parsed_args.target_project:
            identity_client = self.app.client_manager.identity
            project_id = identity_common.find_project(
                identity_client,
                parsed_args.target_project,
                parsed_args.target_project_domain,
            ).id
            attrs['target_tenant'] = project_id
        client.update_rbac_policy(obj, **attrs)


class ShowNetworkRBAC(command.ShowOne):
    """Display network RBAC policy details"""

    def get_parser(self, prog_name):
        parser = super(ShowNetworkRBAC, self).get_parser(prog_name)
        parser.add_argument(
            'rbac_policy',
            metavar="<rbac-policy>",
            help=_("RBAC policy (ID only)")
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        obj = client.find_rbac_policy(parsed_args.rbac_policy,
                                      ignore_missing=False)
        columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns)
        return columns, data
