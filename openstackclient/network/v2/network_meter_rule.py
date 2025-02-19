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

"""Meter Rule Implementations"""

import logging
import typing as ty

from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _
from openstackclient.identity import common as identity_common
from openstackclient.network import common

LOG = logging.getLogger(__name__)


def _get_columns(item):
    hidden_columns = ['location', 'tenant_id']
    return utils.get_osc_show_columns_for_sdk_resource(
        item, {}, hidden_columns
    )


def _get_attrs(client_manager, parsed_args):
    attrs: dict[str, ty.Any] = {}

    if parsed_args.exclude:
        attrs['excluded'] = True
    if parsed_args.include:
        attrs['excluded'] = False
    if parsed_args.ingress or not parsed_args.egress:
        attrs['direction'] = 'ingress'
    if parsed_args.egress:
        attrs['direction'] = 'egress'
    if parsed_args.remote_ip_prefix is not None:
        attrs['remote_ip_prefix'] = parsed_args.remote_ip_prefix
    if parsed_args.source_ip_prefix is not None:
        attrs['source_ip_prefix'] = parsed_args.source_ip_prefix
    if parsed_args.destination_ip_prefix is not None:
        attrs['destination_ip_prefix'] = parsed_args.destination_ip_prefix
    if parsed_args.meter is not None:
        attrs['metering_label_id'] = parsed_args.meter
    if parsed_args.project is not None:
        identity_client = client_manager.identity
        project_id = identity_common.find_project(
            identity_client,
            parsed_args.project,
            parsed_args.project_domain,
        ).id
        attrs['project_id'] = project_id

    return attrs


class CreateMeterRule(command.ShowOne, common.NeutronCommandWithExtraArgs):
    _description = _("Create a new meter rule")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)

        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_("Owner's project (name or ID)"),
        )
        identity_common.add_project_domain_option_to_parser(parser)
        exclude_group = parser.add_mutually_exclusive_group()
        exclude_group.add_argument(
            '--exclude',
            action='store_true',
            help=_("Exclude remote IP prefix from traffic count"),
        )
        exclude_group.add_argument(
            '--include',
            action='store_true',
            help=_("Include remote IP prefix from traffic count (default)"),
        )
        direction_group = parser.add_mutually_exclusive_group()
        direction_group.add_argument(
            '--ingress',
            action='store_true',
            help=_("Apply rule to incoming network traffic (default)"),
        )
        direction_group.add_argument(
            '--egress',
            action='store_true',
            help=_('Apply rule to outgoing network traffic'),
        )
        parser.add_argument(
            '--remote-ip-prefix',
            metavar='<remote-ip-prefix>',
            required=False,
            help=_('The remote IP prefix to associate with this rule'),
        )
        parser.add_argument(
            '--source-ip-prefix',
            metavar='<remote-ip-prefix>',
            required=False,
            help=_('The source IP prefix to associate with this rule'),
        )
        parser.add_argument(
            '--destination-ip-prefix',
            metavar='<remote-ip-prefix>',
            required=False,
            help=_('The destination IP prefix to associate with this rule'),
        )
        parser.add_argument(
            'meter',
            metavar='<meter>',
            help=_('Label to associate with this metering rule (name or ID)'),
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        _meter = client.find_metering_label(
            parsed_args.meter, ignore_missing=False
        )
        parsed_args.meter = _meter.id
        attrs = _get_attrs(self.app.client_manager, parsed_args)
        attrs.update(
            self._parse_extra_properties(parsed_args.extra_properties)
        )
        obj = client.create_metering_label_rule(**attrs)
        display_columns, columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns, formatters={})

        return (display_columns, data)


class DeleteMeterRule(command.Command):
    _description = _("Delete meter rule(s)")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)

        parser.add_argument(
            'meter_rule_id',
            metavar='<meter-rule-id>',
            nargs='+',
            help=_('Meter rule to delete (ID only)'),
        )

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        result = 0

        for id in parsed_args.meter_rule_id:
            try:
                obj = client.find_metering_label_rule(id, ignore_missing=False)
                client.delete_metering_label_rule(obj)
            except Exception as e:
                result += 1
                LOG.error(
                    _("Failed to delete meter rule with ID '%(id)s': %(e)s"),
                    {"id": id, "e": e},
                )

        if result > 0:
            total = len(parsed_args.meter_rule_id)
            msg = _(
                "%(result)s of %(total)s meter rules failed to delete."
            ) % {"result": result, "total": total}
            raise exceptions.CommandError(msg)


class ListMeterRule(command.Lister):
    _description = _("List meter rules")

    def take_action(self, parsed_args):
        client = self.app.client_manager.network

        columns = (
            'id',
            'excluded',
            'direction',
            'remote_ip_prefix',
            'source_ip_prefix',
            'destination_ip_prefix',
        )
        column_headers = (
            'ID',
            'Excluded',
            'Direction',
            'Remote IP Prefix',
            'Source IP Prefix',
            'Destination IP Prefix',
        )
        data = client.metering_label_rules()
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


class ShowMeterRule(command.ShowOne):
    _description = _("Display meter rules details")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'meter_rule_id',
            metavar='<meter-rule-id>',
            help=_('Meter rule (ID only)'),
        )
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.network
        obj = client.find_metering_label_rule(
            parsed_args.meter_rule_id, ignore_missing=False
        )
        display_columns, columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns)
        return display_columns, data
