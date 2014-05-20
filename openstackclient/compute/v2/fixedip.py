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

"""Fixed IP action implementations"""

import logging

from cliff import command

from openstackclient.common import utils


class AddFixedIP(command.Command):
    """Add fixed-ip command"""

    log = logging.getLogger(__name__ + ".AddFixedIP")

    def get_parser(self, prog_name):
        parser = super(AddFixedIP, self).get_parser(prog_name)
        parser.add_argument(
            "network",
            metavar="<network>",
            help="Name of the network to fetch an IP address from",
        )
        parser.add_argument(
            "server",
            metavar="<server>",
            help="Name of the server to receive the IP address",
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        compute_client = self.app.client_manager.compute

        network = utils.find_resource(
            compute_client.networks, parsed_args.network)

        server = utils.find_resource(
            compute_client.servers, parsed_args.server)

        server.add_fixed_ip(network.id)
        return


class RemoveFixedIP(command.Command):
    """Remove fixed-ip command"""

    log = logging.getLogger(__name__ + ".RemoveFixedIP")

    def get_parser(self, prog_name):
        parser = super(RemoveFixedIP, self).get_parser(prog_name)
        parser.add_argument(
            "ip_address",
            metavar="<ip-address>",
            help="IP address to remove from server",
        )
        parser.add_argument(
            "server",
            metavar="<server>",
            help="Name of the server to remove the IP address from",
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        compute_client = self.app.client_manager.compute

        server = utils.find_resource(
            compute_client.servers, parsed_args.server)

        server.remove_fixed_ip(parsed_args.ip_address)
        return
