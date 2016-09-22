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

"""Volume v2 transfer action implementations"""

import logging

from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils
import six

from openstackclient.i18n import _


LOG = logging.getLogger(__name__)


class AcceptTransferRequest(command.ShowOne):
    """Accept volume transfer request."""

    def get_parser(self, prog_name):
        parser = super(AcceptTransferRequest, self).get_parser(prog_name)
        parser.add_argument(
            'transfer_request',
            metavar="<transfer-request>",
            help=_('Volume transfer request to accept (name or ID)'),
        )
        parser.add_argument(
            'auth_key',
            metavar="<auth-key>",
            help=_('Authentication key of transfer request'),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        transfer_request_id = utils.find_resource(
            volume_client.transfers, parsed_args.transfer_request).id
        transfer_accept = volume_client.transfers.accept(
            transfer_request_id, parsed_args.auth_key)
        transfer_accept._info.pop("links", None)

        return zip(*sorted(six.iteritems(transfer_accept._info)))


class CreateTransferRequest(command.ShowOne):
    """Create volume transfer request."""

    def get_parser(self, prog_name):
        parser = super(CreateTransferRequest, self).get_parser(prog_name)
        parser.add_argument(
            '--name',
            metavar="<name>",
            help=_('New transfer request name (default to None)'),
        )
        parser.add_argument(
            'volume',
            metavar="<volume>",
            help=_('Volume to transfer (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        volume_id = utils.find_resource(
            volume_client.volumes, parsed_args.volume).id
        volume_transfer_request = volume_client.transfers.create(
            volume_id, parsed_args.name,
        )
        volume_transfer_request._info.pop("links", None)

        return zip(*sorted(six.iteritems(volume_transfer_request._info)))


class DeleteTransferRequest(command.Command):
    """Delete volume transfer request(s)."""

    def get_parser(self, prog_name):
        parser = super(DeleteTransferRequest, self).get_parser(prog_name)
        parser.add_argument(
            'transfer_request',
            metavar="<transfer-request>",
            nargs="+",
            help=_('Volume transfer request(s) to delete (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        result = 0

        for t in parsed_args.transfer_request:
            try:
                transfer_request_id = utils.find_resource(
                    volume_client.transfers, t).id
                volume_client.transfers.delete(transfer_request_id)
            except Exception as e:
                result += 1
                LOG.error(_("Failed to delete volume transfer request "
                            "with name or ID '%(transfer)s': %(e)s")
                          % {'transfer': t, 'e': e})

        if result > 0:
            total = len(parsed_args.transfer_request)
            msg = (_("%(result)s of %(total)s volume transfer requests failed"
                   " to delete.") % {'result': result, 'total': total})
            raise exceptions.CommandError(msg)


class ListTransferRequest(command.Lister):
    """Lists all volume transfer requests."""

    def get_parser(self, prog_name):
        parser = super(ListTransferRequest, self).get_parser(prog_name)
        parser.add_argument(
            '--all-projects',
            dest='all_projects',
            action="store_true",
            default=False,
            help=_('Shows detail for all projects. Admin only. '
                   '(defaults to False)')
        )
        return parser

    def take_action(self, parsed_args):
        columns = ['ID', 'Volume ID', 'Name']
        column_headers = ['ID', 'Volume', 'Name']

        volume_client = self.app.client_manager.volume

        volume_transfer_result = volume_client.transfers.list(
            detailed=True,
            search_opts={'all_tenants': parsed_args.all_projects}
        )

        return (column_headers, (
            utils.get_item_properties(s, columns)
            for s in volume_transfer_result))


class ShowTransferRequest(command.ShowOne):
    """Show volume transfer request details."""

    def get_parser(self, prog_name):
        parser = super(ShowTransferRequest, self).get_parser(prog_name)
        parser.add_argument(
            'transfer_request',
            metavar="<transfer-request>",
            help=_('Volume transfer request to display (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        volume_transfer_request = utils.find_resource(
            volume_client.transfers, parsed_args.transfer_request)
        volume_transfer_request._info.pop("links", None)

        return zip(*sorted(six.iteritems(volume_transfer_request._info)))
