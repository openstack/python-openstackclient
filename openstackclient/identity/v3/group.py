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

"""Group action implementations"""

import logging
import sys

from cliff import command
from cliff import lister
from cliff import show

from openstackclient.common import utils


class CreateGroup(show.ShowOne):
    """Create group command"""

    api = 'identity'
    log = logging.getLogger(__name__ + '.CreateGroup')

    def get_parser(self, prog_name):
        parser = super(CreateGroup, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<group-name>',
            help='New group name')
        parser.add_argument(
            '--description',
            metavar='<group-description>',
            help='New group description')
        parser.add_argument(
            '--domain',
            metavar='<group-domain>',
            help='References the domain ID or name which owns the group')

        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity
        if parsed_args.domain:
            domain = utils.find_resource(identity_client.domains,
                                         parsed_args.domain).id
        else:
            domain = None
        group = identity_client.groups.create(
            parsed_args.name,
            domain=domain,
            description=parsed_args.description)

        info = {}
        info.update(group._info)
        return zip(*sorted(info.iteritems()))


class DeleteGroup(command.Command):
    """Delete group command"""

    api = 'identity'
    log = logging.getLogger(__name__ + '.DeleteGroup')

    def get_parser(self, prog_name):
        parser = super(DeleteGroup, self).get_parser(prog_name)
        parser.add_argument(
            'group',
            metavar='<group>',
            help='Name or ID of group to delete')
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity
        group = utils.find_resource(identity_client.groups, parsed_args.group)
        identity_client.groups.delete(group.id)
        return


class ListGroup(lister.Lister):
    """List group command"""

    api = 'identity'
    log = logging.getLogger(__name__ + '.ListGroup')

    def get_parser(self, prog_name):
        parser = super(ListGroup, self).get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help='Additional fields are listed in output')
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        if parsed_args.long:
            columns = ('ID', 'Name', 'Domain ID', 'Description')
        else:
            columns = ('ID', 'Name')
        data = self.app.client_manager.identity.groups.list()
        return (columns,
                (utils.get_item_properties(
                    s, columns,
                    formatters={},
                ) for s in data))


class SetGroup(command.Command):
    """Set group command"""

    api = 'identity'
    log = logging.getLogger(__name__ + '.SetGroup')

    def get_parser(self, prog_name):
        parser = super(SetGroup, self).get_parser(prog_name)
        parser.add_argument(
            'group',
            metavar='<group>',
            help='Name or ID of group to change')
        parser.add_argument(
            '--name',
            metavar='<new-group-name>',
            help='New group name')
        parser.add_argument(
            '--domain',
            metavar='<group-domain>',
            help='New domain name or ID that will now own the group')
        parser.add_argument(
            '--description',
            metavar='<group-description>',
            help='New group description')
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity
        group = utils.find_resource(identity_client.groups, parsed_args.group)
        kwargs = {}
        if parsed_args.name:
            kwargs['name'] = parsed_args.name
        if parsed_args.description:
            kwargs['description'] = parsed_args.description
        if parsed_args.domain:
            domain = utils.find_resource(
                identity_client.domains, parsed_args.domain).id
            kwargs['domain'] = domain

        if not len(kwargs):
            sys.stdout.write("Group not updated, no arguments present")
            return
        identity_client.groups.update(group.id, **kwargs)
        return


class ShowGroup(show.ShowOne):
    """Show group command"""

    api = 'identity'
    log = logging.getLogger(__name__ + '.ShowGroup')

    def get_parser(self, prog_name):
        parser = super(ShowGroup, self).get_parser(prog_name)
        parser.add_argument(
            'group',
            metavar='<group>',
            help='Name or ID of group to display')
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        identity_client = self.app.client_manager.identity
        group = utils.find_resource(identity_client.groups, parsed_args.group)

        info = {}
        info.update(group._info)
        return zip(*sorted(info.iteritems()))
