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

from openstackclient.common import utils


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

NETWORK_QUOTAS = {
    'floatingip': 'floating-ips',
    'security_group_rule': 'secgroup-rules',
    'security_group': 'secgroups',
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
        parser.add_argument(
            '--volume-type',
            metavar='<volume-type>',
            help='Set quotas for a specific <volume-type>',
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):

        compute_client = self.app.client_manager.compute
        volume_client = self.app.client_manager.volume

        compute_kwargs = {}
        for k, v in COMPUTE_QUOTAS.items():
            value = getattr(parsed_args, k, None)
            if value is not None:
                compute_kwargs[k] = value

        volume_kwargs = {}
        for k, v in VOLUME_QUOTAS.items():
            value = getattr(parsed_args, k, None)
            if value is not None:
                if parsed_args.volume_type:
                    k = k + '_%s' % parsed_args.volume_type
                volume_kwargs[k] = value

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

    def get_compute_volume_quota(self, client, parsed_args):
        try:
            if parsed_args.quota_class:
                quota = client.quota_classes.get(parsed_args.project)
            elif parsed_args.default:
                quota = client.quotas.defaults(parsed_args.project)
            else:
                quota = client.quotas.get(parsed_args.project)
        except Exception as e:
            if type(e).__name__ == 'EndpointNotFound':
                return {}
            else:
                raise e
        return quota._info

    def get_network_quota(self, parsed_args):
        if parsed_args.quota_class or parsed_args.default:
            return {}
        service_catalog = self.app.client_manager.auth_ref.service_catalog
        if 'network' in service_catalog.get_endpoints():
            network_client = self.app.client_manager.network
            return network_client.show_quota(parsed_args.project)['quota']
        else:
            return {}

    @utils.log_method(log)
    def take_action(self, parsed_args):

        compute_client = self.app.client_manager.compute
        volume_client = self.app.client_manager.volume
        # NOTE(dtroyer): These quota API calls do not validate the project
        #                or class arguments and return what appears to be
        #                the default quota values if the project or class
        #                does not exist. If this is determined to be the
        #                intended behaviour of the API we will validate
        #                the argument with Identity ourselves later.
        compute_quota_info = self.get_compute_volume_quota(compute_client,
                                                           parsed_args)
        volume_quota_info = self.get_compute_volume_quota(volume_client,
                                                          parsed_args)
        network_quota_info = self.get_network_quota(parsed_args)

        info = {}
        info.update(compute_quota_info)
        info.update(volume_quota_info)
        info.update(network_quota_info)

        # Map the internal quota names to the external ones
        # COMPUTE_QUOTAS and NETWORK_QUOTAS share floating-ips,
        # secgroup-rules and secgroups as dict value, so when
        # neutron is enabled, quotas of these three resources
        # in nova will be replaced by neutron's.
        for k, v in itertools.chain(
                COMPUTE_QUOTAS.items(), VOLUME_QUOTAS.items(),
                NETWORK_QUOTAS.items()):
            if not k == v and info.get(k):
                info[v] = info[k]
                info.pop(k)

        # Handle project ID special as it only appears in output
        if 'id' in info:
            info['project'] = info.pop('id')

        return zip(*sorted(six.iteritems(info)))
