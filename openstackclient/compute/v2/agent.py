#   Copyright 2013 OpenStack Foundation
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

"""Agent action implementations"""

import six

from openstackclient.common import command
from openstackclient.common import utils
from openstackclient.i18n import _


class CreateAgent(command.ShowOne):
    """Create compute agent command"""

    def get_parser(self, prog_name):
        parser = super(CreateAgent, self).get_parser(prog_name)
        parser.add_argument(
            "os",
            metavar="<os>",
            help=_("Type of OS")
        )
        parser.add_argument(
            "architecture",
            metavar="<architecture>",
            help=_("Type of architecture")
        )
        parser.add_argument(
            "version",
            metavar="<version>",
            help=_("Version")
        )
        parser.add_argument(
            "url",
            metavar="<url>",
            help=_("URL")
        )
        parser.add_argument(
            "md5hash",
            metavar="<md5hash>",
            help=_("MD5 hash")
        )
        parser.add_argument(
            "hypervisor",
            metavar="<hypervisor>",
            default="xen",
            help=_("Type of hypervisor")
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        args = (
            parsed_args.os,
            parsed_args.architecture,
            parsed_args.version,
            parsed_args.url,
            parsed_args.md5hash,
            parsed_args.hypervisor
        )
        agent = compute_client.agents.create(*args)._info.copy()
        return zip(*sorted(six.iteritems(agent)))


class DeleteAgent(command.Command):
    """Delete compute agent command"""

    def get_parser(self, prog_name):
        parser = super(DeleteAgent, self).get_parser(prog_name)
        parser.add_argument(
            "id",
            metavar="<id>",
            help=_("ID of agent to delete")
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        compute_client.agents.delete(parsed_args.id)


class ListAgent(command.Lister):
    """List compute agent command"""

    def get_parser(self, prog_name):
        parser = super(ListAgent, self).get_parser(prog_name)
        parser.add_argument(
            "--hypervisor",
            metavar="<hypervisor>",
            help=_("Type of hypervisor")
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        columns = (
            "Agent ID",
            "Hypervisor",
            "OS",
            "Architecture",
            "Version",
            "Md5Hash",
            "URL"
        )
        data = compute_client.agents.list(parsed_args.hypervisor)
        return (columns,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class SetAgent(command.Command):
    """Set compute agent command"""

    def get_parser(self, prog_name):
        parser = super(SetAgent, self).get_parser(prog_name)
        parser.add_argument(
            "id",
            metavar="<id>",
            help=_("ID of the agent")
        )
        parser.add_argument(
            "version",
            metavar="<version>",
            help=_("Version of the agent")
        )
        parser.add_argument(
            "url",
            metavar="<url>",
            help=_("URL")
        )
        parser.add_argument(
            "md5hash",
            metavar="<md5hash>",
            help=_("MD5 hash")
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        args = (
            parsed_args.id,
            parsed_args.version,
            parsed_args.url,
            parsed_args.md5hash
        )
        compute_client.agents.update(*args)
