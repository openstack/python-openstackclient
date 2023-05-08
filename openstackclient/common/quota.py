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

import argparse
import itertools
import logging
import sys

from osc_lib.command import command
from osc_lib import utils

from openstackclient.i18n import _
from openstackclient.network import common

LOG = logging.getLogger(__name__)

# List the quota items, map the internal argument name to the option
# name that the user sees.

COMPUTE_QUOTAS = {
    'cores': 'cores',
    'fixed_ips': 'fixed-ips',
    'injected_file_content_bytes': 'injected-file-size',
    'injected_file_path_bytes': 'injected-path-size',
    'injected_files': 'injected-files',
    'instances': 'instances',
    'key_pairs': 'key-pairs',
    'metadata_items': 'properties',
    'ram': 'ram',
    'server_groups': 'server-groups',
    'server_group_members': 'server-group-members',
}

VOLUME_QUOTAS = {
    'backups': 'backups',
    'backup_gigabytes': 'backup-gigabytes',
    'gigabytes': 'gigabytes',
    'per_volume_gigabytes': 'per-volume-gigabytes',
    'snapshots': 'snapshots',
    'volumes': 'volumes',
}

IMPACT_VOLUME_TYPE_QUOTAS = [
    'gigabytes',
    'snapshots',
    'volumes',
]

NOVA_NETWORK_QUOTAS = {
    'floating_ips': 'floating-ips',
    'security_group_rules': 'secgroup-rules',
    'security_groups': 'secgroups',
}

NETWORK_QUOTAS = {
    'floatingip': 'floating-ips',
    'security_group_rule': 'secgroup-rules',
    'security_group': 'secgroups',
    'network': 'networks',
    'subnet': 'subnets',
    'port': 'ports',
    'router': 'routers',
    'rbac_policy': 'rbac-policies',
    'subnetpool': 'subnetpools',
}

NETWORK_KEYS = [
    'floating_ips',
    'networks',
    'rbac_policies',
    'routers',
    'ports',
    'security_group_rules',
    'security_groups',
    'subnet_pools',
    'subnets',
]


def _xform_get_quota(data, value, keys):
    res = []
    res_info = {}
    for key in keys:
        res_info[key] = getattr(data, key, '')

    res_info['id'] = value
    res.append(res_info)
    return res


def get_project(app, project):
    if project is not None:
        identity_client = app.client_manager.identity
        project = utils.find_resource(
            identity_client.projects,
            project,
        )
        project_id = project.id
        project_name = project.name
    elif app.client_manager.auth_ref:
        # Get the project from the current auth
        project = app.client_manager.auth_ref
        project_id = project.project_id
        project_name = project.project_name
    else:
        project_id = None
        project_name = None

    return {
        'id': project_id,
        'name': project_name,
    }


def get_compute_quotas(
    app,
    project_id,
    *,
    quota_class=False,
    detail=False,
    default=False,
):
    try:
        client = app.client_manager.compute
        if quota_class:
            # NOTE(stephenfin): The 'project' argument here could be anything
            # as the nova API doesn't care what you pass in. We only pass the
            # project in to avoid weirding people out :)
            quota = client.quota_classes.get(project_id)
        elif default:
            quota = client.quotas.defaults(project_id)
        else:
            quota = client.quotas.get(project_id, detail=detail)
    except Exception as e:
        if type(e).__name__ == 'EndpointNotFound':
            return {}
        raise
    return quota._info


def get_volume_quotas(
    app,
    project_id,
    *,
    quota_class=False,
    detail=False,
    default=False,
):
    try:
        client = app.client_manager.volume
        if quota_class:
            quota = client.quota_classes.get(project_id)
        elif default:
            quota = client.quotas.defaults(project_id)
        else:
            quota = client.quotas.get(project_id, usage=detail)
    except Exception as e:
        if type(e).__name__ == 'EndpointNotFound':
            return {}
        else:
            raise
    return quota._info


def get_network_quotas(
    app,
    project_id,
    *,
    quota_class=False,
    detail=False,
    default=False,
):
    def _network_quota_to_dict(network_quota, detail=False):
        if type(network_quota) is not dict:
            dict_quota = network_quota.to_dict()
        else:
            dict_quota = network_quota

        result = {}

        for key, values in dict_quota.items():
            if values is None:
                continue

            # NOTE(slaweq): Neutron returns values with key "used" but Nova for
            # example returns same data with key "in_use" instead. Because of
            # that we need to convert Neutron key to the same as is returned
            # from Nova to make result more consistent
            if isinstance(values, dict) and 'used' in values:
                values['in_use'] = values.pop("used")

            result[key] = values

        return result

    # neutron doesn't have the concept of quota classes and if we're using
    # nova-network we already fetched this
    if quota_class:
        return {}

    # we have nothing to return if we are not using neutron
    if not app.client_manager.is_network_endpoint_enabled():
        return {}

    client = app.client_manager.network
    if default:
        network_quota = client.get_quota_default(project_id)
        network_quota = _network_quota_to_dict(network_quota)
    else:
        network_quota = client.get_quota(project_id, details=detail)
        network_quota = _network_quota_to_dict(network_quota, detail=detail)
    return network_quota


class ListQuota(command.Lister):
    _description = _(
        "List quotas for all projects with non-default quota values or "
        "list detailed quota information for requested project"
    )

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        # TODO(stephenfin): Remove in OSC 8.0
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_(
                "**Deprecated** List quotas for this project <project> "
                "(name or ID). "
                "Use 'quota show' instead."
            ),
        )
        # TODO(stephenfin): Remove in OSC 8.0
        parser.add_argument(
            '--detail',
            dest='detail',
            action='store_true',
            default=False,
            help=_(
                "**Deprecated** Show details about quotas usage. "
                "Use 'quota show --usage' instead."
            ),
        )
        option = parser.add_mutually_exclusive_group(required=True)
        option.add_argument(
            '--compute',
            action='store_true',
            default=False,
            help=_('List compute quota'),
        )
        option.add_argument(
            '--volume',
            action='store_true',
            default=False,
            help=_('List volume quota'),
        )
        option.add_argument(
            '--network',
            action='store_true',
            default=False,
            help=_('List network quota'),
        )
        return parser

    def _get_detailed_quotas(self, parsed_args):
        project_info = get_project(self.app, parsed_args.project)
        project = project_info['id']

        quotas = {}

        if parsed_args.compute:
            quotas.update(
                get_compute_quotas(
                    self.app,
                    project,
                    detail=parsed_args.detail,
                )
            )

        if parsed_args.network:
            quotas.update(
                get_network_quotas(
                    self.app,
                    project,
                    detail=parsed_args.detail,
                )
            )

        if parsed_args.volume:
            quotas.update(
                get_volume_quotas(
                    self.app,
                    parsed_args,
                    detail=parsed_args.detail,
                ),
            )

        result = []
        for resource, values in quotas.items():
            # NOTE(slaweq): there is no detailed quotas info for some resources
            # and it shouldn't be displayed here
            if isinstance(values, dict):
                result.append(
                    {
                        'resource': resource,
                        'in_use': values.get('in_use'),
                        'reserved': values.get('reserved'),
                        'limit': values.get('limit'),
                    }
                )

        columns = (
            'resource',
            'in_use',
            'reserved',
            'limit',
        )
        column_headers = (
            'Resource',
            'In Use',
            'Reserved',
            'Limit',
        )

        return (
            column_headers,
            (utils.get_dict_properties(s, columns) for s in result),
        )

    def take_action(self, parsed_args):
        if parsed_args.detail:
            msg = _(
                "The --detail option has been deprecated. "
                "Use 'openstack quota show --usage' instead."
            )
            self.log.warning(msg)
        elif parsed_args.project:  # elif to avoid being too noisy
            msg = _(
                "The --project option has been deprecated. "
                "Use 'openstack quota show' instead."
            )
            self.log.warning(msg)

        result = []
        project_ids = []
        if parsed_args.project is None:
            for p in self.app.client_manager.identity.projects.list():
                project_ids.append(getattr(p, 'id', ''))
        else:
            identity_client = self.app.client_manager.identity
            project = utils.find_resource(
                identity_client.projects,
                parsed_args.project,
            )
            project_ids.append(getattr(project, 'id', ''))

        if parsed_args.compute:
            if parsed_args.detail:
                return self._get_detailed_quotas(parsed_args)

            compute_client = self.app.client_manager.compute
            for p in project_ids:
                try:
                    data = compute_client.quotas.get(p)
                except Exception as ex:
                    if (
                        type(ex).__name__ == 'NotFound'
                        or ex.http_status >= 400
                        and ex.http_status <= 499
                    ):
                        # Project not found, move on to next one
                        LOG.warning("Project %s not found: %s" % (p, ex))
                        continue
                    else:
                        raise

                result_data = _xform_get_quota(
                    data,
                    p,
                    COMPUTE_QUOTAS.keys(),
                )
                default_data = compute_client.quotas.defaults(p)
                result_default = _xform_get_quota(
                    default_data,
                    p,
                    COMPUTE_QUOTAS.keys(),
                )
                if result_default != result_data:
                    result += result_data

            columns = (
                'id',
                'cores',
                'fixed_ips',
                'injected_files',
                'injected_file_content_bytes',
                'injected_file_path_bytes',
                'instances',
                'key_pairs',
                'metadata_items',
                'ram',
                'server_groups',
                'server_group_members',
            )
            column_headers = (
                'Project ID',
                'Cores',
                'Fixed IPs',
                'Injected Files',
                'Injected File Content Bytes',
                'Injected File Path Bytes',
                'Instances',
                'Key Pairs',
                'Metadata Items',
                'Ram',
                'Server Groups',
                'Server Group Members',
            )
            return (
                column_headers,
                (utils.get_dict_properties(s, columns) for s in result),
            )

        if parsed_args.volume:
            if parsed_args.detail:
                return self._get_detailed_quotas(parsed_args)

            volume_client = self.app.client_manager.volume
            for p in project_ids:
                try:
                    data = volume_client.quotas.get(p)
                except Exception as ex:
                    if type(ex).__name__ == 'NotFound':
                        # Project not found, move on to next one
                        LOG.warning("Project %s not found: %s" % (p, ex))
                        continue
                    else:
                        raise

                result_data = _xform_get_quota(
                    data,
                    p,
                    VOLUME_QUOTAS.keys(),
                )
                default_data = volume_client.quotas.defaults(p)
                result_default = _xform_get_quota(
                    default_data,
                    p,
                    VOLUME_QUOTAS.keys(),
                )
                if result_default != result_data:
                    result += result_data

            columns = (
                'id',
                'backups',
                'backup_gigabytes',
                'gigabytes',
                'per_volume_gigabytes',
                'snapshots',
                'volumes',
            )
            column_headers = (
                'Project ID',
                'Backups',
                'Backup Gigabytes',
                'Gigabytes',
                'Per Volume Gigabytes',
                'Snapshots',
                'Volumes',
            )

            return (
                column_headers,
                (utils.get_dict_properties(s, columns) for s in result),
            )

        if parsed_args.network:
            if parsed_args.detail:
                return self._get_detailed_quotas(parsed_args)

            client = self.app.client_manager.network
            for p in project_ids:
                try:
                    data = client.get_quota(p)
                except Exception as ex:
                    if type(ex).__name__ == 'NotFound':
                        # Project not found, move on to next one
                        LOG.warning("Project %s not found: %s" % (p, ex))
                        continue
                    else:
                        raise

                result_data = _xform_get_quota(
                    data,
                    p,
                    NETWORK_KEYS,
                )
                default_data = client.get_quota_default(p)
                result_default = _xform_get_quota(
                    default_data,
                    p,
                    NETWORK_KEYS,
                )
                if result_default != result_data:
                    result += result_data

            columns = (
                'id',
                'floating_ips',
                'networks',
                'ports',
                'rbac_policies',
                'routers',
                'security_groups',
                'security_group_rules',
                'subnets',
                'subnet_pools',
            )
            column_headers = (
                'Project ID',
                'Floating IPs',
                'Networks',
                'Ports',
                'RBAC Policies',
                'Routers',
                'Security Groups',
                'Security Group Rules',
                'Subnets',
                'Subnet Pools',
            )

            return (
                column_headers,
                (utils.get_dict_properties(s, columns) for s in result),
            )

        return ((), ())


class SetQuota(common.NetDetectionMixin, command.Command):
    _description = _("Set quotas for project or class")

    def _build_options_list(self):
        help_fmt = _('New value for the %s quota')
        # Compute and volume quota options are always the same
        rets = [
            (k, v, help_fmt % v)
            for k, v in itertools.chain(
                COMPUTE_QUOTAS.items(),
                VOLUME_QUOTAS.items(),
            )
        ]
        # For docs build, we want to produce helps for both neutron and
        # nova-network options. They overlap, so we have to figure out which
        # need to be tagged as specific to one network type or the other.
        if self.is_docs_build:
            # NOTE(efried): This takes advantage of the fact that we know the
            # nova-net options are a subset of the neutron options. If that
            # ever changes, this algorithm will need to be adjusted accordingly
            inv_compute = set(NOVA_NETWORK_QUOTAS.values())
            for k, v in NETWORK_QUOTAS.items():
                _help = help_fmt % v
                if v not in inv_compute:
                    # This one is unique to neutron
                    _help = self.enhance_help_neutron(_help)
                rets.append((k, v, _help))
        elif self.is_neutron:
            rets.extend(
                [(k, v, help_fmt % v) for k, v in NETWORK_QUOTAS.items()]
            )
        elif self.is_nova_network:
            rets.extend(
                [(k, v, help_fmt % v) for k, v in NOVA_NETWORK_QUOTAS.items()]
            )
        return rets

    def get_parser(self, prog_name):
        parser = super(SetQuota, self).get_parser(prog_name)
        parser.add_argument(
            'project',
            metavar='<project/class>',
            help=_('Set quotas for this project or class (name or ID)'),
        )
        # TODO(stephenfin): Remove in OSC 8.0
        parser.add_argument(
            '--class',
            dest='quota_class',
            action='store_true',
            default=False,
            help=_(
                '**Deprecated** Set quotas for <class>. '
                'Deprecated as quota classes were never fully implemented '
                'and only the default class is supported. '
                '(compute and volume only)'
            ),
        )
        for k, v, h in self._build_options_list():
            parser.add_argument(
                '--%s' % v,
                metavar='<%s>' % v,
                dest=k,
                type=int,
                help=h,
            )
        parser.add_argument(
            '--volume-type',
            metavar='<volume-type>',
            help=_('Set quotas for a specific <volume-type>'),
        )
        force_group = parser.add_mutually_exclusive_group()
        force_group.add_argument(
            '--force',
            action='store_true',
            dest='force',
            # TODO(stephenfin): Change the default to False in Z or later
            default=None,
            help=_(
                'Force quota update (only supported by compute and network) '
                '(default for network)'
            ),
        )
        force_group.add_argument(
            '--no-force',
            action='store_false',
            dest='force',
            default=None,
            help=_(
                'Do not force quota update '
                '(only supported by compute and network) '
                '(default for compute)'
            ),
        )
        # kept here for backwards compatibility/to keep the neutron folks happy
        force_group.add_argument(
            '--check-limit',
            action='store_false',
            dest='force',
            default=None,
            help=argparse.SUPPRESS,
        )
        return parser

    def take_action(self, parsed_args):
        if parsed_args.quota_class:
            msg = _(
                "The '--class' option has been deprecated. Quota classes were "
                "never fully implemented and the compute and volume services "
                "only support a single 'default' quota class while the "
                "network service does not support quota classes at all. "
                "Please use 'openstack quota show --default' instead."
            )
            self.log.warning(msg)

        identity_client = self.app.client_manager.identity
        compute_client = self.app.client_manager.compute
        volume_client = self.app.client_manager.volume
        compute_kwargs = {}
        for k, v in COMPUTE_QUOTAS.items():
            value = getattr(parsed_args, k, None)
            if value is not None:
                compute_kwargs[k] = value

        if parsed_args.force is not None:
            compute_kwargs['force'] = parsed_args.force

        volume_kwargs = {}
        for k, v in VOLUME_QUOTAS.items():
            value = getattr(parsed_args, k, None)
            if value is not None:
                if parsed_args.volume_type and k in IMPACT_VOLUME_TYPE_QUOTAS:
                    k = k + '_%s' % parsed_args.volume_type
                volume_kwargs[k] = value

        network_kwargs = {}
        if parsed_args.force is True:
            # Unlike compute, network doesn't provide a simple boolean option.
            # Instead, it provides two options: 'force' and 'check_limit'
            # (a.k.a. 'not force')
            network_kwargs['force'] = True
        elif parsed_args.force is False:
            network_kwargs['check_limit'] = True
        else:
            msg = _(
                "This command currently defaults to '--force' when modifying "
                "network quotas. This behavior will change in a future "
                "release. Consider explicitly providing '--force' or "
                "'--no-force' options to avoid changes in behavior."
            )
            self.log.warning(msg)

        if self.app.client_manager.is_network_endpoint_enabled():
            for k, v in NETWORK_QUOTAS.items():
                value = getattr(parsed_args, k, None)
                if value is not None:
                    network_kwargs[k] = value
        else:
            for k, v in NOVA_NETWORK_QUOTAS.items():
                value = getattr(parsed_args, k, None)
                if value is not None:
                    compute_kwargs[k] = value

        if parsed_args.quota_class:
            if compute_kwargs:
                compute_client.quota_classes.update(
                    parsed_args.project,
                    **compute_kwargs,
                )
            if volume_kwargs:
                volume_client.quota_classes.update(
                    parsed_args.project,
                    **volume_kwargs,
                )
            if network_kwargs:
                sys.stderr.write(
                    "Network quotas are ignored since quota classes are not "
                    "supported."
                )
        else:
            project = utils.find_resource(
                identity_client.projects,
                parsed_args.project,
            ).id

            if compute_kwargs:
                compute_client.quotas.update(project, **compute_kwargs)
            if volume_kwargs:
                volume_client.quotas.update(project, **volume_kwargs)
            if (
                network_kwargs
                and self.app.client_manager.is_network_endpoint_enabled()
            ):
                network_client = self.app.client_manager.network
                network_client.update_quota(project, **network_kwargs)


class ShowQuota(command.Lister):
    _description = _(
        """Show quotas for project or class.

Specify ``--os-compute-api-version 2.50`` or higher to see ``server-groups``
and ``server-group-members`` output for a given quota class."""
    )

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'project',
            metavar='<project/class>',
            nargs='?',
            help=_(
                'Show quotas for this project or class (name or ID) '
                '(defaults to current project)'
            ),
        )
        type_group = parser.add_mutually_exclusive_group()
        # TODO(stephenfin): Remove in OSC 8.0
        type_group.add_argument(
            '--class',
            dest='quota_class',
            action='store_true',
            default=False,
            help=_(
                '**Deprecated** Show quotas for <class>. '
                'Deprecated as quota classes were never fully implemented '
                'and only the default class is supported. '
                'Use --default instead which is also supported by the network '
                'service. '
                '(compute and volume only)'
            ),
        )
        type_group.add_argument(
            '--default',
            dest='default',
            action='store_true',
            default=False,
            help=_('Show default quotas for <project>'),
        )
        type_group.add_argument(
            '--usage',
            dest='usage',
            action='store_true',
            default=False,
            help=_('Show details about quotas usage'),
        )
        service_group = parser.add_mutually_exclusive_group()
        service_group.add_argument(
            '--all',
            action='store_const',
            const='all',
            dest='service',
            default='all',
            help=_('Show quotas for all services'),
        )
        service_group.add_argument(
            '--compute',
            action='store_const',
            const='compute',
            dest='service',
            default='all',
            help=_('Show compute quota'),
        )
        service_group.add_argument(
            '--volume',
            action='store_const',
            const='volume',
            dest='service',
            default='all',
            help=_('Show volume quota'),
        )
        service_group.add_argument(
            '--network',
            action='store_const',
            const='network',
            dest='service',
            default='all',
            help=_('Show network quota'),
        )

        return parser

    def take_action(self, parsed_args):
        project = parsed_args.project

        if parsed_args.quota_class:
            msg = _(
                "The '--class' option has been deprecated. Quota classes were "
                "never fully implemented and the compute and volume services "
                "only support a single 'default' quota class while the "
                "network service does not support quota classes at all. "
                "Please use 'openstack quota show --default' instead."
            )
            self.log.warning(msg)
        else:
            project_info = get_project(self.app, parsed_args.project)
            project = project_info['id']

        compute_quota_info = {}
        volume_quota_info = {}
        network_quota_info = {}

        # NOTE(stephenfin): These quota API calls do not validate the project
        # or class arguments and return what appears to be the default quota
        # values if the project or class does not exist. This is expected
        # behavior. However, we have already checked for the presence of the
        # project above so it shouldn't be an issue.
        if parsed_args.service in {'all', 'compute'}:
            compute_quota_info = get_compute_quotas(
                self.app,
                project,
                detail=parsed_args.usage,
                quota_class=parsed_args.quota_class,
                default=parsed_args.default,
            )
        if parsed_args.service in {'all', 'volume'}:
            volume_quota_info = get_volume_quotas(
                self.app,
                project,
                detail=parsed_args.usage,
                quota_class=parsed_args.quota_class,
                default=parsed_args.default,
            )
        if parsed_args.service in {'all', 'network'}:
            network_quota_info = get_network_quotas(
                self.app,
                project,
                detail=parsed_args.usage,
                quota_class=parsed_args.quota_class,
                default=parsed_args.default,
            )

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
            COMPUTE_QUOTAS.items(),
            NOVA_NETWORK_QUOTAS.items(),
            VOLUME_QUOTAS.items(),
            NETWORK_QUOTAS.items(),
        ):
            if not k == v and info.get(k) is not None:
                info[v] = info[k]
                info.pop(k)

        # Remove the 'id' field since it's not very useful
        if 'id' in info:
            del info['id']

        # Remove the 'location' field for resources from openstacksdk
        if 'location' in info:
            del info['location']

        if not parsed_args.usage:
            result = [{'resource': k, 'limit': v} for k, v in info.items()]
        else:
            result = [{'resource': k, **v} for k, v in info.items()]

        columns = (
            'resource',
            'limit',
        )
        column_headers = (
            'Resource',
            'Limit',
        )

        if parsed_args.usage:
            columns += (
                'in_use',
                'reserved',
            )
            column_headers += (
                'In Use',
                'Reserved',
            )

        return (
            column_headers,
            (utils.get_dict_properties(s, columns) for s in result),
        )


class DeleteQuota(command.Command):
    _description = _(
        "Delete configured quota for a project and revert to defaults."
    )

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'project',
            metavar='<project>',
            help=_('Delete quotas for this project (name or ID)'),
        )
        option = parser.add_mutually_exclusive_group()
        option.add_argument(
            '--all',
            action='store_const',
            const='all',
            dest='service',
            default='all',
            help=_('Delete project quotas for all services (default)'),
        )
        option.add_argument(
            '--compute',
            action='store_const',
            const='compute',
            dest='service',
            default='all',
            help=_(
                'Delete compute quotas for the project '
                '(including network quotas when using nova-network)'
            ),
        )
        option.add_argument(
            '--volume',
            action='store_const',
            const='volume',
            dest='service',
            default='all',
            help=_('Delete volume quotas for the project'),
        )
        option.add_argument(
            '--network',
            action='store_const',
            const='network',
            dest='service',
            default='all',
            help=_('Delete network quotas for the project'),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        project = utils.find_resource(
            identity_client.projects,
            parsed_args.project,
        )

        # compute quotas
        if parsed_args.service in {'all', 'compute'}:
            compute_client = self.app.client_manager.compute
            compute_client.quotas.delete(project.id)

        # volume quotas
        if parsed_args.service in {'all', 'volume'}:
            volume_client = self.app.client_manager.volume
            volume_client.quotas.delete(project.id)

        # network quotas (but only if we're not using nova-network, otherwise
        # we already deleted the quotas in the compute step)
        if (
            parsed_args.service in {'all', 'network'}
            and self.app.client_manager.is_network_endpoint_enabled()
        ):
            network_client = self.app.client_manager.network
            network_client.delete_quota(project.id)

        return None
