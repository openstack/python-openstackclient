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

"""Floating IP Pool action implementations"""

import logging

from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _
from openstackclient.network import common


class ListFloatingIPPool(common.NetworkAndComputeLister):
    """List pools of floating IP addresses"""

    def take_action_network(self, client, parsed_args):
        msg = _("Floating ip pool operations are only available for "
                "Compute v2 network.")
        raise exceptions.CommandError(msg)

    def take_action_compute(self, client, parsed_args):
        columns = (
            'Name',
        )
        data = client.floating_ip_pools.list()

        return (columns,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class ListIPFloatingPool(ListFloatingIPPool):
    """List pools of floating IP addresses"""

    # TODO(tangchen): Remove this class and ``ip floating pool list`` command
    #                 two cycles after Mitaka.

    # This notifies cliff to not display the help for this command
    deprecated = True

    log = logging.getLogger('deprecated')

    def take_action_network(self, client, parsed_args):
        self.log.warning(_('This command has been deprecated. '
                           'Please use "floating ip pool list" instead.'))
        return super(ListIPFloatingPool, self).take_action_network(
            client, parsed_args)

    def take_action_compute(self, client, parsed_args):
        self.log.warning(_('This command has been deprecated. '
                           'Please use "floating ip pool list" instead.'))
        return super(ListIPFloatingPool, self).take_action_compute(
            client, parsed_args)
