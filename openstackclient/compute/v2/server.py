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

from cliff import command
from cliff import lister
from cliff import show

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


class ListServer(lister.Lister):
    """List server command"""

    api = 'compute'
    log = logging.getLogger(__name__ + '.ListServer')

    def get_parser(self, prog_name):
        parser = super(ListServer, self).get_parser(prog_name)
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

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
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
                (utils.get_item_properties(
                    s, columns,
                    formatters={'Networks': _format_servers_list_networks},
                    ) for s in data),
                )


class ShowServer(show.ShowOne):
    """Show server command"""

    api = 'compute'
    log = logging.getLogger(__name__ + '.ShowServer')

    def get_parser(self, prog_name):
        parser = super(ShowServer, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help='Name or ID of server to display')
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
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
        return zip(*sorted(info.iteritems()))
