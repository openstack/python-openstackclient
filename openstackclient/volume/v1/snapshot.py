#   Copyright 2012-2013 OpenStack, LLC.
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

"""Volume v1 Snapshot action implementations"""

import logging
import six
import sys

from cliff import command
from cliff import lister
from cliff import show

from openstackclient.common import utils


class CreateSnapshot(show.ShowOne):
    """Create snapshot command"""

    log = logging.getLogger(__name__ + '.CreateSnapshot')

    def get_parser(self, prog_name):
        parser = super(CreateSnapshot, self).get_parser(prog_name)
        parser.add_argument(
            'volume',
            metavar='<volume>',
            help='The name or ID of the volume to snapshot',
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            required=True,
            help='Name of the snapshot',
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help='Description of the snapshot',
        )
        parser.add_argument(
            '--force',
            dest='force',
            action='store_true',
            default=False,
            help='Create a snapshot attached to an instance. Default is False',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)', parsed_args)
        volume_client = self.app.client_manager.volume
        volume_id = utils.find_resource(volume_client.volumes,
                                        parsed_args.volume).id
        snapshot = volume_client.volume_snapshots.create(
            volume_id,
            parsed_args.force,
            parsed_args.name,
            parsed_args.description
        )

        return zip(*sorted(six.iteritems(snapshot._info)))


class DeleteSnapshot(command.Command):
    """Delete snapshot command"""

    log = logging.getLogger(__name__ + '.DeleteSnapshot')

    def get_parser(self, prog_name):
        parser = super(DeleteSnapshot, self).get_parser(prog_name)
        parser.add_argument(
            'snapshot',
            metavar='<snapshot>',
            help='Name or ID of snapshot to delete',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)', parsed_args)
        volume_client = self.app.client_manager.volume
        snapshot_id = utils.find_resource(volume_client.volume_snapshots,
                                          parsed_args.snapshot).id
        volume_client.volume_snapshots.delete(snapshot_id)
        return


class ListSnapshot(lister.Lister):
    """List snapshot command"""

    log = logging.getLogger(__name__ + '.ListSnapshot')

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)', parsed_args)
        columns = (
            'ID',
            'Display Name',
            'Display Description',
            'Status',
            'Size'
        )
        data = self.app.client_manager.volume.volume_snapshots.list()
        return (columns,
                (utils.get_item_properties(
                    s, columns,
                    formatters={},
                ) for s in data))


class SetSnapshot(command.Command):
    """Set snapshot command"""

    log = logging.getLogger(__name__ + '.SetSnapshot')

    def get_parser(self, prog_name):
        parser = super(SetSnapshot, self).get_parser(prog_name)
        parser.add_argument(
            'snapshot',
            metavar='<snapshot>',
            help='Name or ID of snapshot to change')
        parser.add_argument(
            '--name',
            metavar='<new-snapshot-name>',
            help='New snapshot name')
        parser.add_argument(
            '--description',
            metavar='<new-snapshot-description>',
            help='New snapshot description')
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)', parsed_args)
        volume_client = self.app.client_manager.volume
        snapshot = utils.find_resource(volume_client.volume_snapshots,
                                       parsed_args.snapshot)
        kwargs = {}
        if parsed_args.name:
            kwargs['display_name'] = parsed_args.name
        if parsed_args.description:
            kwargs['display_description'] = parsed_args.description

        if not kwargs:
            sys.stdout.write("Snapshot not updated, no arguments present")
            return
        snapshot.update(**kwargs)
        return


class ShowSnapshot(show.ShowOne):
    """Show snapshot command"""

    log = logging.getLogger(__name__ + '.ShowSnapshot')

    def get_parser(self, prog_name):
        parser = super(ShowSnapshot, self).get_parser(prog_name)
        parser.add_argument(
            'snapshot',
            metavar='<snapshot>',
            help='Name or ID of snapshot to display')
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)', parsed_args)
        volume_client = self.app.client_manager.volume
        snapshot = utils.find_resource(volume_client.volume_snapshots,
                                       parsed_args.snapshot)

        return zip(*sorted(six.iteritems(snapshot._info)))
