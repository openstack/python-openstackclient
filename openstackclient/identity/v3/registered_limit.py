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

from osc_lib import exceptions
from osc_lib import utils

from openstackclient import command
from openstackclient.i18n import _
from openstackclient.identity import common as common_utils

LOG = logging.getLogger(__name__)


def _format_registered_limit(registered_limit):
    columns = (
        'default_limit',
        'description',
        'id',
        'region_id',
        'resource_name',
        'service_id',
    )
    column_headers = (
        'default_limit',
        'description',
        'id',
        'region_id',
        'resource_name',
        'service_id',
    )
    return (
        column_headers,
        utils.get_item_properties(registered_limit, columns),
    )


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
            help=_(
                'Service responsible for the resource to limit (required) '
                '(name or ID)'
            ),
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
        identity_client = self.app.client_manager.sdk_connection.identity

        kwargs = {}

        if parsed_args.description:
            kwargs["description"] = parsed_args.description

        kwargs["service_id"] = common_utils.find_service_sdk(
            identity_client, parsed_args.service
        ).id

        if parsed_args.region:
            kwargs["region_id"] = identity_client.get_region(
                parsed_args.region
            ).id

        kwargs["resource_name"] = parsed_args.resource_name
        kwargs["default_limit"] = parsed_args.default_limit

        registered_limit = identity_client.create_registered_limit(**kwargs)

        return _format_registered_limit(registered_limit)


class DeleteRegisteredLimit(command.Command):
    _description = _("Delete a registered limit")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'registered_limits',
            metavar='<registered-limits>',
            nargs="+",
            help=_(
                'Registered limit(s) to delete (ID) '
                '(repeat option to remove multiple registered limits)'
            ),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.sdk_connection.identity

        errors = 0
        for registered_limit_id in parsed_args.registered_limits:
            try:
                identity_client.delete_registered_limit(
                    registered_limit_id, ignore_missing=False
                )
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
            total = len(parsed_args.registered_limits)
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
            help=_(
                'Service responsible for the resource to limit (name or ID)'
            ),
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
        identity_client = self.app.client_manager.sdk_connection.identity

        kwargs = {}
        if parsed_args.service:
            kwargs["service_id"] = common_utils.find_service_sdk(
                identity_client, parsed_args.service
            ).id
        if parsed_args.region:
            kwargs["region_id"] = identity_client.get_region(
                parsed_args.region
            ).id

        if parsed_args.resource_name:
            kwargs["resource_name"] = parsed_args.resource_name

        registered_limits = identity_client.registered_limits(**kwargs)

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
                'Service to be updated responsible for the resource to limit '
                '(name or ID). Either --service, --resource-name or --region '
                'must be different than existing value otherwise it will be '
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
        identity_client = self.app.client_manager.sdk_connection.identity

        kwargs = {}
        if parsed_args.service:
            kwargs["service_id"] = common_utils.find_service_sdk(
                identity_client, parsed_args.service
            ).id

        if parsed_args.resource_name:
            kwargs["resource_name"] = parsed_args.resource_name

        if parsed_args.default_limit:
            kwargs["default_limit"] = parsed_args.default_limit

        if parsed_args.description:
            kwargs["description"] = parsed_args.description

        if parsed_args.region:
            kwargs["region_id"] = identity_client.get_region(
                parsed_args.region
            ).id

        registered_limit = identity_client.update_registered_limit(
            parsed_args.registered_limit_id, **kwargs
        )

        return _format_registered_limit(registered_limit)


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
        identity_client = self.app.client_manager.sdk_connection.identity
        registered_limit = identity_client.get_registered_limit(
            parsed_args.registered_limit_id
        )
        return _format_registered_limit(registered_limit)
