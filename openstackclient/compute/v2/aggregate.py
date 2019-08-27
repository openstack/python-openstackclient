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

from osc_lib.cli import format_columns
from osc_lib.cli import parseractions
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils
import six

from openstackclient.i18n import _


LOG = logging.getLogger(__name__)


class AddAggregateHost(command.ShowOne):
    _description = _("Add host to aggregate")

    def get_parser(self, prog_name):
        parser = super(AddAggregateHost, self).get_parser(prog_name)
        parser.add_argument(
            'aggregate',
            metavar='<aggregate>',
            help=_("Aggregate (name or ID)")
        )
        parser.add_argument(
            'host',
            metavar='<host>',
            help=_("Host to add to <aggregate>")
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute

        aggregate = utils.find_resource(
            compute_client.aggregates,
            parsed_args.aggregate,
        )
        data = compute_client.aggregates.add_host(aggregate, parsed_args.host)

        info = {}
        info.update(data._info)

        # Special mapping for columns to make the output easier to read:
        # 'metadata' --> 'properties'
        info.update(
            {
                'hosts': format_columns.ListColumn(info.pop('hosts')),
                'properties': format_columns.DictColumn(info.pop('metadata')),
            },
        )
        return zip(*sorted(six.iteritems(info)))


class CreateAggregate(command.ShowOne):
    _description = _("Create a new aggregate")

    def get_parser(self, prog_name):
        parser = super(CreateAggregate, self).get_parser(prog_name)
        parser.add_argument(
            "name",
            metavar="<name>",
            help=_("New aggregate name")
        )
        parser.add_argument(
            "--zone",
            metavar="<availability-zone>",
            help=_("Availability zone name")
        )
        parser.add_argument(
            "--property",
            metavar="<key=value>",
            action=parseractions.KeyValueAction,
            help=_("Property to add to this aggregate "
                   "(repeat option to set multiple properties)")
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute

        info = {}
        data = compute_client.aggregates.create(
            parsed_args.name,
            parsed_args.zone,
        )
        info.update(data._info)

        if parsed_args.property:
            info.update(compute_client.aggregates.set_metadata(
                data,
                parsed_args.property,
            )._info)

        # Special mapping for columns to make the output easier to read:
        # 'metadata' --> 'properties'
        hosts = None
        properties = None
        if 'hosts' in info.keys():
            hosts = format_columns.ListColumn(info.pop('hosts'))
        if 'metadata' in info.keys():
            properties = format_columns.DictColumn(info.pop('metadata'))
        info.update(
            {
                'hosts': hosts,
                'properties': properties,
            },
        )
        return zip(*sorted(six.iteritems(info)))


class DeleteAggregate(command.Command):
    _description = _("Delete existing aggregate(s)")

    def get_parser(self, prog_name):
        parser = super(DeleteAggregate, self).get_parser(prog_name)
        parser.add_argument(
            'aggregate',
            metavar='<aggregate>',
            nargs='+',
            help=_("Aggregate(s) to delete (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        result = 0
        for a in parsed_args.aggregate:
            try:
                data = utils.find_resource(
                    compute_client.aggregates, a)
                compute_client.aggregates.delete(data.id)
            except Exception as e:
                result += 1
                LOG.error(_("Failed to delete aggregate with name or "
                          "ID '%(aggregate)s': %(e)s"),
                          {'aggregate': a, 'e': e})

        if result > 0:
            total = len(parsed_args.aggregate)
            msg = (_("%(result)s of %(total)s aggregates failed "
                   "to delete.") % {'result': result, 'total': total})
            raise exceptions.CommandError(msg)


class ListAggregate(command.Lister):
    _description = _("List all aggregates")

    def get_parser(self, prog_name):
        parser = super(ListAggregate, self).get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_("List additional fields in output")
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute

        data = compute_client.aggregates.list()

        if parsed_args.long:
            # Remove availability_zone from metadata because Nova doesn't
            for d in data:
                if 'availability_zone' in d.metadata:
                    d.metadata.pop('availability_zone')
            # This is the easiest way to change column headers
            column_headers = (
                "ID",
                "Name",
                "Availability Zone",
                "Properties",
            )
            columns = (
                "ID",
                "Name",
                "Availability Zone",
                "Metadata",
            )
        else:
            column_headers = columns = (
                "ID",
                "Name",
                "Availability Zone",
            )

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                    formatters={
                        'Hosts': format_columns.ListColumn,
                        'Metadata': format_columns.DictColumn,
                    },
                ) for s in data))


class RemoveAggregateHost(command.ShowOne):
    _description = _("Remove host from aggregate")

    def get_parser(self, prog_name):
        parser = super(RemoveAggregateHost, self).get_parser(prog_name)
        parser.add_argument(
            'aggregate',
            metavar='<aggregate>',
            help=_("Aggregate (name or ID)")
        )
        parser.add_argument(
            'host',
            metavar='<host>',
            help=_("Host to remove from <aggregate>")
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute

        aggregate = utils.find_resource(
            compute_client.aggregates,
            parsed_args.aggregate,
        )
        data = compute_client.aggregates.remove_host(
            aggregate,
            parsed_args.host,
        )

        info = {}
        info.update(data._info)

        # Special mapping for columns to make the output easier to read:
        # 'metadata' --> 'properties'
        info.update(
            {
                'hosts': format_columns.ListColumn(info.pop('hosts')),
                'properties': format_columns.DictColumn(info.pop('metadata')),
            },
        )
        return zip(*sorted(six.iteritems(info)))


class SetAggregate(command.Command):
    _description = _("Set aggregate properties")

    def get_parser(self, prog_name):
        parser = super(SetAggregate, self).get_parser(prog_name)
        parser.add_argument(
            'aggregate',
            metavar='<aggregate>',
            help=_("Aggregate to modify (name or ID)")
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_("Set aggregate name")
        )
        parser.add_argument(
            "--zone",
            metavar="<availability-zone>",
            help=_("Set availability zone name")
        )
        parser.add_argument(
            "--property",
            metavar="<key=value>",
            action=parseractions.KeyValueAction,
            help=_("Property to set on <aggregate> "
                   "(repeat option to set multiple properties)")
        )
        parser.add_argument(
            "--no-property",
            dest="no_property",
            action="store_true",
            help=_("Remove all properties from <aggregate> "
                   "(specify both --property and --no-property to "
                   "overwrite the current properties)"),
        )
        return parser

    def take_action(self, parsed_args):

        compute_client = self.app.client_manager.compute
        aggregate = utils.find_resource(
            compute_client.aggregates,
            parsed_args.aggregate,
        )

        kwargs = {}
        if parsed_args.name:
            kwargs['name'] = parsed_args.name
        if parsed_args.zone:
            kwargs['availability_zone'] = parsed_args.zone
        if kwargs:
            compute_client.aggregates.update(
                aggregate,
                kwargs
            )

        set_property = {}
        if parsed_args.no_property:
            # NOTE(RuiChen): "availability_zone" is removed from response of
            #                aggregate show and create commands, don't see it
            #                anywhere, so pop it, avoid the unexpected server
            #                exception(can't unset the availability zone from
            #                aggregate metadata in nova).
            set_property.update({key: None
                                 for key in aggregate.metadata.keys()
                                 if key != 'availability_zone'})
        if parsed_args.property:
            set_property.update(parsed_args.property)

        if set_property:
            compute_client.aggregates.set_metadata(
                aggregate,
                set_property
            )


class ShowAggregate(command.ShowOne):
    _description = _("Display aggregate details")

    def get_parser(self, prog_name):
        parser = super(ShowAggregate, self).get_parser(prog_name)
        parser.add_argument(
            'aggregate',
            metavar='<aggregate>',
            help=_("Aggregate to display (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):

        compute_client = self.app.client_manager.compute
        data = utils.find_resource(
            compute_client.aggregates,
            parsed_args.aggregate,
        )
        # Remove availability_zone from metadata because Nova doesn't
        if 'availability_zone' in data.metadata:
            data.metadata.pop('availability_zone')

        # Special mapping for columns to make the output easier to read:
        # 'metadata' --> 'properties'
        data._info.update(
            {
                'hosts': format_columns.ListColumn(
                    data._info.pop('hosts')
                ),
                'properties': format_columns.DictColumn(
                    data._info.pop('metadata')
                ),
            },
        )

        info = {}
        info.update(data._info)
        return zip(*sorted(six.iteritems(info)))


class UnsetAggregate(command.Command):
    _description = _("Unset aggregate properties")

    def get_parser(self, prog_name):
        parser = super(UnsetAggregate, self).get_parser(prog_name)
        parser.add_argument(
            "aggregate",
            metavar="<aggregate>",
            help=_("Aggregate to modify (name or ID)")
        )
        parser.add_argument(
            "--property",
            metavar="<key>",
            action='append',
            help=_("Property to remove from aggregate "
                   "(repeat option to remove multiple properties)")
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        aggregate = utils.find_resource(
            compute_client.aggregates,
            parsed_args.aggregate)

        unset_property = {}
        if parsed_args.property:
            unset_property.update({key: None for key in parsed_args.property})
        if unset_property:
            compute_client.aggregates.set_metadata(aggregate,
                                                   unset_property)
