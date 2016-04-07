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

from osc_lib.command import command
from osc_lib import utils

from openstackclient.i18n import _


class AddFixedIP(command.Command):
    """Add fixed IP address to server"""

    # TODO(tangchen): Remove this class and ``ip fixed add`` command
    #                 two cycles after Mitaka.

    # This notifies cliff to not display the help for this command
    deprecated = True

    log = logging.getLogger('deprecated')

    def get_parser(self, prog_name):
        parser = super(AddFixedIP, self).get_parser(prog_name)
        parser.add_argument(
            "network",
            metavar="<network>",
            help=_("Network to fetch an IP address from (name or ID)"),
        )
        parser.add_argument(
            "server",
            metavar="<server>",
            help=_("Server to receive the IP address (name or ID)"),
        )
        return parser

    def take_action(self, parsed_args):
        self.log.warning(_('This command has been deprecated. '
                           'Please use "server add fixed ip" instead.'))

        compute_client = self.app.client_manager.compute

        network = utils.find_resource(
            compute_client.networks, parsed_args.network)

        server = utils.find_resource(
            compute_client.servers, parsed_args.server)

        server.add_fixed_ip(network.id)


class RemoveFixedIP(command.Command):
    """Remove fixed IP address from server"""

    # TODO(tangchen): Remove this class and ``ip fixed remove`` command
    #                 two cycles after Mitaka.

    # This notifies cliff to not display the help for this command
    deprecated = True

    log = logging.getLogger('deprecated')

    def get_parser(self, prog_name):
        parser = super(RemoveFixedIP, self).get_parser(prog_name)
        parser.add_argument(
            "ip_address",
            metavar="<ip-address>",
            help=_("IP address to remove from server (name only)"),
        )
        parser.add_argument(
            "server",
            metavar="<server>",
            help=_("Server to remove the IP address from (name or ID)"),
        )
        return parser

    def take_action(self, parsed_args):
        self.log.warning(_('This command has been deprecated. '
                           'Please use "server remove fixed ip" instead.'))

        compute_client = self.app.client_manager.compute

        server = utils.find_resource(
            compute_client.servers, parsed_args.server)

        server.remove_fixed_ip(parsed_args.ip_address)
