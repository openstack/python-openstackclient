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

import logging

from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils
import six

from openstackclient.i18n import _


LOG = logging.getLogger(__name__)


class CreateAgent(command.ShowOne):
    _description = _("Create compute agent")

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
    _description = _("Delete compute agent(s)")

    def get_parser(self, prog_name):
        parser = super(DeleteAgent, self).get_parser(prog_name)
        parser.add_argument(
            "id",
            metavar="<id>",
            nargs='+',
            help=_("ID of agent(s) to delete")
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        result = 0
        for id in parsed_args.id:
            try:
                compute_client.agents.delete(id)
            except Exception as e:
                result += 1
                LOG.error(_("Failed to delete agent with ID '%(id)s': %(e)s"),
                          {'id': id, 'e': e})

        if result > 0:
            total = len(parsed_args.id)
            msg = (_("%(result)s of %(total)s agents failed "
                     "to delete.") % {'result': result, 'total': total})
            raise exceptions.CommandError(msg)


class ListAgent(command.Lister):
    _description = _("List compute agents")

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
    _description = _("Set compute agent properties")

    def get_parser(self, prog_name):
        parser = super(SetAgent, self).get_parser(prog_name)
        parser.add_argument(
            "id",
            metavar="<id>",
            help=_("ID of the agent")
        )
        parser.add_argument(
            "--agent-version",
            dest="version",
            metavar="<version>",
            help=_("Version of the agent")
        )
        parser.add_argument(
            "--url",
            metavar="<url>",
            help=_("URL of the agent")
        )
        parser.add_argument(
            "--md5hash",
            metavar="<md5hash>",
            help=_("MD5 hash of the agent")
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        data = compute_client.agents.list(hypervisor=None)
        agent = {}

        for s in data:
            if s.agent_id == int(parsed_args.id):
                agent['version'] = s.version
                agent['url'] = s.url
                agent['md5hash'] = s.md5hash
        if agent == {}:
            msg = _("No agent with a ID of '%(id)s' exists.")
            raise exceptions.CommandError(msg % parsed_args.id)

        if parsed_args.version:
            agent['version'] = parsed_args.version
        if parsed_args.url:
            agent['url'] = parsed_args.url
        if parsed_args.md5hash:
            agent['md5hash'] = parsed_args.md5hash

        args = (
            parsed_args.id,
            agent['version'],
            agent['url'],
            agent['md5hash'],
        )
        compute_client.agents.update(*args)
