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


"""Hypervisor Stats action implementations"""

import logging
import six

from cliff import show


class ShowHypervisorStats(show.ShowOne):
    """Display hypervisor stats details"""

    log = logging.getLogger(__name__ + ".ShowHypervisorStats")

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        compute_client = self.app.client_manager.compute
        hypervisor_stats = compute_client.hypervisors.statistics().to_dict()

        return zip(*sorted(six.iteritems(hypervisor_stats)))
