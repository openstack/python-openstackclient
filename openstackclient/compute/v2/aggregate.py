#   Copyright 2012 OpenStack Foundation
#   Copyright 2013 Nebula Inc.
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

"""Compute v2 Aggregate action implementations"""

import logging
import typing as ty

from openstack import utils as sdk_utils
from osc_lib.cli import format_columns
from osc_lib.cli import parseractions
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _


LOG = logging.getLogger(__name__)


_aggregate_formatters = {
    'Hosts': format_columns.ListColumn,
    'Metadata': format_columns.DictColumn,
    'hosts': format_columns.ListColumn,
    'metadata': format_columns.DictColumn,
}


def _get_aggregate_columns(item):
    # To maintain backwards compatibility we need to rename sdk props to
    # whatever OSC was using before
    column_map = {
        'metadata': 'properties',
    }
    hidden_columns = ['links', 'location']
    return utils.get_osc_show_columns_for_sdk_resource(
        item, column_map, hidden_columns
    )


class AddAggregateHost(command.ShowOne):
    _description = _("Add host to aggregate")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'aggregate',
            metavar='<aggregate>',
            help=_("Aggregate (name or ID)"),
        )
        parser.add_argument(
            'host', metavar='<host>', help=_("Host to add to <aggregate>")
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute

        aggregate = compute_client.find_aggregate(
            parsed_args.aggregate, ignore_missing=False
        )

        aggregate = compute_client.add_host_to_aggregate(
            aggregate.id, parsed_args.host
        )

        display_columns, columns = _get_aggregate_columns(aggregate)
        data = utils.get_item_properties(
            aggregate, columns, formatters=_aggregate_formatters
        )
        return (display_columns, data)


class CreateAggregate(command.ShowOne):
    _description = _("Create a new aggregate")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "name", metavar="<name>", help=_("New aggregate name")
        )
        parser.add_argument(
            "--zone",
            metavar="<availability-zone>",
            help=_("Availability zone name"),
        )
        parser.add_argument(
            "--property",
            metavar="<key=value>",
            action=parseractions.KeyValueAction,
            dest="properties",
            help=_(
                "Property to add to this aggregate "
                "(repeat option to set multiple properties)"
            ),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute

        attrs = {'name': parsed_args.name}

        if parsed_args.zone:
            attrs['availability_zone'] = parsed_args.zone

        aggregate = compute_client.create_aggregate(**attrs)

        if parsed_args.properties:
            aggregate = compute_client.set_aggregate_metadata(
                aggregate.id,
                parsed_args.properties,
            )

        display_columns, columns = _get_aggregate_columns(aggregate)
        data = utils.get_item_properties(
            aggregate, columns, formatters=_aggregate_formatters
        )
        return (display_columns, data)


class DeleteAggregate(command.Command):
    _description = _("Delete existing aggregate(s)")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'aggregate',
            metavar='<aggregate>',
            nargs='+',
            help=_("Aggregate(s) to delete (name or ID)"),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        result = 0
        for a in parsed_args.aggregate:
            try:
                aggregate = compute_client.find_aggregate(
                    a, ignore_missing=False
                )
                compute_client.delete_aggregate(
                    aggregate.id, ignore_missing=False
                )
            except Exception as e:
                result += 1
                LOG.error(
                    _(
                        "Failed to delete aggregate with name or "
                        "ID '%(aggregate)s': %(e)s"
                    ),
                    {'aggregate': a, 'e': e},
                )

        if result > 0:
            total = len(parsed_args.aggregate)
            msg = _("%(result)s of %(total)s aggregates failed to delete.") % {
                'result': result,
                'total': total,
            }
            raise exceptions.CommandError(msg)


class ListAggregate(command.Lister):
    _description = _("List all aggregates")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_("List additional fields in output"),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute

        aggregates = list(compute_client.aggregates())

        if sdk_utils.supports_microversion(compute_client, '2.41'):
            column_headers: tuple[str, ...] = ("ID", "UUID")
            columns: tuple[str, ...] = ("id", "uuid")
        else:
            column_headers = ("ID",)
            columns = ("id",)

        column_headers += (
            "Name",
            "Availability Zone",
        )
        columns += (
            "name",
            "availability_zone",
        )

        if parsed_args.long:
            # Remove availability_zone from metadata because Nova doesn't
            for aggregate in aggregates:
                if 'availability_zone' in aggregate.metadata:
                    aggregate.metadata.pop('availability_zone')

            column_headers += (
                "Properties",
                "Hosts",
            )
            columns += (
                "metadata",
                "hosts",
            )

        return (
            column_headers,
            (
                utils.get_item_properties(
                    s, columns, formatters=_aggregate_formatters
                )
                for s in aggregates
            ),
        )


class RemoveAggregateHost(command.ShowOne):
    _description = _("Remove host from aggregate")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'aggregate',
            metavar='<aggregate>',
            help=_("Aggregate (name or ID)"),
        )
        parser.add_argument(
            'host', metavar='<host>', help=_("Host to remove from <aggregate>")
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute

        aggregate = compute_client.find_aggregate(
            parsed_args.aggregate, ignore_missing=False
        )

        aggregate = compute_client.remove_host_from_aggregate(
            aggregate.id, parsed_args.host
        )

        display_columns, columns = _get_aggregate_columns(aggregate)
        data = utils.get_item_properties(
            aggregate, columns, formatters=_aggregate_formatters
        )
        return (display_columns, data)


class SetAggregate(command.Command):
    _description = _("Set aggregate properties")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'aggregate',
            metavar='<aggregate>',
            help=_("Aggregate to modify (name or ID)"),
        )
        parser.add_argument(
            '--name', metavar='<name>', help=_("Set aggregate name")
        )
        parser.add_argument(
            "--zone",
            metavar="<availability-zone>",
            help=_("Set availability zone name"),
        )
        parser.add_argument(
            "--property",
            metavar="<key=value>",
            action=parseractions.KeyValueAction,
            dest="properties",
            help=_(
                "Property to set on <aggregate> "
                "(repeat option to set multiple properties)"
            ),
        )
        parser.add_argument(
            "--no-property",
            action="store_true",
            help=_(
                "Remove all properties from <aggregate> "
                "(specify both --property and --no-property to "
                "overwrite the current properties)"
            ),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        aggregate = compute_client.find_aggregate(
            parsed_args.aggregate, ignore_missing=False
        )

        kwargs = {}
        if parsed_args.name:
            kwargs['name'] = parsed_args.name
        if parsed_args.zone:
            kwargs['availability_zone'] = parsed_args.zone
        if kwargs:
            compute_client.update_aggregate(aggregate.id, **kwargs)

        properties: dict[str, ty.Any] = {}
        if parsed_args.no_property:
            # NOTE(RuiChen): "availability_zone" can not be unset from
            # properties. It is already excluded from show and create output.
            properties.update(
                {
                    key: None
                    for key in aggregate.metadata.keys()
                    if key != 'availability_zone'
                }
            )

        if parsed_args.properties:
            properties.update(parsed_args.properties)

        if properties:
            compute_client.set_aggregate_metadata(aggregate.id, properties)


class ShowAggregate(command.ShowOne):
    _description = _("Display aggregate details")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'aggregate',
            metavar='<aggregate>',
            help=_("Aggregate to display (name or ID)"),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        aggregate = compute_client.find_aggregate(
            parsed_args.aggregate, ignore_missing=False
        )

        # Remove availability_zone from metadata because Nova doesn't
        if 'availability_zone' in aggregate.metadata:
            aggregate.metadata.pop('availability_zone')

        display_columns, columns = _get_aggregate_columns(aggregate)
        data = utils.get_item_properties(
            aggregate, columns, formatters=_aggregate_formatters
        )
        return (display_columns, data)


class UnsetAggregate(command.Command):
    _description = _("Unset aggregate properties")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "aggregate",
            metavar="<aggregate>",
            help=_("Aggregate to modify (name or ID)"),
        )
        parser.add_argument(
            "--property",
            metavar="<key>",
            action="append",
            default=[],
            dest="properties",
            help=_(
                "Property to remove from aggregate "
                "(repeat option to remove multiple properties)"
            ),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        aggregate = compute_client.find_aggregate(
            parsed_args.aggregate, ignore_missing=False
        )

        properties = {key: None for key in parsed_args.properties}

        if properties:
            compute_client.set_aggregate_metadata(aggregate.id, properties)


class CacheImageForAggregate(command.Command):
    _description = _("Request image caching for aggregate")
    # NOTE(gtema): According to stephenfin and dansmith there is no and will
    # not be anything to return.

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'aggregate',
            metavar='<aggregate>',
            help=_("Aggregate (name or ID)"),
        )
        parser.add_argument(
            'image',
            metavar='<image>',
            nargs='+',
            help=_(
                "Image ID to request caching for aggregate (name or ID). "
                "May be specified multiple times."
            ),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute

        if not sdk_utils.supports_microversion(compute_client, '2.81'):
            msg = _(
                'This operation requires server support for '
                'API microversion 2.81'
            )
            raise exceptions.CommandError(msg)

        aggregate = compute_client.find_aggregate(
            parsed_args.aggregate, ignore_missing=False
        )

        images = []
        for img in parsed_args.image:
            image = self.app.client_manager.sdk_connection.image.find_image(
                img, ignore_missing=False
            )
            images.append(image.id)

        compute_client.aggregate_precache_images(aggregate.id, images)
