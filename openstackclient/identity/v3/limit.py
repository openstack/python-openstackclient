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

from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _
from openstackclient.identity import common as common_utils

LOG = logging.getLogger(__name__)


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
        identity_client = self.app.client_manager.identity

        project = common_utils.find_project(
            identity_client, parsed_args.project
        )
        service = common_utils.find_service(
            identity_client, parsed_args.service
        )
        region = None
        if parsed_args.region:
            if 'None' not in parsed_args.region:
                # NOTE (vishakha): Due to bug #1799153 and for any another
                # related case where GET resource API does not support the
                # filter by name, osc_lib.utils.find_resource() method cannot
                # be used because that method try to fall back to list all the
                # resource if requested resource cannot be get via name. Which
                # ends up with NoUniqueMatch error.
                # So osc_lib.utils.find_resource() function cannot be used for
                # 'regions', using common_utils.get_resource() instead.
                region = common_utils.get_resource(
                    identity_client.regions, parsed_args.region
                )
            else:
                self.log.warning(
                    _(
                        "Passing 'None' to indicate no region is deprecated. "
                        "Instead, don't pass --region."
                    )
                )

        limit = identity_client.limits.create(
            project,
            service,
            parsed_args.resource_name,
            parsed_args.resource_limit,
            description=parsed_args.description,
            region=region,
        )

        limit._info.pop('links', None)
        return zip(*sorted(limit._info.items()))


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
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        service = None
        if parsed_args.service:
            service = common_utils.find_service(
                identity_client, parsed_args.service
            )
        region = None
        if parsed_args.region:
            if 'None' not in parsed_args.region:
                # NOTE (vishakha): Due to bug #1799153 and for any another
                # related case where GET resource API does not support the
                # filter by name, osc_lib.utils.find_resource() method cannot
                # be used because that method try to fall back to list all the
                # resource if requested resource cannot be get via name. Which
                # ends up with NoUniqueMatch error.
                # So osc_lib.utils.find_resource() function cannot be used for
                # 'regions', using common_utils.get_resource() instead.
                region = common_utils.get_resource(
                    identity_client.regions, parsed_args.region
                )
            else:
                self.log.warning(
                    _(
                        "Passing 'None' to indicate no region is deprecated. "
                        "Instead, don't pass --region."
                    )
                )

        project = None
        if parsed_args.project:
            project = utils.find_resource(
                identity_client.projects, parsed_args.project
            )

        limits = identity_client.limits.list(
            service=service,
            resource_name=parsed_args.resource_name,
            region=region,
            project=project,
        )

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
        identity_client = self.app.client_manager.identity
        limit = identity_client.limits.get(parsed_args.limit_id)
        limit._info.pop('links', None)
        return zip(*sorted(limit._info.items()))


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
        identity_client = self.app.client_manager.identity

        limit = identity_client.limits.update(
            parsed_args.limit_id,
            description=parsed_args.description,
            resource_limit=parsed_args.resource_limit,
        )

        limit._info.pop('links', None)

        return zip(*sorted(limit._info.items()))


class DeleteLimit(command.Command):
    _description = _("Delete a limit")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'limit_id',
            metavar='<limit-id>',
            nargs="+",
            help=_('Limit to delete (ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        errors = 0
        for limit_id in parsed_args.limit_id:
            try:
                identity_client.limits.delete(limit_id)
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
