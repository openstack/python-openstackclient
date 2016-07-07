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

from osc_lib.cli import parseractions
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils
import six

from openstackclient.i18n import _
from openstackclient.identity import common as identity_common


LOG = logging.getLogger(__name__)


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
        parser.add_argument(
            "--property",
            metavar="<key=value>",
            action=parseractions.KeyValueAction,
            help=_("Property to add for this flavor "
                   "(repeat option to set multiple properties)")
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_("Allow <project> to access private flavor (name or ID) "
                   "(Must be used with --private option)"),
        )
        identity_common.add_project_domain_option_to_parser(parser)
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        identity_client = self.app.client_manager.identity

        if parsed_args.project and parsed_args.public:
            msg = _("--project is only allowed with --private")
            raise exceptions.CommandError(msg)

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

        flavor = compute_client.flavors.create(*args)

        if parsed_args.project:
            try:
                project_id = identity_common.find_project(
                    identity_client,
                    parsed_args.project,
                    parsed_args.project_domain,
                ).id
                compute_client.flavor_access.add_tenant_access(
                    parsed_args.id, project_id)
            except Exception as e:
                msg = _("Failed to add project %(project)s access to "
                        "flavor: %(e)s")
                LOG.error(msg % {'project': parsed_args.project, 'e': e})
        if parsed_args.property:
            try:
                flavor.set_keys(parsed_args.property)
            except Exception as e:
                LOG.error(_("Failed to set flavor property: %s"), e)

        flavor_info = flavor._info.copy()
        flavor_info.pop("links")
        flavor_info['properties'] = utils.format_dict(flavor.get_keys())

        return zip(*sorted(six.iteritems(flavor_info)))


class DeleteFlavor(command.Command):
    """Delete flavor(s)"""

    def get_parser(self, prog_name):
        parser = super(DeleteFlavor, self).get_parser(prog_name)
        parser.add_argument(
            "flavor",
            metavar="<flavor>",
            nargs='+',
            help=_("Flavor(s) to delete (name or ID)")
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        result = 0
        for f in parsed_args.flavor:
            try:
                flavor = _find_flavor(compute_client, f)
                compute_client.flavors.delete(flavor.id)
            except Exception as e:
                result += 1
                LOG.error(_("Failed to delete flavor with name or "
                          "ID '%(flavor)s': %(e)s")
                          % {'flavor': f, 'e': e})

        if result > 0:
            total = len(parsed_args.flavor)
            msg = (_("%(result)s of %(total)s flavors failed "
                   "to delete.") % {'result': result, 'total': total})
            raise exceptions.CommandError(msg)


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
            "flavor",
            metavar="<flavor>",
            help=_("Flavor to modify (name or ID)")
        )
        parser.add_argument(
            "--property",
            metavar="<key=value>",
            action=parseractions.KeyValueAction,
            help=_("Property to add or modify for this flavor "
                   "(repeat option to set multiple properties)")
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_('Set flavor access to project (name or ID) '
                   '(admin only)'),
        )
        identity_common.add_project_domain_option_to_parser(parser)

        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        identity_client = self.app.client_manager.identity

        flavor = _find_flavor(compute_client, parsed_args.flavor)

        result = 0
        if parsed_args.property:
            try:
                flavor.set_keys(parsed_args.property)
            except Exception as e:
                LOG.error(_("Failed to set flavor property: %s"), e)
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
                    compute_client.flavor_access.add_tenant_access(
                        flavor.id, project_id)
            except Exception as e:
                LOG.error(_("Failed to set flavor access to project: %s"), e)
                result += 1

        if result > 0:
            raise exceptions.CommandError(_("Command Failed: One or more of"
                                            " the operations failed"))


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

        access_projects = None
        # get access projects list of this flavor
        if not resource_flavor.is_public:
            try:
                flavor_access = compute_client.flavor_access.list(
                    flavor=resource_flavor.id)
                projects = [utils.get_field(access, 'tenant_id')
                            for access in flavor_access]
                # TODO(Huanxuan Ao): This format case can be removed after
                # patch https://review.openstack.org/#/c/330223/ merged.
                access_projects = utils.format_list(projects)
            except Exception as e:
                msg = _("Failed to get access projects list "
                        "for flavor '%(flavor)s': %(e)s")
                LOG.error(msg % {'flavor': parsed_args.flavor, 'e': e})

        flavor = resource_flavor._info.copy()
        flavor.update({
            'access_project_ids': access_projects
        })
        flavor.pop("links", None)

        flavor['properties'] = utils.format_dict(resource_flavor.get_keys())

        return zip(*sorted(six.iteritems(flavor)))


class UnsetFlavor(command.Command):
    """Unset flavor properties"""

    def get_parser(self, prog_name):
        parser = super(UnsetFlavor, self).get_parser(prog_name)
        parser.add_argument(
            "flavor",
            metavar="<flavor>",
            help=_("Flavor to modify (name or ID)")
        )
        parser.add_argument(
            "--property",
            metavar="<key>",
            action='append',
            help=_("Property to remove from flavor "
                   "(repeat option to unset multiple properties)")
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_('Remove flavor access from project (name or ID) '
                   '(admin only)'),
        )
        identity_common.add_project_domain_option_to_parser(parser)

        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        identity_client = self.app.client_manager.identity

        flavor = _find_flavor(compute_client, parsed_args.flavor)

        result = 0
        if parsed_args.property:
            try:
                flavor.unset_keys(parsed_args.property)
            except Exception as e:
                LOG.error(_("Failed to unset flavor property: %s"), e)
                result += 1

        if parsed_args.project:
            try:
                if flavor.is_public:
                    msg = _("Cannot remove access for a public flavor")
                    raise exceptions.CommandError(msg)
                else:
                    project_id = identity_common.find_project(
                        identity_client,
                        parsed_args.project,
                        parsed_args.project_domain,
                    ).id
                    compute_client.flavor_access.remove_tenant_access(
                        flavor.id, project_id)
            except Exception as e:
                LOG.error(_("Failed to remove flavor access from project: %s"),
                          e)
                result += 1

        if result > 0:
            raise exceptions.CommandError(_("Command Failed: One or more of"
                                            " the operations failed"))
