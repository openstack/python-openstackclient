#   Copyright 2013 OpenStack Foundation
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

"""Floating IP action implementations"""

import six

from openstackclient.common import command
from openstackclient.common import utils


class AddFloatingIP(command.Command):
    """Add floating IP address to server"""

    def get_parser(self, prog_name):
        parser = super(AddFloatingIP, self).get_parser(prog_name)
        parser.add_argument(
            "ip_address",
            metavar="<ip-address>",
            help="IP address to add to server (name only)",
        )
        parser.add_argument(
            "server",
            metavar="<server>",
            help="Server to receive the IP address (name or ID)",
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute

        server = utils.find_resource(
            compute_client.servers, parsed_args.server)

        server.add_floating_ip(parsed_args.ip_address)


class CreateFloatingIP(command.ShowOne):
    """Create new floating IP address"""

    def get_parser(self, prog_name):
        parser = super(CreateFloatingIP, self).get_parser(prog_name)
        parser.add_argument(
            'pool',
            metavar='<pool>',
            help='Pool to fetch IP address from (name or ID)',
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        floating_ip = compute_client.floating_ips.create(parsed_args.pool)

        info = {}
        info.update(floating_ip._info)
        return zip(*sorted(six.iteritems(info)))


class RemoveFloatingIP(command.Command):
    """Remove floating IP address from server"""

    def get_parser(self, prog_name):
        parser = super(RemoveFloatingIP, self).get_parser(prog_name)
        parser.add_argument(
            "ip_address",
            metavar="<ip-address>",
            help="IP address to remove from server (name only)",
        )
        parser.add_argument(
            "server",
            metavar="<server>",
            help="Server to remove the IP address from (name or ID)",
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute

        server = utils.find_resource(
            compute_client.servers, parsed_args.server)

        server.remove_floating_ip(parsed_args.ip_address)
