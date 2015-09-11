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
import six

from cliff import command
from cliff import lister
from cliff import show

from openstackclient.common import parseractions
from openstackclient.common import utils


class AddAggregateHost(show.ShowOne):
    """Add host to aggregate"""

    log = logging.getLogger(__name__ + '.AddAggregateHost')

    def get_parser(self, prog_name):
        parser = super(AddAggregateHost, self).get_parser(prog_name)
        parser.add_argument(
            'aggregate',
            metavar='<aggregate>',
            help='Aggregate (name or ID)',
        )
        parser.add_argument(
            'host',
            metavar='<host>',
            help='Host to add to <aggregate>',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        compute_client = self.app.client_manager.compute

        aggregate = utils.find_resource(
            compute_client.aggregates,
            parsed_args.aggregate,
        )
        data = compute_client.aggregates.add_host(aggregate, parsed_args.host)

        info = {}
        info.update(data._info)
        return zip(*sorted(six.iteritems(info)))


class CreateAggregate(show.ShowOne):
    """Create a new aggregate"""

    log = logging.getLogger(__name__ + ".CreateAggregate")

    def get_parser(self, prog_name):
        parser = super(CreateAggregate, self).get_parser(prog_name)
        parser.add_argument(
            "name",
            metavar="<name>",
            help="New aggregate name",
        )
        parser.add_argument(
            "--zone",
            metavar="<availability-zone>",
            help="Availability zone name",
        )
        parser.add_argument(
            "--property",
            metavar="<key=value>",
            action=parseractions.KeyValueAction,
            help='Property to add to this aggregate '
                 '(repeat option to set multiple properties)',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

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

        return zip(*sorted(six.iteritems(info)))


class DeleteAggregate(command.Command):
    """Delete an existing aggregate"""

    log = logging.getLogger(__name__ + '.DeleteAggregate')

    def get_parser(self, prog_name):
        parser = super(DeleteAggregate, self).get_parser(prog_name)
        parser.add_argument(
            'aggregate',
            metavar='<aggregate>',
            help='Aggregate to delete (name or ID)',
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):

        compute_client = self.app.client_manager.compute
        data = utils.find_resource(
            compute_client.aggregates,
            parsed_args.aggregate,
        )
        compute_client.aggregates.delete(data.id)
        return


class ListAggregate(lister.Lister):
    """List all aggregates"""

    log = logging.getLogger(__name__ + ".ListAggregate")

    def get_parser(self, prog_name):
        parser = super(ListAggregate, self).get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help='List additional fields in output')
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

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
                ) for s in data))


class RemoveAggregateHost(show.ShowOne):
    """Remove host from aggregate"""

    log = logging.getLogger(__name__ + '.RemoveAggregateHost')

    def get_parser(self, prog_name):
        parser = super(RemoveAggregateHost, self).get_parser(prog_name)
        parser.add_argument(
            'aggregate',
            metavar='<aggregate>',
            help='Aggregate (name or ID)',
        )
        parser.add_argument(
            'host',
            metavar='<host>',
            help='Host to remove from <aggregate>',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

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
        return zip(*sorted(six.iteritems(info)))


class SetAggregate(show.ShowOne):
    """Set aggregate properties"""

    log = logging.getLogger(__name__ + '.SetAggregate')

    def get_parser(self, prog_name):
        parser = super(SetAggregate, self).get_parser(prog_name)
        parser.add_argument(
            'aggregate',
            metavar='<aggregate>',
            help='Aggregate to modify (name or ID)',
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            help='Set aggregate name',
        )
        parser.add_argument(
            "--zone",
            metavar="<availability-zone>",
            help="Set availability zone name",
        )
        parser.add_argument(
            "--property",
            metavar="<key=value>",
            action=parseractions.KeyValueAction,
            help='Property to set on <aggregate> '
                 '(repeat option to set multiple properties)',
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):

        compute_client = self.app.client_manager.compute
        aggregate = utils.find_resource(
            compute_client.aggregates,
            parsed_args.aggregate,
        )

        info = {}
        kwargs = {}
        if parsed_args.name:
            kwargs['name'] = parsed_args.name
        if parsed_args.zone:
            kwargs['availability_zone'] = parsed_args.zone
        if kwargs:
            info.update(compute_client.aggregates.update(
                aggregate,
                kwargs
            )._info)

        if parsed_args.property:
            info.update(compute_client.aggregates.set_metadata(
                aggregate,
                parsed_args.property,
            )._info)

        if info:
            return zip(*sorted(six.iteritems(info)))
        else:
            return ({}, {})


class ShowAggregate(show.ShowOne):
    """Display aggregate details"""

    log = logging.getLogger(__name__ + '.ShowAggregate')

    def get_parser(self, prog_name):
        parser = super(ShowAggregate, self).get_parser(prog_name)
        parser.add_argument(
            'aggregate',
            metavar='<aggregate>',
            help='Aggregate to display (name or ID)',
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):

        compute_client = self.app.client_manager.compute
        data = utils.find_resource(
            compute_client.aggregates,
            parsed_args.aggregate,
        )
        # Remove availability_zone from metadata because Nova doesn't
        if 'availability_zone' in data.metadata:
            data.metadata.pop('availability_zone')
        # Map 'metadata' column to 'properties'
        data._info.update({'properties': data._info.pop('metadata')})

        info = {}
        info.update(data._info)
        return zip(*sorted(six.iteritems(info)))
