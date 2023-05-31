#   Copyright 2019 SUSE LLC
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

"""Identity v3 Access Rule action implementations"""

import logging

from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _
from openstackclient.identity import common


LOG = logging.getLogger(__name__)


class DeleteAccessRule(command.Command):
    _description = _("Delete access rule(s)")

    def get_parser(self, prog_name):
        parser = super(DeleteAccessRule, self).get_parser(prog_name)
        parser.add_argument(
            'access_rule',
            metavar='<access-rule>',
            nargs="+",
            help=_('Access rule ID(s) to delete'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        errors = 0
        for ac in parsed_args.access_rule:
            try:
                access_rule = common.get_resource_by_id(
                    identity_client.access_rules, ac
                )
                identity_client.access_rules.delete(access_rule.id)
            except Exception as e:
                errors += 1
                LOG.error(
                    _(
                        "Failed to delete access rule with "
                        "ID '%(ac)s': %(e)s"
                    ),
                    {'ac': ac, 'e': e},
                )

        if errors > 0:
            total = len(parsed_args.access_rule)
            msg = _(
                "%(errors)s of %(total)s access rules failed " "to delete."
            ) % {'errors': errors, 'total': total}
            raise exceptions.CommandError(msg)


class ListAccessRule(command.Lister):
    _description = _("List access rules")

    def get_parser(self, prog_name):
        parser = super(ListAccessRule, self).get_parser(prog_name)
        parser.add_argument(
            '--user',
            metavar='<user>',
            help=_('User whose access rules to list (name or ID)'),
        )
        common.add_user_domain_option_to_parser(parser)
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        if parsed_args.user:
            user_id = common.find_user(
                identity_client, parsed_args.user, parsed_args.user_domain
            ).id
        else:
            user_id = None

        columns = ('ID', 'Service', 'Method', 'Path')
        data = identity_client.access_rules.list(user=user_id)
        return (
            columns,
            (
                utils.get_item_properties(
                    s,
                    columns,
                    formatters={},
                )
                for s in data
            ),
        )


class ShowAccessRule(command.ShowOne):
    _description = _("Display access rule details")

    def get_parser(self, prog_name):
        parser = super(ShowAccessRule, self).get_parser(prog_name)
        parser.add_argument(
            'access_rule',
            metavar='<access-rule>',
            help=_('Access rule ID to display'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        access_rule = common.get_resource_by_id(
            identity_client.access_rules, parsed_args.access_rule
        )

        access_rule._info.pop('links', None)

        return zip(*sorted(access_rule._info.items()))
