#   Copyright 2012-2013 OpenStack Foundation
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

"""Identity v3 Domain action implementations"""

import logging

from keystoneauth1 import exceptions as ks_exc
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils
import six

from openstackclient.i18n import _
from openstackclient.identity import common


LOG = logging.getLogger(__name__)


class CreateDomain(command.ShowOne):
    """Create new domain"""

    def get_parser(self, prog_name):
        parser = super(CreateDomain, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<domain-name>',
            help=_('New domain name'),
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('New domain description'),
        )
        enable_group = parser.add_mutually_exclusive_group()
        enable_group.add_argument(
            '--enable',
            action='store_true',
            help=_('Enable domain (default)'),
        )
        enable_group.add_argument(
            '--disable',
            action='store_true',
            help=_('Disable domain'),
        )
        parser.add_argument(
            '--or-show',
            action='store_true',
            help=_('Return existing domain'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        enabled = True
        if parsed_args.disable:
            enabled = False

        try:
            domain = identity_client.domains.create(
                name=parsed_args.name,
                description=parsed_args.description,
                enabled=enabled,
            )
        except ks_exc.Conflict:
            if parsed_args.or_show:
                domain = utils.find_resource(identity_client.domains,
                                             parsed_args.name)
                LOG.info(_('Returning existing domain %s'), domain.name)
            else:
                raise

        domain._info.pop('links')
        return zip(*sorted(six.iteritems(domain._info)))


class DeleteDomain(command.Command):
    """Delete domain(s)"""

    def get_parser(self, prog_name):
        parser = super(DeleteDomain, self).get_parser(prog_name)
        parser.add_argument(
            'domain',
            metavar='<domain>',
            nargs='+',
            help=_('Domain(s) to delete (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        result = 0
        for i in parsed_args.domain:
            try:
                domain = utils.find_resource(identity_client.domains, i)
                identity_client.domains.delete(domain.id)
            except Exception as e:
                result += 1
                LOG.error(_("Failed to delete domain with name or "
                          "ID '%(domain)s': %(e)s")
                          % {'domain': i, 'e': e})

        if result > 0:
            total = len(parsed_args.domain)
            msg = (_("%(result)s of %(total)s domains failed "
                   "to delete.") % {'result': result, 'total': total})
            raise exceptions.CommandError(msg)


class ListDomain(command.Lister):
    """List domains"""

    def take_action(self, parsed_args):
        columns = ('ID', 'Name', 'Enabled', 'Description')
        data = self.app.client_manager.identity.domains.list()
        return (columns,
                (utils.get_item_properties(
                    s, columns,
                    formatters={},
                ) for s in data))


class SetDomain(command.Command):
    """Set domain properties"""

    def get_parser(self, prog_name):
        parser = super(SetDomain, self).get_parser(prog_name)
        parser.add_argument(
            'domain',
            metavar='<domain>',
            help=_('Domain to modify (name or ID)'),
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('New domain name'),
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('New domain description'),
        )
        enable_group = parser.add_mutually_exclusive_group()
        enable_group.add_argument(
            '--enable',
            action='store_true',
            help=_('Enable domain'),
        )
        enable_group.add_argument(
            '--disable',
            action='store_true',
            help=_('Disable domain'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        domain = utils.find_resource(identity_client.domains,
                                     parsed_args.domain)
        kwargs = {}
        if parsed_args.name:
            kwargs['name'] = parsed_args.name
        if parsed_args.description:
            kwargs['description'] = parsed_args.description

        if parsed_args.enable:
            kwargs['enabled'] = True
        if parsed_args.disable:
            kwargs['enabled'] = False

        identity_client.domains.update(domain.id, **kwargs)


class ShowDomain(command.ShowOne):
    """Display domain details"""

    def get_parser(self, prog_name):
        parser = super(ShowDomain, self).get_parser(prog_name)
        parser.add_argument(
            'domain',
            metavar='<domain>',
            help=_('Domain to display (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity

        domain_str = common._get_token_resource(identity_client, 'domain',
                                                parsed_args.domain)

        domain = utils.find_resource(identity_client.domains,
                                     domain_str)

        domain._info.pop('links')
        return zip(*sorted(six.iteritems(domain._info)))
