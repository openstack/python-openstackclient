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

import logging

from osc_lib.command import command
from osc_lib import utils

from openstackclient.i18n import _


class AddFloatingIP(command.Command):
    """Add floating IP address to server"""

    # TODO(tangchen): Remove this class and ``ip floating add`` command
    #                 two cycles after Mitaka.

    # This notifies cliff to not display the help for this command
    deprecated = True

    log = logging.getLogger('deprecated')

    def get_parser(self, prog_name):
        parser = super(AddFloatingIP, self).get_parser(prog_name)
        parser.add_argument(
            "ip_address",
            metavar="<ip-address>",
            help=_("IP address to add to server (name only)"),
        )
        parser.add_argument(
            "server",
            metavar="<server>",
            help=_("Server to receive the IP address (name or ID)"),
        )
        return parser

    def take_action(self, parsed_args):
        self.log.warning(_('This command has been deprecated. '
                           'Please use "server add floating ip" instead.'))

        compute_client = self.app.client_manager.compute

        server = utils.find_resource(
            compute_client.servers, parsed_args.server)

        server.add_floating_ip(parsed_args.ip_address)


class RemoveFloatingIP(command.Command):
    """Remove floating IP address from server"""

    # TODO(tangchen): Remove this class and ``ip floating remove`` command
    #                 two cycles after Mitaka.

    # This notifies cliff to not display the help for this command
    deprecated = True

    log = logging.getLogger('deprecated')

    def get_parser(self, prog_name):
        parser = super(RemoveFloatingIP, self).get_parser(prog_name)
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
                           'Please use "server remove floating ip" instead.'))

        compute_client = self.app.client_manager.compute

        server = utils.find_resource(
            compute_client.servers, parsed_args.server)

        server.remove_floating_ip(parsed_args.ip_address)
