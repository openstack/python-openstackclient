# Copyright (c) 2019 SUSE Linux Products GmbH
# All Rights Reserved
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#

"""Subnet onboard action implementation"""

import argparse
import logging

from openstackclient.i18n import _
from openstackclient.network.v2 import subnet_pool


LOG = logging.getLogger(__name__)


class NetworkOnboardSubnets(subnet_pool.AddNetworkSubnetPool):
    """Onboard network subnets into a subnet pool"""

    _description = _("DEPRECATED: Use 'subnet pool add network' instead.")

    def take_action(self, parsed_args: argparse.Namespace) -> None:
        self.log.warning(
            _(
                'The "network onboard subnet" command is deprecated '
                'in favour of "subnet pool add network". '
                'It will be removed in a future release.'
            )
        )
        super().take_action(parsed_args)
