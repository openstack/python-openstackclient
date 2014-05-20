#   Copyright 2013 OpenStack, LLC.
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

"""Host action implementations"""

import logging

from cliff import lister

from openstackclient.common import utils


class ListHost(lister.Lister):
    """List host command"""

    log = logging.getLogger(__name__ + ".ListHost")

    def get_parser(self, prog_name):
        parser = super(ListHost, self).get_parser(prog_name)
        parser.add_argument(
            "--zone",
            metavar="<zone>",
            help="Only return hosts in the availability zone.")
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        compute_client = self.app.client_manager.compute
        columns = (
            "Host Name",
            "Service",
            "Zone"
        )
        data = compute_client.hosts.list_all(parsed_args.zone)
        return (columns,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class ShowHost(lister.Lister):
    """Show host command"""

    log = logging.getLogger(__name__ + ".ShowHost")

    def get_parser(self, prog_name):
        parser = super(ShowHost, self).get_parser(prog_name)
        parser.add_argument(
            "host",
            metavar="<host>",
            help="Name of host")
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        compute_client = self.app.client_manager.compute
        columns = (
            "Host",
            "Project",
            "CPU",
            "Memory MB",
            "Disk GB"
        )
        data = compute_client.hosts.get(parsed_args.host)
        return (columns,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))
