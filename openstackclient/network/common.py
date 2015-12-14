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

import abc
import six

from openstackclient.common import command


@six.add_metaclass(abc.ABCMeta)
class NetworkAndComputeCommand(command.Command):
    """Network and Compute Command"""

    def take_action(self, parsed_args):
        if self.app.client_manager.is_network_endpoint_enabled():
            return self.take_action_network(self.app.client_manager.network,
                                            parsed_args)
        else:
            return self.take_action_compute(self.app.client_manager.compute,
                                            parsed_args)

    def get_parser(self, prog_name):
        self.log.debug('get_parser(%s)', prog_name)
        parser = super(NetworkAndComputeCommand, self).get_parser(prog_name)
        parser = self.update_parser_common(parser)
        self.log.debug('common parser: %s', parser)
        if self.app.client_manager.is_network_endpoint_enabled():
            return self.update_parser_network(parser)
        else:
            return self.update_parser_compute(parser)

    def update_parser_common(self, parser):
        """Default is no updates to parser."""
        return parser

    def update_parser_network(self, parser):
        """Default is no updates to parser."""
        return parser

    def update_parser_compute(self, parser):
        """Default is no updates to parser."""
        return parser

    @abc.abstractmethod
    def take_action_network(self, client, parsed_args):
        """Override to do something useful."""
        pass

    @abc.abstractmethod
    def take_action_compute(self, client, parsed_args):
        """Override to do something useful."""
        pass
