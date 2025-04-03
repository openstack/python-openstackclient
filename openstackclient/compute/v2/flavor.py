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

from openstack import exceptions as sdk_exceptions
from openstack import utils as sdk_utils
from osc_lib.cli import format_columns
from osc_lib.cli import parseractions
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.common import pagination
from openstackclient.i18n import _
from openstackclient.identity import common as identity_common


LOG = logging.getLogger(__name__)


_formatters = {
    'extra_specs': format_columns.DictColumn,
    'properties': format_columns.DictColumn,
}


def _get_flavor_columns(item):
    # To maintain backwards compatibility we need to rename sdk props to
    # whatever OSC was using before
    column_map = {
        'extra_specs': 'properties',
        'ephemeral': 'OS-FLV-EXT-DATA:ephemeral',
        'is_disabled': 'OS-FLV-DISABLED:disabled',
        'is_public': 'os-flavor-access:is_public',
    }
    hidden_columns = ['links', 'location', 'original_name']
    return utils.get_osc_show_columns_for_sdk_resource(
        item, column_map, hidden_columns
    )


class CreateFlavor(command.ShowOne):
    _description = _("Create new flavor")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "name", metavar="<flavor-name>", help=_("New flavor name")
        )
        parser.add_argument("--id", metavar="<id>", help=_("Unique flavor ID"))
        parser.add_argument(
            "--ram",
            type=int,
            metavar="<size-mb>",
            default=256,
            help=_("Memory size in MB (default 256M)"),
        )
        parser.add_argument(
            "--disk",
            type=int,
            metavar="<size-gb>",
            default=0,
            help=_("Disk size in GB (default 0G)"),
        )
        parser.add_argument(
            "--ephemeral",
            type=int,
            metavar="<size-gb>",
            default=0,
            help=_("Ephemeral disk size in GB (default 0G)"),
        )
        parser.add_argument(
            "--swap",
            type=int,
            metavar="<size-mb>",
            default=0,
            help=_("Additional swap space size in MB (default 0M)"),
        )
        parser.add_argument(
            "--vcpus",
            type=int,
            metavar="<vcpus>",
            default=1,
            help=_("Number of vcpus (default 1)"),
        )
        parser.add_argument(
            "--rxtx-factor",
            type=float,
            metavar="<factor>",
            default=1.0,
            help=_("RX/TX factor (default 1.0)"),
        )
        public_group = parser.add_mutually_exclusive_group()
        public_group.add_argument(
            "--public",
            dest="public",
            action="store_true",
            default=True,
            help=_("Flavor is available to other projects (default)"),
        )
        public_group.add_argument(
            "--private",
            dest="public",
            action="store_false",
            help=_("Flavor is not available to other projects"),
        )
        parser.add_argument(
            "--property",
            metavar="<key=value>",
            action=parseractions.KeyValueAction,
            dest="properties",
            help=_(
                "Property to add for this flavor "
                "(repeat option to set multiple properties)"
            ),
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_(
                "Allow <project> to access private flavor (name or ID) "
                "(Must be used with --private option)"
            ),
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_(
                "Description for the flavor.(Supported by API versions "
                "'2.55' - '2.latest'"
            ),
        )
        identity_common.add_project_domain_option_to_parser(parser)
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        identity_client = self.app.client_manager.identity

        if parsed_args.project and parsed_args.public:
            msg = _("--project is only allowed with --private")
            raise exceptions.CommandError(msg)

        args = {
            'name': parsed_args.name,
            'ram': parsed_args.ram,
            'vcpus': parsed_args.vcpus,
            'disk': parsed_args.disk,
            'id': parsed_args.id,
            'ephemeral': parsed_args.ephemeral,
            'swap': parsed_args.swap,
            'rxtx_factor': parsed_args.rxtx_factor,
            'is_public': parsed_args.public,
        }

        if parsed_args.description:
            if not sdk_utils.supports_microversion(compute_client, '2.55'):
                msg = _(
                    'The --description parameter requires server support for '
                    'API microversion 2.55'
                )
                raise exceptions.CommandError(msg)

            args['description'] = parsed_args.description

        flavor = compute_client.create_flavor(**args)

        if parsed_args.project:
            try:
                project_id = identity_common.find_project(
                    identity_client,
                    parsed_args.project,
                    parsed_args.project_domain,
                ).id
                compute_client.flavor_add_tenant_access(flavor.id, project_id)
            except Exception as e:
                msg = _(
                    "Failed to add project %(project)s access to flavor: %(e)s"
                )
                LOG.error(msg, {'project': parsed_args.project, 'e': e})
        if parsed_args.properties:
            try:
                flavor = compute_client.create_flavor_extra_specs(
                    flavor, parsed_args.properties
                )
            except Exception as e:
                LOG.error(_("Failed to set flavor properties: %s"), e)

        display_columns, columns = _get_flavor_columns(flavor)
        data = utils.get_dict_properties(
            flavor, columns, formatters=_formatters
        )

        return (display_columns, data)


class DeleteFlavor(command.Command):
    _description = _("Delete flavor(s)")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "flavor",
            metavar="<flavor>",
            nargs='+',
            help=_("Flavor(s) to delete (name or ID)"),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        result = 0
        for f in parsed_args.flavor:
            try:
                flavor = compute_client.find_flavor(f, ignore_missing=False)
                compute_client.delete_flavor(flavor.id)
            except Exception as e:
                result += 1
                LOG.error(
                    _(
                        "Failed to delete flavor with name or "
                        "ID '%(flavor)s': %(e)s"
                    ),
                    {'flavor': f, 'e': e},
                )

        if result > 0:
            total = len(parsed_args.flavor)
            msg = _("%(result)s of %(total)s flavors failed to delete.") % {
                'result': result,
                'total': total,
            }
            raise exceptions.CommandError(msg)


class ListFlavor(command.Lister):
    _description = _("List flavors")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        public_group = parser.add_mutually_exclusive_group()
        public_group.add_argument(
            "--public",
            dest="public",
            action="store_true",
            default=True,
            help=_("List only public flavors (default)"),
        )
        public_group.add_argument(
            "--private",
            dest="public",
            action="store_false",
            help=_("List only private flavors"),
        )
        public_group.add_argument(
            "--all",
            dest="all",
            action="store_true",
            default=False,
            help=_("List all flavors, whether public or private"),
        )
        parser.add_argument(
            '--min-disk',
            type=int,
            metavar='<min-disk>',
            help=_('Filters the flavors by a minimum disk space, in GiB.'),
        )
        parser.add_argument(
            '--min-ram',
            type=int,
            metavar='<min-ram>',
            help=_('Filters the flavors by a minimum RAM, in MiB.'),
        )
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_("List additional fields in output"),
        )
        pagination.add_marker_pagination_option_to_parser(parser)
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        # is_public is ternary - None means give all flavors,
        # True is public only and False is private only
        # By default Nova assumes True and gives admins public flavors
        # and flavors from their own projects only.
        is_public = None if parsed_args.all else parsed_args.public

        query_attrs = {'is_public': is_public}

        if parsed_args.marker:
            query_attrs['marker'] = parsed_args.marker

        if parsed_args.limit:
            query_attrs['limit'] = parsed_args.limit

        if parsed_args.limit or parsed_args.marker:
            # User passed explicit pagination request, switch off SDK
            # pagination
            query_attrs['paginated'] = False

        if parsed_args.min_disk:
            query_attrs['min_disk'] = parsed_args.min_disk

        if parsed_args.min_ram:
            query_attrs['min_ram'] = parsed_args.min_ram

        data = list(compute_client.flavors(**query_attrs))
        # Even if server supports 2.61 some policy might stop it sending us
        # extra_specs. So try to fetch them if they are absent
        for f in data:
            if parsed_args.long and not f.extra_specs:
                compute_client.fetch_flavor_extra_specs(f)

        columns: tuple[str, ...] = (
            "id",
            "name",
            "ram",
            "disk",
            "ephemeral",
            "vcpus",
            "is_public",
        )
        if parsed_args.long:
            columns += (
                "swap",
                "rxtx_factor",
                "extra_specs",
            )

        column_headers: tuple[str, ...] = (
            "ID",
            "Name",
            "RAM",
            "Disk",
            "Ephemeral",
            "VCPUs",
            "Is Public",
        )
        if parsed_args.long:
            column_headers += (
                "Swap",
                "RXTX Factor",
                "Properties",
            )

        return (
            column_headers,
            (
                utils.get_item_properties(s, columns, formatters=_formatters)
                for s in data
            ),
        )


class SetFlavor(command.Command):
    _description = _("Set flavor properties")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "flavor",
            metavar="<flavor>",
            help=_("Flavor to modify (name or ID)"),
        )
        parser.add_argument(
            "--no-property",
            action="store_true",
            help=_(
                "Remove all properties from this flavor "
                "(specify both --no-property and --property"
                " to remove the current properties before setting"
                " new properties.)"
            ),
        )
        parser.add_argument(
            "--property",
            metavar="<key=value>",
            action=parseractions.KeyValueAction,
            dest="properties",
            help=_(
                "Property to add or modify for this flavor "
                "(repeat option to set multiple properties)"
            ),
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_('Set flavor access to project (name or ID) (admin only)'),
        )
        identity_common.add_project_domain_option_to_parser(parser)
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_(
                "Set description for the flavor.(Supported by API "
                "versions '2.55' - '2.latest'"
            ),
        )

        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        identity_client = self.app.client_manager.identity

        try:
            flavor = compute_client.find_flavor(
                parsed_args.flavor, get_extra_specs=True, ignore_missing=False
            )
        except sdk_exceptions.ResourceNotFound as e:
            raise exceptions.CommandError(e.message)

        if parsed_args.description:
            if not sdk_utils.supports_microversion(compute_client, '2.55'):
                msg = _(
                    'The --description parameter requires server support for '
                    'API microversion 2.55'
                )
                raise exceptions.CommandError(msg)

            compute_client.update_flavor(
                flavor=flavor.id, description=parsed_args.description
            )

        result = 0
        if parsed_args.no_property:
            try:
                for key in flavor.extra_specs.keys():
                    compute_client.delete_flavor_extra_specs_property(
                        flavor.id, key
                    )
            except Exception as e:
                LOG.error(_("Failed to clear flavor properties: %s"), e)
                result += 1

        if parsed_args.properties:
            try:
                compute_client.create_flavor_extra_specs(
                    flavor.id, parsed_args.properties
                )
            except Exception as e:
                LOG.error(_("Failed to set flavor properties: %s"), e)
                result += 1

        if parsed_args.project:
            try:
                if flavor.is_public:
                    msg = _("Cannot set access for a public flavor")
                    raise exceptions.CommandError(msg)
                else:
                    project_id = identity_common.find_project(
                        identity_client,
                        parsed_args.project,
                        parsed_args.project_domain,
                    ).id
                    compute_client.flavor_add_tenant_access(
                        flavor.id, project_id
                    )
            except Exception as e:
                LOG.error(_("Failed to set flavor access to project: %s"), e)
                result += 1

        if result > 0:
            raise exceptions.CommandError(
                _("Command Failed: One or more of the operations failed")
            )


class ShowFlavor(command.ShowOne):
    _description = _("Display flavor details")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "flavor",
            metavar="<flavor>",
            help=_("Flavor to display (name or ID)"),
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        flavor = compute_client.find_flavor(
            parsed_args.flavor, get_extra_specs=True, ignore_missing=False
        )

        access_projects = None
        # get access projects list of this flavor
        if not flavor.is_public:
            try:
                flavor_access = compute_client.get_flavor_access(
                    flavor=flavor.id
                )
                access_projects = [
                    utils.get_field(access, 'tenant_id')
                    for access in flavor_access
                ]
            except Exception as e:
                msg = _(
                    "Failed to get access projects list "
                    "for flavor '%(flavor)s': %(e)s"
                )
                LOG.error(msg, {'flavor': parsed_args.flavor, 'e': e})

        # Since we need to inject "access_project_id" into resource - convert
        # it to dict and treat it respectively
        flavor = flavor.to_dict()
        flavor['access_project_ids'] = access_projects

        display_columns, columns = _get_flavor_columns(flavor)
        data = utils.get_dict_properties(
            flavor, columns, formatters=_formatters
        )

        return (display_columns, data)


class UnsetFlavor(command.Command):
    _description = _("Unset flavor properties")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "flavor",
            metavar="<flavor>",
            help=_("Flavor to modify (name or ID)"),
        )
        parser.add_argument(
            "--property",
            metavar="<key>",
            action='append',
            dest="properties",
            help=_(
                "Property to remove from flavor "
                "(repeat option to unset multiple properties)"
            ),
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_(
                'Remove flavor access from project (name or ID) (admin only)'
            ),
        )
        identity_common.add_project_domain_option_to_parser(parser)

        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        identity_client = self.app.client_manager.identity

        try:
            flavor = compute_client.find_flavor(
                parsed_args.flavor, get_extra_specs=True, ignore_missing=False
            )
        except sdk_exceptions.ResourceNotFound as e:
            raise exceptions.CommandError(e.message)

        result = 0
        if parsed_args.properties:
            for key in parsed_args.properties:
                try:
                    compute_client.delete_flavor_extra_specs_property(
                        flavor.id, key
                    )
                except sdk_exceptions.SDKException as e:
                    LOG.error(_("Failed to unset flavor property: %s"), e)
                    result += 1

        if parsed_args.project:
            try:
                if flavor.is_public:
                    msg = _("Cannot remove access for a public flavor")
                    raise exceptions.CommandError(msg)

                project_id = identity_common.find_project(
                    identity_client,
                    parsed_args.project,
                    parsed_args.project_domain,
                ).id
                compute_client.flavor_remove_tenant_access(
                    flavor.id, project_id
                )
            except Exception as e:
                LOG.error(
                    _("Failed to remove flavor access from project: %s"), e
                )
                result += 1

        if result > 0:
            raise exceptions.CommandError(
                _("Command Failed: One or more of the operations failed")
            )
