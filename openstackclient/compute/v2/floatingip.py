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
import six

from cliff import command
from cliff import lister
from cliff import show

from openstackclient.common import utils


class AddFloatingIP(command.Command):
    """Add floating-ip to server"""

    log = logging.getLogger(__name__ + ".AddFloatingIP")

    def get_parser(self, prog_name):
        parser = super(AddFloatingIP, self).get_parser(prog_name)
        parser.add_argument(
            "ip_address",
            metavar="<ip-address>",
            help="IP address to add to server",
        )
        parser.add_argument(
            "server",
            metavar="<server>",
            help="Server to receive the IP address (name or ID)",
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        compute_client = self.app.client_manager.compute

        server = utils.find_resource(
            compute_client.servers, parsed_args.server)

        server.add_floating_ip(parsed_args.ip_address)
        return


class CreateFloatingIP(show.ShowOne):
    """Create new floating-ip"""

    log = logging.getLogger(__name__ + '.CreateFloatingIP')

    def get_parser(self, prog_name):
        parser = super(CreateFloatingIP, self).get_parser(prog_name)
        parser.add_argument(
            'pool',
            metavar='<pool>',
            help='Pool to fetch floating IP from',
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        floating_ip = compute_client.floating_ips.create(parsed_args.pool)

        info = {}
        info.update(floating_ip._info)
        return zip(*sorted(six.iteritems(info)))


class DeleteFloatingIP(command.Command):
    """Delete a floating-ip"""

    log = logging.getLogger(__name__ + '.DeleteFloatingIP')

    def get_parser(self, prog_name):
        parser = super(DeleteFloatingIP, self).get_parser(prog_name)
        parser.add_argument(
            "ip_address",
            metavar="<ip-address>",
            help="IP address to delete",
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute

        floating_ip = utils.find_resource(
            compute_client.floating_ips,
            parsed_args.ip_address,
        )

        compute_client.floating_ips.delete(floating_ip)
        return


class ListFloatingIP(lister.Lister):
    """List floating-ips"""

    log = logging.getLogger(__name__ + '.ListFloatingIP')

    @utils.log_method(log)
    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute

        columns = ('ID', 'Pool', 'IP', 'Fixed IP', 'Instance ID')

        data = compute_client.floating_ips.list()

        return (columns,
                (utils.get_item_properties(
                    s, columns,
                    formatters={},
                ) for s in data))


class RemoveFloatingIP(command.Command):
    """Remove floating-ip from server"""

    log = logging.getLogger(__name__ + ".RemoveFloatingIP")

    def get_parser(self, prog_name):
        parser = super(RemoveFloatingIP, self).get_parser(prog_name)
        parser.add_argument(
            "ip_address",
            metavar="<ip-address>",
            help="IP address to remove from server",
        )
        parser.add_argument(
            "server",
            metavar="<server>",
            help="Server to remove the IP address from (name or ID)",
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        compute_client = self.app.client_manager.compute

        server = utils.find_resource(
            compute_client.servers, parsed_args.server)

        server.remove_floating_ip(parsed_args.ip_address)
        return
