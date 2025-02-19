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

import itertools

from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _
from openstackclient.network import common

RULE_TYPE_BANDWIDTH_LIMIT = 'bandwidth-limit'
RULE_TYPE_DSCP_MARKING = 'dscp-marking'
RULE_TYPE_MINIMUM_BANDWIDTH = 'minimum-bandwidth'
RULE_TYPE_MINIMUM_PACKET_RATE = 'minimum-packet-rate'
MANDATORY_PARAMETERS = {
    RULE_TYPE_MINIMUM_BANDWIDTH: {'min_kbps', 'direction'},
    RULE_TYPE_MINIMUM_PACKET_RATE: {'min_kpps', 'direction'},
    RULE_TYPE_DSCP_MARKING: {'dscp_mark'},
    RULE_TYPE_BANDWIDTH_LIMIT: {'max_kbps'},
}
OPTIONAL_PARAMETERS = {
    RULE_TYPE_MINIMUM_BANDWIDTH: set(),
    RULE_TYPE_MINIMUM_PACKET_RATE: set(),
    RULE_TYPE_DSCP_MARKING: set(),
    RULE_TYPE_BANDWIDTH_LIMIT: {'direction', 'max_burst_kbps'},
}
DIRECTION_EGRESS = 'egress'
DIRECTION_INGRESS = 'ingress'
DIRECTION_ANY = 'any'
DSCP_VALID_MARKS = [
    0,
    8,
    10,
    12,
    14,
    16,
    18,
    20,
    22,
    24,
    26,
    28,
    30,
    32,
    34,
    36,
    38,
    40,
    46,
    48,
    56,
]

ACTION_CREATE = 'create'
ACTION_DELETE = 'delete'
ACTION_FIND = 'find'
ACTION_SET = 'update'
ACTION_SHOW = 'get'


def _get_columns(item):
    hidden_columns = ['location', 'tenant_id']
    return utils.get_osc_show_columns_for_sdk_resource(
        item, {}, hidden_columns
    )


def _check_type_parameters(attrs, type, is_create):
    req_params = MANDATORY_PARAMETERS[type]
    opt_params = OPTIONAL_PARAMETERS[type]
    type_params = req_params | opt_params
    notreq_params = set(
        itertools.chain(
            *[v for k, v in MANDATORY_PARAMETERS.items() if k != type]
        )
    )
    notreq_params -= type_params
    if is_create and None in map(attrs.get, req_params):
        msg = _(
            '"Create" rule command for type "%(rule_type)s" requires '
            'arguments: %(args)s'
        ) % {'rule_type': type, 'args': ", ".join(sorted(req_params))}
        raise exceptions.CommandError(msg)
    if set(attrs.keys()) & notreq_params:
        msg = _(
            'Rule type "%(rule_type)s" only requires arguments: %(args)s'
        ) % {'rule_type': type, 'args': ", ".join(sorted(type_params))}
        raise exceptions.CommandError(msg)


def _get_attrs(network_client, parsed_args, is_create=False):
    attrs = {}
    qos = network_client.find_qos_policy(
        parsed_args.qos_policy, ignore_missing=False
    )
    attrs['qos_policy_id'] = qos.id
    if not is_create:
        attrs['id'] = parsed_args.id
        rule_type = _find_rule_type(qos, parsed_args.id)
        if not rule_type:
            msg = _('Rule ID %(rule_id)s not found') % {
                'rule_id': parsed_args.id
            }
            raise exceptions.CommandError(msg)
    else:
        rule_type = parsed_args.type
    if parsed_args.max_kbps is not None:
        attrs['max_kbps'] = parsed_args.max_kbps
    if parsed_args.max_burst_kbits is not None:
        # NOTE(ralonsoh): this parameter must be changed in SDK and then in
        #                 Neutron API, from 'max_burst_kbps' to
        #                 'max_burst_kbits'
        attrs['max_burst_kbps'] = parsed_args.max_burst_kbits
    if parsed_args.dscp_mark is not None:
        attrs['dscp_mark'] = parsed_args.dscp_mark
    if parsed_args.min_kbps is not None:
        attrs['min_kbps'] = parsed_args.min_kbps
    if parsed_args.min_kpps is not None:
        attrs['min_kpps'] = parsed_args.min_kpps
    if parsed_args.ingress:
        attrs['direction'] = DIRECTION_INGRESS
    if parsed_args.egress:
        attrs['direction'] = DIRECTION_EGRESS
    if parsed_args.any:
        if rule_type == RULE_TYPE_MINIMUM_PACKET_RATE:
            attrs['direction'] = DIRECTION_ANY
        else:
            msg = _(
                'Direction "any" can only be used with '
                '%(rule_type_min_pps)s rule type'
            ) % {'rule_type_min_pps': RULE_TYPE_MINIMUM_PACKET_RATE}
            raise exceptions.CommandError(msg)
    _check_type_parameters(attrs, rule_type, is_create)
    return attrs


def _get_item_properties(item, fields):
    """Return a tuple containing the item properties."""
    row = []
    for field in fields:
        row.append(item.get(field, ''))
    return tuple(row)


def _rule_action_call(client, action, rule_type):
    rule_type = rule_type.replace('-', '_')
    func_name = f'{action}_qos_{rule_type}_rule'
    return getattr(client, func_name)


def _find_rule_type(qos, rule_id):
    for rule in (r for r in qos.rules if r['id'] == rule_id):
        return rule['type'].replace('_', '-')
    return None


def _add_rule_arguments(parser):
    parser.add_argument(
        '--max-kbps',
        dest='max_kbps',
        metavar='<max-kbps>',
        type=int,
        help=_('Maximum bandwidth in kbps'),
    )
    parser.add_argument(
        '--max-burst-kbits',
        dest='max_burst_kbits',
        metavar='<max-burst-kbits>',
        type=int,
        help=_(
            'Maximum burst in kilobits, 0 or not specified means '
            'automatic, which is 80%% of the bandwidth limit, which works '
            'for typical TCP traffic. For details check the QoS user '
            'workflow.'
        ),
    )
    parser.add_argument(
        '--dscp-mark',
        dest='dscp_mark',
        metavar='<dscp-mark>',
        type=int,
        help=_(
            'DSCP mark: value can be 0, even numbers from 8-56, '
            'excluding 42, 44, 50, 52, and 54'
        ),
    )
    parser.add_argument(
        '--min-kbps',
        dest='min_kbps',
        metavar='<min-kbps>',
        type=int,
        help=_('Minimum guaranteed bandwidth in kbps'),
    )
    parser.add_argument(
        '--min-kpps',
        dest='min_kpps',
        metavar='<min-kpps>',
        type=int,
        help=_('Minimum guaranteed packet rate in kpps'),
    )
    direction_group = parser.add_mutually_exclusive_group()
    direction_group.add_argument(
        '--ingress',
        action='store_true',
        help=_("Ingress traffic direction from the project point of view"),
    )
    direction_group.add_argument(
        '--egress',
        action='store_true',
        help=_("Egress traffic direction from the project point of view"),
    )
    direction_group.add_argument(
        '--any',
        action='store_true',
        help=_(
            "Any traffic direction from the project point of view. Can be "
            "used only with minimum packet rate rule."
        ),
    )


class CreateNetworkQosRule(
    command.ShowOne, common.NeutronCommandWithExtraArgs
):
    _description = _("Create new Network QoS rule")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'qos_policy',
            metavar='<qos-policy>',
            help=_('QoS policy that contains the rule (name or ID)'),
        )
        parser.add_argument(
            '--type',
            metavar='<type>',
            required=True,
            choices=[
                RULE_TYPE_MINIMUM_BANDWIDTH,
                RULE_TYPE_MINIMUM_PACKET_RATE,
                RULE_TYPE_DSCP_MARKING,
                RULE_TYPE_BANDWIDTH_LIMIT,
            ],
            help=(
                _('QoS rule type (%s)')
                % ", ".join(MANDATORY_PARAMETERS.keys())
            ),
        )
        _add_rule_arguments(parser)
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network
        try:
            attrs = _get_attrs(network_client, parsed_args, is_create=True)
            attrs.update(
                self._parse_extra_properties(parsed_args.extra_properties)
            )
            obj = _rule_action_call(
                network_client, ACTION_CREATE, parsed_args.type
            )(attrs.pop('qos_policy_id'), **attrs)
        except Exception as e:
            msg = _('Failed to create Network QoS rule: %(e)s') % {'e': e}
            raise exceptions.CommandError(msg)
        display_columns, columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns)
        return display_columns, data


class DeleteNetworkQosRule(command.Command):
    _description = _("Delete Network QoS rule")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'qos_policy',
            metavar='<qos-policy>',
            help=_('QoS policy that contains the rule (name or ID)'),
        )
        parser.add_argument(
            'id',
            metavar='<rule-id>',
            help=_('Network QoS rule to delete (ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network
        rule_id = parsed_args.id
        try:
            qos = network_client.find_qos_policy(
                parsed_args.qos_policy, ignore_missing=False
            )
            rule_type = _find_rule_type(qos, rule_id)
            if not rule_type:
                raise Exception(f'Rule {rule_id} not found')
            _rule_action_call(network_client, ACTION_DELETE, rule_type)(
                rule_id, qos.id
            )
        except Exception as e:
            msg = _(
                'Failed to delete Network QoS rule ID "%(rule)s": %(e)s'
            ) % {'rule': rule_id, 'e': e}
            raise exceptions.CommandError(msg)


class ListNetworkQosRule(command.Lister):
    _description = _("List Network QoS rules")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'qos_policy',
            metavar='<qos-policy>',
            help=_('QoS policy that contains the rule (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        columns = (
            'id',
            'qos_policy_id',
            'type',
            'max_kbps',
            'max_burst_kbps',
            'min_kbps',
            'min_kpps',
            'dscp_mark',
            'direction',
        )
        column_headers = (
            'ID',
            'QoS Policy ID',
            'Type',
            'Max Kbps',
            'Max Burst Kbits',
            'Min Kbps',
            'Min Kpps',
            'DSCP mark',
            'Direction',
        )
        qos = client.find_qos_policy(
            parsed_args.qos_policy, ignore_missing=False
        )
        data = qos.rules
        return (
            column_headers,
            (_get_item_properties(s, columns) for s in data),
        )


class SetNetworkQosRule(common.NeutronCommandWithExtraArgs):
    _description = _("Set Network QoS rule properties")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'qos_policy',
            metavar='<qos-policy>',
            help=_('QoS policy that contains the rule (name or ID)'),
        )
        parser.add_argument(
            'id',
            metavar='<rule-id>',
            help=_('Network QoS rule to set (ID)'),
        )
        _add_rule_arguments(parser)
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network
        try:
            qos = network_client.find_qos_policy(
                parsed_args.qos_policy, ignore_missing=False
            )
            rule_type = _find_rule_type(qos, parsed_args.id)
            if not rule_type:
                raise Exception('Rule not found')
            attrs = _get_attrs(network_client, parsed_args)
            attrs.update(
                self._parse_extra_properties(parsed_args.extra_properties)
            )
            qos_id = attrs.pop('qos_policy_id')
            qos_rule = _rule_action_call(
                network_client, ACTION_FIND, rule_type
            )(attrs.pop('id'), qos_id)
            _rule_action_call(network_client, ACTION_SET, rule_type)(
                qos_rule, qos_id, **attrs
            )
        except Exception as e:
            msg = _('Failed to set Network QoS rule ID "%(rule)s": %(e)s') % {
                'rule': parsed_args.id,
                'e': e,
            }
            raise exceptions.CommandError(msg)


class ShowNetworkQosRule(command.ShowOne):
    _description = _("Display Network QoS rule details")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'qos_policy',
            metavar='<qos-policy>',
            help=_('QoS policy that contains the rule (name or ID)'),
        )
        parser.add_argument(
            'id',
            metavar='<rule-id>',
            help=_('Network QoS rule to show (ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        network_client = self.app.client_manager.network
        rule_id = parsed_args.id
        try:
            qos = network_client.find_qos_policy(
                parsed_args.qos_policy, ignore_missing=False
            )
            rule_type = _find_rule_type(qos, rule_id)
            if not rule_type:
                raise Exception('Rule not found')
            obj = _rule_action_call(network_client, ACTION_SHOW, rule_type)(
                rule_id, qos.id
            )
        except Exception as e:
            msg = _('Failed to show Network QoS rule ID "%(rule)s": %(e)s') % {
                'rule': rule_id,
                'e': e,
            }
            raise exceptions.CommandError(msg)
        display_columns, columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns)
        return display_columns, data
