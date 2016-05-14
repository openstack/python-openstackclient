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

import six

from openstackclient.common import command
from openstackclient.common import exceptions
from openstackclient.common import parseractions
from openstackclient.common import utils
from openstackclient.i18n import _


def _find_flavor(compute_client, flavor):
    try:
        return compute_client.flavors.get(flavor)
    except Exception as ex:
        if type(ex).__name__ == 'NotFound':
            pass
        else:
            raise
    try:
        return compute_client.flavors.find(name=flavor, is_public=None)
    except Exception as ex:
        if type(ex).__name__ == 'NotFound':
            msg = _("No flavor with a name or ID of '%s' exists.") % flavor
            raise exceptions.CommandError(msg)
        else:
            raise


class CreateFlavor(command.ShowOne):
    """Create new flavor"""

    def get_parser(self, prog_name):
        parser = super(CreateFlavor, self).get_parser(prog_name)
        parser.add_argument(
            "name",
            metavar="<flavor-name>",
            help=_("New flavor name")
        )
        parser.add_argument(
            "--id",
            metavar="<id>",
            default='auto',
            help=_("Unique flavor ID; 'auto' creates a UUID "
                   "(default: auto)")
        )
        parser.add_argument(
            "--ram",
            type=int,
            metavar="<size-mb>",
            default=256,
            help=_("Memory size in MB (default 256M)")
        )
        parser.add_argument(
            "--disk",
            type=int,
            metavar="<size-gb>",
            default=0,
            help=_("Disk size in GB (default 0G)")
        )
        parser.add_argument(
            "--ephemeral",
            type=int,
            metavar="<size-gb>",
            default=0,
            help=_("Ephemeral disk size in GB (default 0G)")
        )
        parser.add_argument(
            "--swap",
            type=int,
            metavar="<size-gb>",
            default=0,
            help=_("Swap space size in GB (default 0G)")
        )
        parser.add_argument(
            "--vcpus",
            type=int,
            metavar="<vcpus>",
            default=1,
            help=_("Number of vcpus (default 1)")
        )
        parser.add_argument(
            "--rxtx-factor",
            type=float,
            metavar="<factor>",
            default=1.0,
            help=_("RX/TX factor (default 1.0)")
        )
        public_group = parser.add_mutually_exclusive_group()
        public_group.add_argument(
            "--public",
            dest="public",
            action="store_true",
            default=True,
            help=_("Flavor is available to other projects (default)")
        )
        public_group.add_argument(
            "--private",
            dest="public",
            action="store_false",
            help=_("Flavor is not available to other projects")
        )
        return parser

    def take_action(self, parsed_args):
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
    """Delete flavor"""

    def get_parser(self, prog_name):
        parser = super(DeleteFlavor, self).get_parser(prog_name)
        parser.add_argument(
            "flavor",
            metavar="<flavor>",
            help=_("Flavor to delete (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        flavor = _find_flavor(compute_client, parsed_args.flavor)
        compute_client.flavors.delete(flavor.id)


class ListFlavor(command.Lister):
    """List flavors"""

    def get_parser(self, prog_name):
        parser = super(ListFlavor, self).get_parser(prog_name)
        public_group = parser.add_mutually_exclusive_group()
        public_group.add_argument(
            "--public",
            dest="public",
            action="store_true",
            default=True,
            help=_("List only public flavors (default)")
        )
        public_group.add_argument(
            "--private",
            dest="public",
            action="store_false",
            help=_("List only private flavors")
        )
        public_group.add_argument(
            "--all",
            dest="all",
            action="store_true",
            default=False,
            help=_("List all flavors, whether public or private")
        )
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_("List additional fields in output")
        )
        parser.add_argument(
            '--marker',
            metavar="<marker>",
            help=_("The last flavor ID of the previous page")
        )
        parser.add_argument(
            '--limit',
            type=int,
            metavar="<limit>",
            help=_("Maximum number of flavors to display")
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        columns = (
            "ID",
            "Name",
            "RAM",
            "Disk",
            "Ephemeral",
            "VCPUs",
            "Is Public",
        )

        # is_public is ternary - None means give all flavors,
        # True is public only and False is private only
        # By default Nova assumes True and gives admins public flavors
        # and flavors from their own projects only.
        is_public = None if parsed_args.all else parsed_args.public

        data = compute_client.flavors.list(is_public=is_public,
                                           marker=parsed_args.marker,
                                           limit=parsed_args.limit)

        if parsed_args.long:
            columns = columns + (
                "Swap",
                "RXTX Factor",
                "Properties",
            )
            for f in data:
                f.properties = f.get_keys()

        column_headers = columns

        return (column_headers,
                (utils.get_item_properties(
                    s, columns, formatters={'Properties': utils.format_dict},
                ) for s in data))


class SetFlavor(command.Command):
    """Set flavor properties"""

    def get_parser(self, prog_name):
        parser = super(SetFlavor, self).get_parser(prog_name)
        parser.add_argument(
            "--property",
            metavar="<key=value>",
            action=parseractions.KeyValueAction,
            help=_("Property to add or modify for this flavor "
                   "(repeat option to set multiple properties)")
        )
        parser.add_argument(
            "flavor",
            metavar="<flavor>",
            help=_("Flavor to modify (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        flavor = _find_flavor(compute_client, parsed_args.flavor)
        flavor.set_keys(parsed_args.property)


class ShowFlavor(command.ShowOne):
    """Display flavor details"""

    def get_parser(self, prog_name):
        parser = super(ShowFlavor, self).get_parser(prog_name)
        parser.add_argument(
            "flavor",
            metavar="<flavor>",
            help=_("Flavor to display (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        resource_flavor = _find_flavor(compute_client, parsed_args.flavor)
        flavor = resource_flavor._info.copy()
        flavor.pop("links", None)

        flavor['properties'] = utils.format_dict(resource_flavor.get_keys())

        return zip(*sorted(six.iteritems(flavor)))


class UnsetFlavor(command.Command):
    """Unset flavor properties"""

    def get_parser(self, prog_name):
        parser = super(UnsetFlavor, self).get_parser(prog_name)
        parser.add_argument(
            "--property",
            metavar="<key>",
            action='append',
            required=True,
            help=_("Property to remove from flavor "
                   "(repeat option to unset multiple properties)")
        )
        parser.add_argument(
            "flavor",
            metavar="<flavor>",
            help=_("Flavor to modify (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        flavor = _find_flavor(compute_client, parsed_args.flavor)
        flavor.unset_keys(parsed_args.property)
