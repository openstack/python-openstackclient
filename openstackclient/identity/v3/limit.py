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

"""Limits action implementations."""

import logging

from osc_lib import exceptions
from osc_lib import utils

from openstackclient import command
from openstackclient.i18n import _
from openstackclient.identity import common as common_utils

LOG = logging.getLogger(__name__)


def _format_limit(limit):
    columns = (
        "description",
        "id",
        "project_id",
        "region_id",
        "resource_limit",
        "resource_name",
        "service_id",
    )
    column_headers = (
        "description",
        "id",
        "project_id",
        "region_id",
        "resource_limit",
        "resource_name",
        "service_id",
    )
    return (column_headers, utils.get_item_properties(limit, columns))


class CreateLimit(command.ShowOne):
    _description = _("Create a limit")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('Description of the limit'),
        )
        parser.add_argument(
            '--region',
            metavar='<region>',
            help=_('Region for the limit to affect.'),
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            required=True,
            help=_('Project to associate the resource limit to'),
        )
        common_utils.add_project_domain_option_to_parser(parser)
        parser.add_argument(
            '--service',
            metavar='<service>',
            required=True,
            help=_('Service responsible for the resource to limit'),
        )
        parser.add_argument(
            '--resource-limit',
            metavar='<resource-limit>',
            required=True,
            type=int,
            help=_('The resource limit for the project to assume'),
        )
        parser.add_argument(
            'resource_name',
            metavar='<resource-name>',
            help=_('The name of the resource to limit'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.sdk_connection.identity

        kwargs = {
            "resource_name": parsed_args.resource_name,
            "resource_limit": parsed_args.resource_limit,
        }
        if parsed_args.description:
            kwargs["description"] = parsed_args.description

        kwargs["project_id"] = common_utils.find_project_id_sdk(
            identity_client,
            parsed_args.project,
            domain_name_or_id=parsed_args.project_domain,
        )

        kwargs["service_id"] = common_utils.find_service_sdk(
            identity_client, parsed_args.service
        ).id

        if parsed_args.region:
            kwargs["region_id"] = identity_client.get_region(
                parsed_args.region
            ).id

        limit = identity_client.create_limit(**kwargs)

        return _format_limit(limit)


class ListLimit(command.Lister):
    _description = _("List limits")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--service',
            metavar='<service>',
            help=_('Service responsible for the resource to limit'),
        )
        parser.add_argument(
            '--resource-name',
            metavar='<resource-name>',
            dest='resource_name',
            help=_('The name of the resource to limit'),
        )
        parser.add_argument(
            '--region',
            metavar='<region>',
            help=_('Region for the registered limit to affect.'),
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_('List resource limits associated with project'),
        )
        common_utils.add_project_domain_option_to_parser(parser)

        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.sdk_connection.identity

        kwargs = {}
        if parsed_args.service:
            kwargs["service_id"] = common_utils.find_service_sdk(
                identity_client, parsed_args.service
            )

        if parsed_args.region:
            kwargs["region_id"] = identity_client.get_region(
                parsed_args.region
            ).id

        if parsed_args.project:
            project_domain_id = None
            if parsed_args.project_domain:
                project_domain_id = common_utils.find_domain_id_sdk(
                    identity_client, parsed_args.project_domain
                )

            kwargs["project_id"] = common_utils._find_sdk_id(
                identity_client.find_project,
                name_or_id=parsed_args.project,
                domain_id=project_domain_id,
            )

        if parsed_args.resource_name:
            kwargs["resource_name"] = parsed_args.resource_name

        limits = identity_client.limits(**kwargs)

        columns = (
            'ID',
            'Project ID',
            'Service ID',
            'Resource Name',
            'Resource Limit',
            'Description',
            'Region ID',
        )
        return (
            columns,
            (utils.get_item_properties(s, columns) for s in limits),
        )


class ShowLimit(command.ShowOne):
    _description = _("Display limit details")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'limit_id',
            metavar='<limit-id>',
            help=_('Limit to display (ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.sdk_connection.identity
        limit = identity_client.get_limit(parsed_args.limit_id)
        return _format_limit(limit)


class SetLimit(command.ShowOne):
    _description = _("Update information about a limit")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'limit_id',
            metavar='<limit-id>',
            help=_('Limit to update (ID)'),
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('Description of the limit'),
        )
        parser.add_argument(
            '--resource-limit',
            metavar='<resource-limit>',
            dest='resource_limit',
            type=int,
            help=_('The resource limit for the project to assume'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.sdk_connection.identity

        kwargs = {}
        if parsed_args.description:
            kwargs["description"] = parsed_args.description
        if parsed_args.resource_limit:
            kwargs["resource_limit"] = parsed_args.resource_limit
        limit = identity_client.update_limit(parsed_args.limit_id, **kwargs)

        return _format_limit(limit)


class DeleteLimit(command.Command):
    _description = _("Delete a limit")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'limit_id',
            metavar='<limit-id>',
            nargs="+",
            help=_(
                'Limit to delete (ID) '
                '(repeat option to remove multiple limits)'
            ),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.sdk_connection.identity

        errors = 0
        for limit_id in parsed_args.limit_id:
            try:
                identity_client.delete_limit(limit_id)
            except Exception as e:
                errors += 1
                LOG.error(
                    _("Failed to delete limit with ID '%(id)s': %(e)s"),
                    {'id': limit_id, 'e': e},
                )

        if errors > 0:
            total = len(parsed_args.limit_id)
            msg = _("%(errors)s of %(total)s limits failed to delete.") % {
                'errors': errors,
                'total': total,
            }
            raise exceptions.CommandError(msg)
