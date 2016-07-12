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

"""Identity v3 Consumer action implementations"""

import logging

from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils
import six

from openstackclient.i18n import _


LOG = logging.getLogger(__name__)


class CreateConsumer(command.ShowOne):
    """Create new consumer"""

    def get_parser(self, prog_name):
        parser = super(CreateConsumer, self).get_parser(prog_name)
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('New consumer description'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        consumer = identity_client.oauth1.consumers.create(
            parsed_args.description
        )
        consumer._info.pop('links', None)
        return zip(*sorted(six.iteritems(consumer._info)))


class DeleteConsumer(command.Command):
    """Delete consumer(s)"""

    def get_parser(self, prog_name):
        parser = super(DeleteConsumer, self).get_parser(prog_name)
        parser.add_argument(
            'consumer',
            metavar='<consumer>',
            nargs='+',
            help=_('Consumer(s) to delete'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        result = 0
        for i in parsed_args.consumer:
            try:
                consumer = utils.find_resource(
                    identity_client.oauth1.consumers, i)
                identity_client.oauth1.consumers.delete(consumer.id)
            except Exception as e:
                result += 1
                LOG.error(_("Failed to delete consumer with name or "
                          "ID '%(consumer)s': %(e)s")
                          % {'consumer': i, 'e': e})

        if result > 0:
            total = len(parsed_args.consumer)
            msg = (_("%(result)s of %(total)s consumers failed "
                   "to delete.") % {'result': result, 'total': total})
            raise exceptions.CommandError(msg)


class ListConsumer(command.Lister):
    """List consumers"""

    def take_action(self, parsed_args):
        columns = ('ID', 'Description')
        data = self.app.client_manager.identity.oauth1.consumers.list()
        return (columns,
                (utils.get_item_properties(
                    s, columns,
                    formatters={},
                ) for s in data))


class SetConsumer(command.Command):
    """Set consumer properties"""

    def get_parser(self, prog_name):
        parser = super(SetConsumer, self).get_parser(prog_name)
        parser.add_argument(
            'consumer',
            metavar='<consumer>',
            help=_('Consumer to modify'),
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help=_('New consumer description'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        consumer = utils.find_resource(
            identity_client.oauth1.consumers, parsed_args.consumer)
        kwargs = {}
        if parsed_args.description:
            kwargs['description'] = parsed_args.description

        consumer = identity_client.oauth1.consumers.update(
            consumer.id, **kwargs)


class ShowConsumer(command.ShowOne):
    """Display consumer details"""

    def get_parser(self, prog_name):
        parser = super(ShowConsumer, self).get_parser(prog_name)
        parser.add_argument(
            'consumer',
            metavar='<consumer>',
            help=_('Consumer to display'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        consumer = utils.find_resource(
            identity_client.oauth1.consumers, parsed_args.consumer)

        consumer._info.pop('links', None)
        return zip(*sorted(six.iteritems(consumer._info)))
