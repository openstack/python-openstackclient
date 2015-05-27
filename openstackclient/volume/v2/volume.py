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

"""Volume V2 Volume action implementations"""

import logging

from cliff import command
from cliff import show
import six

from openstackclient.common import utils


class DeleteVolume(command.Command):
    """Delete volume(s)"""

    log = logging.getLogger(__name__ + ".DeleteVolume")

    def get_parser(self, prog_name):
        parser = super(DeleteVolume, self).get_parser(prog_name)
        parser.add_argument(
            "volumes",
            metavar="<volume>",
            nargs="+",
            help="Volume(s) to delete (name or ID)"
        )
        parser.add_argument(
            "--force",
            dest="force",
            action="store_true",
            default=False,
            help="Attempt forced removal of volume(s), regardless of state "
                 "(defaults to False"
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action: (%s)", parsed_args)
        volume_client = self.app.client_manager.volume
        for volume in parsed_args.volumes:
            volume_obj = utils.find_resource(
                volume_client.volumes, volume)
        if parsed_args.force:
            volume_client.volumes.force_delete(volume_obj.id)
        else:
            volume_client.volumes.delete(volume_obj.id)
        return


class ShowVolume(show.ShowOne):
    """Display volume details"""

    log = logging.getLogger(__name__ + '.ShowVolume')

    def get_parser(self, prog_name):
        parser = super(ShowVolume, self).get_parser(prog_name)
        parser.add_argument(
            'volume',
            metavar="<volume-id>",
            help="Volume to display (name or ID)"
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)', parsed_args)
        volume_client = self.app.client_manager.volume
        volume = utils.find_resource(volume_client.volumes, parsed_args.volume)

        # Remove key links from being displayed
        volume._info.pop("links", None)
        return zip(*sorted(six.iteritems(volume._info)))
