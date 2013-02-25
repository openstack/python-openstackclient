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

"""Flavor action implementations"""

import logging

from cliff import command
from cliff import lister
from cliff import show

from novaclient.v1_1 import flavors
from openstackclient.common import utils


class CreateFlavor(show.ShowOne):
    """Create flavor command"""

    api = "compute"
    log = logging.getLogger(__name__ + ".CreateFlavor")

    def get_parser(self, prog_name):
        parser = super(CreateFlavor, self).get_parser(prog_name)
        parser.add_argument(
            "name",
            metavar="<name>",
            help="Name of the new flavor")
        parser.add_argument(
            "id",
            metavar="<id>",
            help="Unique ID (integer or UUID) for the new flavor."
                 " If specifying 'auto', a UUID will be generated as id")
        parser.add_argument(
            "ram",
            type=int,
            metavar="<ram>",
            help="Memory size in MB")
        parser.add_argument(
            "disk",
            type=int,
            metavar="<disk>",
            help="Disk size in GB")
        parser.add_argument(
            "--ephemeral",
            type=int,
            metavar="<ephemeral>",
            help="Ephemeral space size in GB (default 0)",
            default=0)
        parser.add_argument(
            "vcpus",
            type=int,
            metavar="<vcpus>",
            help="Number of vcpus")
        parser.add_argument(
            "--swap",
            type=int,
            metavar="<swap>",
            help="Swap space size in MB (default 0)",
            default=0)
        parser.add_argument(
            "--rxtx-factor",
            type=int,
            metavar="<factor>",
            help="RX/TX factor (default 1)",
            default=1)
        public_group = parser.add_mutually_exclusive_group()
        public_group.add_argument(
            "--public",
            dest="public",
            default=True,
            help="Make flavor inaccessible to the public (default)",
            action="store_true")
        public_group.add_argument(
            "--private",
            dest="public",
            help="Make flavor inaccessible to the public",
            action="store_false")
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)" % parsed_args)
        compute_client = self.app.client_manager.compute

        args = (
            parsed_args.name,
            parsed_args.ram,
            parsed_args.vcpus,
            parsed_args.disk,
            parsed_args.id,
            parsed_args.ephemeral,
            parsed_args.swap,
            parsed_args.rxtx_factor,
            parsed_args.public
        )

        flavor = compute_client.flavors.create(*args)._info.copy()
        flavor.pop("links")

        return zip(*sorted(flavor.iteritems()))


class DeleteFlavor(command.Command):
    """Delete flavor command"""

    api = "compute"
    log = logging.getLogger(__name__ + ".DeleteFlavor")

    def get_parser(self, prog_name):
        parser = super(DeleteFlavor, self).get_parser(prog_name)
        parser.add_argument(
            "flavor",
            metavar="<flavor>",
            help="Name or ID of flavor to delete")
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)" % parsed_args)
        compute_client = self.app.client_manager.compute
        flavor = utils.find_resource(compute_client.flavors,
                                     parsed_args.flavor)
        compute_client.flavors.delete(flavor.id)
        return


class ListFlavor(lister.Lister):
    """List flavor command"""

    api = "compute"
    log = logging.getLogger(__name__ + ".ListFlavor")

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)" % parsed_args)
        compute_client = self.app.client_manager.compute
        columns = (
            "ID",
            "Name",
            "RAM",
            "Disk",
            "Ephemeral",
            "Swap",
            "VCPUs",
            "RXTX Factor",
            "Is Public",
            "Extra Specs"
        )
        data = compute_client.flavors.list()
        return (columns,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class ShowFlavor(show.ShowOne):
    """Show flavor command"""

    api = "compute"
    log = logging.getLogger(__name__ + ".ShowFlavor")

    def get_parser(self, prog_name):
        parser = super(ShowFlavor, self).get_parser(prog_name)
        parser.add_argument(
            "flavor",
            metavar="<flavor>",
            help="Name or ID of flavor to display")
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)" % parsed_args)
        compute_client = self.app.client_manager.compute
        flavor = utils.find_resource(compute_client.flavors,
                                     parsed_args.flavor)._info.copy()
        flavor.pop("links")

        return zip(*sorted(flavor.iteritems()))
