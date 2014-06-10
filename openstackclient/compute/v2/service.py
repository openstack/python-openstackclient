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

"""Service action implementations"""

import logging

from cliff import lister

from openstackclient.common import utils


class ListService(lister.Lister):
    """List service command"""

    log = logging.getLogger(__name__ + ".ListService")

    def get_parser(self, prog_name):
        parser = super(ListService, self).get_parser(prog_name)
        parser.add_argument(
            "--host",
            metavar="<host>",
            help="Name of host")
        parser.add_argument(
            "--service",
            metavar="<service>",
            help="Name of service")
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        compute_client = self.app.client_manager.compute
        columns = (
            "Binary",
            "Host",
            "Zone",
            "Status",
            "State",
            "Updated At"
        )
        data = compute_client.services.list(parsed_args.host,
                                            parsed_args.service)
        return (columns,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class SetService(lister.Lister):
    """Set service command"""

    log = logging.getLogger(__name__ + ".SetService")

    def get_parser(self, prog_name):
        parser = super(SetService, self).get_parser(prog_name)
        parser.add_argument(
            "host",
            metavar="<host>",
            help="Name of host")
        parser.add_argument(
            "service",
            metavar="<service>",
            help="Name of service")
        enabled_group = parser.add_mutually_exclusive_group()
        enabled_group.add_argument(
            "--enable",
            dest="enabled",
            default=True,
            help="Enable a service",
            action="store_true")
        enabled_group.add_argument(
            "--disable",
            dest="enabled",
            help="Disable a service",
            action="store_false")
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        compute_client = self.app.client_manager.compute
        columns = (
            "Host",
            "Service",
            "Disabled"
        )

        if parsed_args.enabled:
            action = compute_client.services.enable
        else:
            action = compute_client.services.disable

        data = action(parsed_args.host, parsed_args.service)
        return (columns,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))
