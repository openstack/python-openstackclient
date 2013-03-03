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

"""Volume v1 Quota action implementations"""

import logging

from cliff import command
from cliff import show

from openstackclient.common import utils


class ListQuota(show.ShowOne):
    """List quota command"""

    api = 'volume'
    log = logging.getLogger(__name__ + '.ListQuota')

    def get_parser(self, prog_name):
        parser = super(ListQuota, self).get_parser(prog_name)
        parser.add_argument(
            'tenant',
            metavar='<tenant>',
            help='ID of tenant to list the default quotas for')
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        volume_client = self.app.client_manager.volume
        defaults = volume_client.quotas.defaults(parsed_args.tenant)

        return zip(*sorted(defaults._info.iteritems()))


class SetQuota(command.Command):
    """Set quota command"""

    api = 'volume'
    log = logging.getLogger(__name__ + '.SetQuota')

    def get_parser(self, prog_name):
        parser = super(SetQuota, self).get_parser(prog_name)
        parser.add_argument(
            'tenant',
            metavar='<tenant>',
            help='ID of tenant to set the quotas for')
        parser.add_argument(
            '--volumes',
            metavar='<new-volumes>',
            type=int,
            help='New value for the volumes quota')
        parser.add_argument(
            '--gigabytes',
            metavar='<new-gigabytes>',
            type=int,
            help='New value for the gigabytes quota')
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)

        kwargs = {}
        if parsed_args.volumes:
            kwargs['volumes'] = parsed_args.volumes
        if parsed_args.gigabytes:
            kwargs['gigabytes'] = parsed_args.gigabytes

        if kwargs == {}:
            stdout.write("Quota not updated, no arguments present")
            return

        volume_client = self.app.client_manager.volume
        volume_client.quotas.update(parsed_args.tenant,
                                    parsed_args.volumes,
                                    parsed_args.gigabytes)

        return


class ShowQuota(show.ShowOne):
    """Show quota command"""

    api = 'volume'
    log = logging.getLogger(__name__ + '.ShowQuota')

    def get_parser(self, prog_name):
        parser = super(ShowQuota, self).get_parser(prog_name)
        parser.add_argument(
            'tenant',
            metavar='<tenant>',
            help='ID of tenant to list the quotas for')
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        volume_client = self.app.client_manager.volume
        quota = utils.find_resource(volume_client.quotas,
                                    parsed_args.tenant)

        return zip(*sorted(quota._info.iteritems()))
