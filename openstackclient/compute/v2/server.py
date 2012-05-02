# Copyright 2012 OpenStack LLC.
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
#
# vim: tabstop=4 shiftwidth=4 softtabstop=4

"""
Server action implementations
"""

import logging
import os

from cliff import lister
from cliff import show

from openstackclient.common import command
from openstackclient.common import utils


def _format_servers_list_networks(server):
    """Return a string containing the networks a server is attached to.

    :param server: a single Server resource
    """
    output = []
    for (network, addresses) in server.networks.items():
        if not addresses:
            continue
        addresses_csv = ', '.join(addresses)
        group = "%s=%s" % (network, addresses_csv)
        output.append(group)
    return '; '.join(output)


def get_server_properties(server, fields, formatters={}):
    """Return a tuple containing the server properties.

    :param server: a single Server resource
    :param fields: tuple of strings with the desired field names
    :param formatters: dictionary mapping field names to callables
       to format the values
    """
    row = []
    mixed_case_fields = ['serverId']

    for field in fields:
        if field in formatters:
            row.append(formatters[field](server))
        else:
            if field in mixed_case_fields:
                field_name = field.replace(' ', '_')
            else:
                field_name = field.lower().replace(' ', '_')
            data = getattr(server, field_name, '')
            row.append(data)
    return tuple(row)


class List_Server(command.OpenStackCommand, lister.Lister):
    "List server command."

    api = 'compute'
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(List_Server, self).get_parser(prog_name)
        parser.add_argument(
            '--reservation-id',
            help='only return instances that match the reservation',
            )
        parser.add_argument(
            '--ip',
            help='regular expression to match IP address',
            )
        parser.add_argument(
            '--ip6',
            help='regular expression to match IPv6 address',
            )
        parser.add_argument(
            '--name',
            help='regular expression to match name',
            )
        parser.add_argument(
            '--instance-name',
            help='regular expression to match instance name',
            )
        parser.add_argument(
            '--status',
            help='search by server status',
            # FIXME(dhellmann): Add choices?
            )
        parser.add_argument(
            '--flavor',
            help='search by flavor ID',
            )
        parser.add_argument(
            '--image',
            help='search by image ID',
            )
        parser.add_argument(
            '--host',
            metavar='HOSTNAME',
            help='search by hostname',
            )
        parser.add_argument(
            '--all-tenants',
            action='store_true',
            default=bool(int(os.environ.get("ALL_TENANTS", 0))),
            help='display information from all tenants (admin only)',
            )
        return parser

    def get_data(self, parsed_args):
        self.log.debug('v2.List_Server.run(%s)' % parsed_args)
        nova_client = self.app.client_manager.compute
        search_opts = {
            'all_tenants': parsed_args.all_tenants,
            'reservation_id': parsed_args.reservation_id,
            'ip': parsed_args.ip,
            'ip6': parsed_args.ip6,
            'name': parsed_args.name,
            'image': parsed_args.image,
            'flavor': parsed_args.flavor,
            'status': parsed_args.status,
            'host': parsed_args.host,
            'instance_name': parsed_args.instance_name,
            }
        self.log.debug('search options: %s', search_opts)
        # FIXME(dhellmann): Consider adding other columns
        columns = ('ID', 'Name', 'Status', 'Networks')
        data = nova_client.servers.list(search_opts=search_opts)
        return (columns,
                (get_server_properties(
                    s, columns,
                    formatters={'Networks': _format_servers_list_networks},
                    ) for s in data),
                )


class Show_Server(command.OpenStackCommand, show.ShowOne):
    "Show server command."

    api = 'compute'
    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Show_Server, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help='Name or ID of server to display')
        return parser

    def get_data(self, parsed_args):
        self.log.debug('v2.Show_Server.run(%s)' % parsed_args)
        nova_client = self.app.client_manager.compute
        server = utils.find_resource(nova_client.servers, parsed_args.server)

        info = {}
        info.update(server._info)

        # Convert the flavor blob to a name
        flavor_info = info.get('flavor', {})
        flavor_id = flavor_info.get('id', '')
        flavor = utils.find_resource(nova_client.flavors, flavor_id)
        info['flavor'] = flavor.name

        # Convert the image blob to a name
        image_info = info.get('image', {})
        image_id = image_info.get('id', '')
        image = utils.find_resource(nova_client.images, image_id)
        info['image'] = image.name

        # Format addresses in a useful way
        info['addresses'] = _format_servers_list_networks(server)

        # Remove a couple of values that are long and not too useful
        info.pop('links', None)

        columns = sorted(info.keys())
        values = [info[c] for c in columns]
        return (columns, values)
