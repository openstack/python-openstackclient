#   Copyright 2012 OpenStack Foundation
#   Copyright 2013 Nebula Inc
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

"""Compute v2 Security Group action implementations"""

import logging
import six

from cliff import command
from cliff import lister
from cliff import show

from keystoneclient import exceptions as ksc_exc

try:
    from novaclient.v2 import security_group_rules
except ImportError:
    from novaclient.v1_1 import security_group_rules

from openstackclient.common import parseractions
from openstackclient.common import utils


def _xform_security_group_rule(sgroup):
    info = {}
    info.update(sgroup)
    from_port = info.pop('from_port')
    to_port = info.pop('to_port')
    if isinstance(from_port, int) and isinstance(to_port, int):
        port_range = {'port_range': "%u:%u" % (from_port, to_port)}
    elif from_port is None and to_port is None:
        port_range = {'port_range': ""}
    else:
        port_range = {'port_range': "%s:%s" % (from_port, to_port)}
    info.update(port_range)
    if 'cidr' in info['ip_range']:
        info['ip_range'] = info['ip_range']['cidr']
    else:
        info['ip_range'] = ''
    if info['ip_protocol'] is None:
        info['ip_protocol'] = ''
    elif info['ip_protocol'].lower() == 'icmp':
        info['port_range'] = ''
    return info


class CreateSecurityGroup(show.ShowOne):
    """Create a new security group"""

    log = logging.getLogger(__name__ + ".CreateSecurityGroup")

    def get_parser(self, prog_name):
        parser = super(CreateSecurityGroup, self).get_parser(prog_name)
        parser.add_argument(
            "name",
            metavar="<name>",
            help="New security group name",
        )
        parser.add_argument(
            "--description",
            metavar="<description>",
            help="Security group description",
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        compute_client = self.app.client_manager.compute

        description = parsed_args.description or parsed_args.name

        data = compute_client.security_groups.create(
            parsed_args.name,
            description,
        )

        info = {}
        info.update(data._info)
        return zip(*sorted(six.iteritems(info)))


class DeleteSecurityGroup(command.Command):
    """Delete a security group"""

    log = logging.getLogger(__name__ + '.DeleteSecurityGroup')

    def get_parser(self, prog_name):
        parser = super(DeleteSecurityGroup, self).get_parser(prog_name)
        parser.add_argument(
            'group',
            metavar='<group>',
            help='Name or ID of security group to delete',
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):

        compute_client = self.app.client_manager.compute
        data = utils.find_resource(
            compute_client.security_groups,
            parsed_args.group,
        )
        compute_client.security_groups.delete(data.id)
        return


class ListSecurityGroup(lister.Lister):
    """List all security groups"""

    log = logging.getLogger(__name__ + ".ListSecurityGroup")

    def get_parser(self, prog_name):
        parser = super(ListSecurityGroup, self).get_parser(prog_name)
        parser.add_argument(
            '--all-projects',
            action='store_true',
            default=False,
            help='Display information from all projects (admin only)',
        )
        return parser

    def take_action(self, parsed_args):

        def _get_project(project_id):
            try:
                return getattr(project_hash[project_id], 'name', project_id)
            except KeyError:
                return project_id

        self.log.debug("take_action(%s)", parsed_args)

        compute_client = self.app.client_manager.compute
        columns = (
            "ID",
            "Name",
            "Description",
        )
        column_headers = columns
        if parsed_args.all_projects:
            # TODO(dtroyer): Translate Project_ID to Project (name)
            columns = columns + ('Tenant ID',)
            column_headers = column_headers + ('Project',)
        search = {'all_tenants': parsed_args.all_projects}
        data = compute_client.security_groups.list(search_opts=search)

        project_hash = {}
        try:
            projects = self.app.client_manager.identity.projects.list()
        except ksc_exc.ClientException:
            # This fails when the user is not an admin, just move along
            pass
        else:
            for project in projects:
                project_hash[project.id] = project

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                    formatters={'Tenant ID': _get_project},
                ) for s in data))


class SetSecurityGroup(show.ShowOne):
    """Set security group properties"""

    log = logging.getLogger(__name__ + '.SetSecurityGroup')

    def get_parser(self, prog_name):
        parser = super(SetSecurityGroup, self).get_parser(prog_name)
        parser.add_argument(
            'group',
            metavar='<group>',
            help='Name or ID of security group to change',
        )
        parser.add_argument(
            '--name',
            metavar='<new-name>',
            help='New security group name',
        )
        parser.add_argument(
            "--description",
            metavar="<description>",
            help="New security group name",
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):

        compute_client = self.app.client_manager.compute
        data = utils.find_resource(
            compute_client.security_groups,
            parsed_args.group,
        )

        if parsed_args.name:
            data.name = parsed_args.name
        if parsed_args.description:
            data.description = parsed_args.description

        info = {}
        info.update(compute_client.security_groups.update(
            data,
            data.name,
            data.description,
        )._info)

        if info:
            return zip(*sorted(six.iteritems(info)))
        else:
            return ({}, {})


class ShowSecurityGroup(show.ShowOne):
    """Show a specific security group"""

    log = logging.getLogger(__name__ + '.ShowSecurityGroup')

    def get_parser(self, prog_name):
        parser = super(ShowSecurityGroup, self).get_parser(prog_name)
        parser.add_argument(
            'group',
            metavar='<group>',
            help='Name or ID of security group to change',
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):

        compute_client = self.app.client_manager.compute
        info = {}
        info.update(utils.find_resource(
            compute_client.security_groups,
            parsed_args.group,
        )._info)
        rules = []
        for r in info['rules']:
            rules.append(utils.format_dict(_xform_security_group_rule(r)))

        # Format rules into a list of strings
        info.update(
            {'rules': rules}
        )
        # Map 'tenant_id' column to 'project_id'
        info.update(
            {'project_id': info.pop('tenant_id')}
        )

        return zip(*sorted(six.iteritems(info)))


class CreateSecurityGroupRule(show.ShowOne):
    """Create a new security group rule"""

    log = logging.getLogger(__name__ + ".CreateSecurityGroupRule")

    def get_parser(self, prog_name):
        parser = super(CreateSecurityGroupRule, self).get_parser(prog_name)
        parser.add_argument(
            'group',
            metavar='<group>',
            help='Create rule in this security group',
        )
        parser.add_argument(
            "--proto",
            metavar="<proto>",
            default="tcp",
            help="IP protocol (icmp, tcp, udp; default: tcp)",
        )
        parser.add_argument(
            "--src-ip",
            metavar="<ip-address>",
            default="0.0.0.0/0",
            help="Source IP (may use CIDR notation; default: 0.0.0.0/0)",
        )
        parser.add_argument(
            "--dst-port",
            metavar="<port-range>",
            default=(0, 0),
            action=parseractions.RangeAction,
            help="Destination port, may be a range: 137:139 (default: 0; "
                 "only required for proto tcp and udp)",
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        compute_client = self.app.client_manager.compute
        group = utils.find_resource(
            compute_client.security_groups,
            parsed_args.group,
        )
        if parsed_args.proto.lower() == 'icmp':
            from_port, to_port = -1, -1
        else:
            from_port, to_port = parsed_args.dst_port
        data = compute_client.security_group_rules.create(
            group.id,
            parsed_args.proto,
            from_port,
            to_port,
            parsed_args.src_ip,
        )

        info = _xform_security_group_rule(data._info)
        return zip(*sorted(six.iteritems(info)))


class DeleteSecurityGroupRule(command.Command):
    """Delete a security group rule"""

    log = logging.getLogger(__name__ + '.DeleteSecurityGroupRule')

    def get_parser(self, prog_name):
        parser = super(DeleteSecurityGroupRule, self).get_parser(prog_name)
        parser.add_argument(
            'rule',
            metavar='<rule>',
            help='Security group rule ID to delete',
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):

        compute_client = self.app.client_manager.compute
        compute_client.security_group_rules.delete(parsed_args.rule)
        return


class ListSecurityGroupRule(lister.Lister):
    """List all security group rules"""

    log = logging.getLogger(__name__ + ".ListSecurityGroupRule")

    def get_parser(self, prog_name):
        parser = super(ListSecurityGroupRule, self).get_parser(prog_name)
        parser.add_argument(
            'group',
            metavar='<group>',
            help='List all rules in this security group',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        compute_client = self.app.client_manager.compute
        group = utils.find_resource(
            compute_client.security_groups,
            parsed_args.group,
        )

        # Argh, the rules are not Resources...
        rules = []
        for rule in group.rules:
            rules.append(security_group_rules.SecurityGroupRule(
                compute_client.security_group_rules,
                _xform_security_group_rule(rule),
            ))

        columns = column_headers = (
            "ID",
            "IP Protocol",
            "IP Range",
            "Port Range",
        )
        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                ) for s in rules))
