#   Copyright 2013 OpenStack, LLC.
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

"""Hypervisor action implementations"""

import logging
import re
import six

from cliff import lister
from cliff import show

from openstackclient.common import utils


class ListHypervisor(lister.Lister):
    """List hypervisors"""

    log = logging.getLogger(__name__ + ".ListHypervisor")

    def get_parser(self, prog_name):
        parser = super(ListHypervisor, self).get_parser(prog_name)
        parser.add_argument(
            "--matching",
            metavar="<hostname>",
            help="Filter hypervisors using <hostname> substring",
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        compute_client = self.app.client_manager.compute
        columns = (
            "ID",
            "Hypervisor Hostname"
        )

        if parsed_args.matching:
            data = compute_client.hypervisors.search(parsed_args.matching)
        else:
            data = compute_client.hypervisors.list()

        return (columns,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class ShowHypervisor(show.ShowOne):
    """Display hypervisor details"""

    log = logging.getLogger(__name__ + ".ShowHypervisor")

    def get_parser(self, prog_name):
        parser = super(ShowHypervisor, self).get_parser(prog_name)
        parser.add_argument(
            "hypervisor",
            metavar="<hypervisor>",
            help="Hypervisor to display (name or ID)")
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        compute_client = self.app.client_manager.compute
        hypervisor = utils.find_resource(compute_client.hypervisors,
                                         parsed_args.hypervisor)._info.copy()

        aggregates = compute_client.aggregates.list()
        hypervisor["aggregates"] = list()
        if aggregates:
            # Hypervisors in nova cells are prefixed by "<cell>@"
            if "@" in hypervisor['service']['host']:
                cell, service_host = hypervisor['service']['host'].split('@',
                                                                         1)
            else:
                cell = None
                service_host = hypervisor['service']['host']

            if cell:
                # The host aggregates are also prefixed by "<cell>@"
                member_of = [aggregate.name
                             for aggregate in aggregates
                             if cell in aggregate.name and
                             service_host in aggregate.hosts]
            else:
                member_of = [aggregate.name
                             for aggregate in aggregates
                             if service_host in aggregate.hosts]
            hypervisor["aggregates"] = member_of

        uptime = compute_client.hypervisors.uptime(hypervisor['id'])._info
        # Extract data from uptime value
        # format: 0 up 0,  0 users,  load average: 0, 0, 0
        # example: 17:37:14 up  2:33,  3 users,  load average: 0.33, 0.36, 0.34
        m = re.match("(.+)\sup\s+(.+),\s+(.+)\susers,\s+load average:\s(.+)",
                     uptime['uptime'])
        if m:
            hypervisor["host_time"] = m.group(1)
            hypervisor["uptime"] = m.group(2)
            hypervisor["users"] = m.group(3)
            hypervisor["load_average"] = m.group(4)

        hypervisor["service_id"] = hypervisor["service"]["id"]
        hypervisor["service_host"] = hypervisor["service"]["host"]
        del hypervisor["service"]

        return zip(*sorted(six.iteritems(hypervisor)))
