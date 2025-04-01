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

"""Registered limits action implementations."""

import logging

from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _
from openstackclient.identity import common as common_utils

LOG = logging.getLogger(__name__)


class CreateRegisteredLimit(command.ShowOne):
    _description = _("Create a registered limit")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('Description of the registered limit'),
        )
        parser.add_argument(
            '--region',
            metavar='<region>',
            help=_('Region for the registered limit to affect'),
        )
        parser.add_argument(
            '--service',
            metavar='<service>',
            required=True,
            help=_('Service responsible for the resource to limit (required)'),
        )
        parser.add_argument(
            '--default-limit',
            type=int,
            metavar='<default-limit>',
            required=True,
            help=_('The default limit for the resources to assume (required)'),
        )
        parser.add_argument(
            'resource_name',
            metavar='<resource-name>',
            help=_('The name of the resource to limit'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        service = utils.find_resource(
            identity_client.services, parsed_args.service
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

        registered_limit = identity_client.registered_limits.create(
            service,
            parsed_args.resource_name,
            parsed_args.default_limit,
            description=parsed_args.description,
            region=region,
        )

        registered_limit._info.pop('links', None)
        return zip(*sorted(registered_limit._info.items()))


class DeleteRegisteredLimit(command.Command):
    _description = _("Delete a registered limit")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'registered_limit_id',
            metavar='<registered-limit-id>',
            nargs="+",
            help=_('Registered limit to delete (ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        errors = 0
        for registered_limit_id in parsed_args.registered_limit_id:
            try:
                identity_client.registered_limits.delete(registered_limit_id)
            except Exception as e:
                errors += 1
                from pprint import pprint

                pprint(type(e))
                LOG.error(
                    _(
                        "Failed to delete registered limit with ID "
                        "'%(id)s': %(e)s"
                    ),
                    {'id': registered_limit_id, 'e': e},
                )

        if errors > 0:
            total = len(parsed_args.registered_limit_id)
            msg = _(
                "%(errors)s of %(total)s registered limits failed to delete."
            ) % {'errors': errors, 'total': total}
            raise exceptions.CommandError(msg)


class ListRegisteredLimit(command.Lister):
    _description = _("List registered limits")

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
            help=_('Region for the limit to affect.'),
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

        registered_limits = identity_client.registered_limits.list(
            service=service,
            resource_name=parsed_args.resource_name,
            region=region,
        )

        columns = (
            'ID',
            'Service ID',
            'Resource Name',
            'Default Limit',
            'Description',
            'Region ID',
        )
        return (
            columns,
            (utils.get_item_properties(s, columns) for s in registered_limits),
        )


class SetRegisteredLimit(command.ShowOne):
    _description = _("Update information about a registered limit")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'registered_limit_id',
            metavar='<registered-limit-id>',
            help=_('Registered limit to update (ID)'),
        )
        parser.add_argument(
            '--service',
            metavar='<service>',
            help=_(
                'Service to be updated responsible for the resource to '
                'limit. Either --service, --resource-name or --region must '
                'be different than existing value otherwise it will be '
                'duplicate entry'
            ),
        )
        parser.add_argument(
            '--resource-name',
            metavar='<resource-name>',
            help=_(
                'Resource to be updated responsible for the resource to '
                'limit. Either --service, --resource-name or --region must '
                'be different than existing value otherwise it will be '
                'duplicate entry'
            ),
        )
        parser.add_argument(
            '--default-limit',
            metavar='<default-limit>',
            type=int,
            help=_('The default limit for the resources to assume'),
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('Description to update of the registered limit'),
        )
        parser.add_argument(
            '--region',
            metavar='<region>',
            help=_(
                'Region for the registered limit to affect. Either '
                '--service, --resource-name or --region must be '
                'different than existing value otherwise it will be '
                'duplicate entry'
            ),
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
                    _("Passing 'None' to indicate no region is deprecated.")
                )

        registered_limit = identity_client.registered_limits.update(
            parsed_args.registered_limit_id,
            service=service,
            resource_name=parsed_args.resource_name,
            default_limit=parsed_args.default_limit,
            description=parsed_args.description,
            region=region,
        )

        registered_limit._info.pop('links', None)
        return zip(*sorted(registered_limit._info.items()))


class ShowRegisteredLimit(command.ShowOne):
    _description = _("Display registered limit details")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'registered_limit_id',
            metavar='<registered-limit-id>',
            help=_('Registered limit to display (ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        registered_limit = identity_client.registered_limits.get(
            parsed_args.registered_limit_id
        )
        registered_limit._info.pop('links', None)
        return zip(*sorted(registered_limit._info.items()))
