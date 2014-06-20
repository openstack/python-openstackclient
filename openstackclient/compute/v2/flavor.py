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

"""Flavor action implementations"""

import logging
import six

from cliff import command
from cliff import lister
from cliff import show

from openstackclient.common import utils


class CreateFlavor(show.ShowOne):
    """Create new flavor"""

    log = logging.getLogger(__name__ + ".CreateFlavor")

    def get_parser(self, prog_name):
        parser = super(CreateFlavor, self).get_parser(prog_name)
        parser.add_argument(
            "name",
            metavar="<name>",
            help="New flavor name",
        )
        parser.add_argument(
            "--id",
            metavar="<id>",
            default='auto',
            help="Unique flavor ID; 'auto' will create a UUID "
                 "(default: auto)")
        parser.add_argument(
            "--ram",
            type=int,
            metavar="<size-mb>",
            default=256,
            help="Memory size in MB (default 256M)")
        parser.add_argument(
            "--disk",
            type=int,
            metavar="<size-gb>",
            default=0,
            help="Disk size in GB (default 0G)")
        parser.add_argument(
            "--ephemeral",
            type=int,
            metavar="<size-gb>",
            help="Ephemeral disk size in GB (default 0G)",
            default=0)
        parser.add_argument(
            "--swap",
            type=int,
            metavar="<size-gb>",
            help="Swap space size in GB (default 0G)",
            default=0)
        parser.add_argument(
            "--vcpus",
            type=int,
            metavar="<vcpus>",
            default=1,
            help="Number of vcpus (default 1)")
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
            action="store_true",
            default=True,
            help="Flavor is accessible to other projects (default)",
        )
        public_group.add_argument(
            "--private",
            dest="public",
            action="store_false",
            help="Flavor is inaccessible to other projects",
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
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

        return zip(*sorted(six.iteritems(flavor)))


class DeleteFlavor(command.Command):
    """Delete a flavor"""

    log = logging.getLogger(__name__ + ".DeleteFlavor")

    def get_parser(self, prog_name):
        parser = super(DeleteFlavor, self).get_parser(prog_name)
        parser.add_argument(
            "flavor",
            metavar="<flavor>",
            help="Flavor to delete (name or ID)",
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        compute_client = self.app.client_manager.compute
        flavor = utils.find_resource(compute_client.flavors,
                                     parsed_args.flavor)
        compute_client.flavors.delete(flavor.id)
        return


class ListFlavor(lister.Lister):
    """List flavors"""

    log = logging.getLogger(__name__ + ".ListFlavor")

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
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
    """Show flavor details"""

    log = logging.getLogger(__name__ + ".ShowFlavor")

    def get_parser(self, prog_name):
        parser = super(ShowFlavor, self).get_parser(prog_name)
        parser.add_argument(
            "flavor",
            metavar="<flavor>",
            help="Flavor to display (name or ID)",
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        compute_client = self.app.client_manager.compute
        flavor = utils.find_resource(compute_client.flavors,
                                     parsed_args.flavor)._info.copy()
        flavor.pop("links")

        return zip(*sorted(six.iteritems(flavor)))
