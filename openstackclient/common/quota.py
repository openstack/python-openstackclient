#   Copyright 2012 OpenStack Foundation
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

"""Quota action implementations"""

import itertools
import logging
import six
import sys

from cliff import command
from cliff import show


# List the quota items, map the internal argument name to the option
# name that the user sees.

COMPUTE_QUOTAS = {
    'cores': 'cores',
    'fixed_ips': 'fixed-ips',
    'floating_ips': 'floating-ips',
    'injected_file_content_bytes': 'injected-file-size',
    'injected_file_path_bytes': 'injected-path-size',
    'injected_files': 'injected-files',
    'instances': 'instances',
    'key_pairs': 'key-pairs',
    'metadata_items': 'properties',
    'ram': 'ram',
    'security_group_rules': 'secgroup-rules',
    'security_groups': 'secgroups',
}

VOLUME_QUOTAS = {
    'gigabytes': 'gigabytes',
    'snapshots': 'snapshots',
    'volumes': 'volumes',
}


class SetQuota(command.Command):
    """Set quotas for project or class"""

    log = logging.getLogger(__name__ + '.SetQuota')

    def get_parser(self, prog_name):
        parser = super(SetQuota, self).get_parser(prog_name)
        parser.add_argument(
            'project',
            metavar='<project/class>',
            help='Set quotas for this project or class (name/ID)',
        )
        parser.add_argument(
            '--class',
            dest='quota_class',
            action='store_true',
            default=False,
            help='Set quotas for <class>',
        )
        for k, v in itertools.chain(
                COMPUTE_QUOTAS.items(), VOLUME_QUOTAS.items()):
            parser.add_argument(
                '--%s' % v,
                metavar='<%s>' % v,
                type=int,
                help='New value for the %s quota' % v,
            )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)', parsed_args)

        compute_client = self.app.client_manager.compute
        volume_client = self.app.client_manager.volume

        compute_kwargs = {}
        for k, v in COMPUTE_QUOTAS.items():
            if v in parsed_args:
                compute_kwargs[k] = getattr(parsed_args, v, None)

        volume_kwargs = {}
        for k, v in VOLUME_QUOTAS.items():
            if v in parsed_args:
                volume_kwargs[k] = getattr(parsed_args, v, None)

        if compute_kwargs == {} and volume_kwargs == {}:
            sys.stderr.write("No quotas updated")
            return

        if parsed_args.quota_class:
            if compute_kwargs:
                compute_client.quota_classes.update(
                    parsed_args.project,
                    **compute_kwargs)
            if volume_kwargs:
                volume_client.quota_classes.update(
                    parsed_args.project,
                    **volume_kwargs)
        else:
            if compute_kwargs:
                compute_client.quotas.update(
                    parsed_args.project,
                    **compute_kwargs)
            if volume_kwargs:
                volume_client.quotas.update(
                    parsed_args.project,
                    **volume_kwargs)


class ShowQuota(show.ShowOne):
    """Show quotas for project or class"""

    log = logging.getLogger(__name__ + '.ShowQuota')

    def get_parser(self, prog_name):
        parser = super(ShowQuota, self).get_parser(prog_name)
        parser.add_argument(
            'project',
            metavar='<project/class>',
            help='Show this project or class (name/ID)',
        )
        type_group = parser.add_mutually_exclusive_group()
        type_group.add_argument(
            '--class',
            dest='quota_class',
            action='store_true',
            default=False,
            help='Show quotas for <class>',
        )
        type_group.add_argument(
            '--default',
            dest='default',
            action='store_true',
            default=False,
            help='Show default quotas for <project>'
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)', parsed_args)

        compute_client = self.app.client_manager.compute
        volume_client = self.app.client_manager.volume

        # NOTE(dtroyer): These quota API calls do not validate the project
        #                or class arguments and return what appears to be
        #                the default quota values if the project or class
        #                does not exist. If this is determined to be the
        #                intended behaviour of the API we will validate
        #                the argument with Identity ourselves later.
        if parsed_args.quota_class:
            compute_quota = compute_client.quota_classes.get(
                parsed_args.project)
            volume_quota = volume_client.quota_classes.get(
                parsed_args.project)
        elif parsed_args.default:
            compute_quota = compute_client.quotas.defaults(
                parsed_args.project)
            volume_quota = volume_client.quotas.defaults(
                parsed_args.project)
        else:
            compute_quota = compute_client.quotas.get(parsed_args.project)
            volume_quota = volume_client.quotas.get(parsed_args.project)

        info = {}
        info.update(compute_quota._info)
        info.update(volume_quota._info)

        # Map the internal quota names to the external ones
        for k, v in itertools.chain(
                COMPUTE_QUOTAS.items(), VOLUME_QUOTAS.items()):
            if not k == v and info[k]:
                info[v] = info[k]
                info.pop(k)

        # Handle project ID special as it only appears in output
        if info['id']:
            info['project'] = info['id']
            info.pop('id')

        return zip(*sorted(six.iteritems(info)))
