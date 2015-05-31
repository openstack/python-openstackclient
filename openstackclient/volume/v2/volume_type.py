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

"""Volume v2 Type action implementations"""

import logging

from cliff import command
from cliff import show
import six

from openstackclient.common import utils


class DeleteVolumeType(command.Command):
    """Delete volume type"""

    log = logging.getLogger(__name__ + ".DeleteVolumeType")

    def get_parser(self, prog_name):
        parser = super(DeleteVolumeType, self).get_parser(prog_name)
        parser.add_argument(
            "volume_type",
            metavar="<volume-type>",
            help="Volume type to delete (name or ID)"
        )
        return parser

    def take_action(self, parsed_args):
        self.log.info("take_action: (%s)", parsed_args)
        volume_client = self.app.client_manager.volume
        volume_type = utils.find_resource(
            volume_client.volume_types, parsed_args.volume_type)
        volume_client.volume_types.delete(volume_type.id)
        return


class ShowVolumeType(show.ShowOne):
    """Display volume type details"""

    log = logging.getLogger(__name__ + ".ShowVolumeType")

    def get_parser(self, prog_name):
        parser = super(ShowVolumeType, self).get_parser(prog_name)
        parser.add_argument(
            "volume_type",
            metavar="<volume-type>",
            help="Volume type to display (name or ID)"
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action: (%s)", parsed_args)
        volume_client = self.app.client_manager.volume
        volume_type = utils.find_resource(
            volume_client.volume_types, parsed_args.volume_type)
        return zip(*sorted(six.iteritems(volume_type._info)))
