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

"""Quota action implementations"""

import argparse
import itertools
import logging
import sys
import typing as ty

from openstack import exceptions as sdk_exceptions
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _
from openstackclient.network import common

LOG = logging.getLogger(__name__)

# List the quota items, map the internal argument name to the option
# name that the user sees.

COMPUTE_QUOTAS = {
    'cores': 'cores',
    'injected_file_content_bytes': 'injected-file-size',
    'injected_file_path_bytes': 'injected-path-size',
    'injected_files': 'injected-files',
    'instances': 'instances',
    'key_pairs': 'key-pairs',
    'metadata_items': 'properties',
    'ram': 'ram',
    'server_group_members': 'server-group-members',
    'server_groups': 'server-groups',
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
    'fixed_ips': 'fixed-ips',
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
        identity_client = app.client_manager.sdk_connection.identity
        project = identity_client.find_project(project, ignore_missing=False)
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
    detail=False,
    default=False,
):
    try:
        client = app.client_manager.compute
        if default:
            quota = client.get_quota_set_defaults(project_id)
        else:
            quota = client.get_quota_set(project_id, usage=detail)
    except sdk_exceptions.EndpointNotFound:
        return {}
    data = quota.to_dict()
    if not detail:
        del data['usage']
        del data['reservation']
    return data


def get_volume_quotas(
    app,
    project_id,
    *,
    detail=False,
    default=False,
):
    try:
        client = app.client_manager.sdk_connection.volume
        if default:
            quota = client.get_quota_set_defaults(project_id)
        else:
            quota = client.get_quota_set(project_id, usage=detail)
    except sdk_exceptions.EndpointNotFound:
        return {}
    data = quota.to_dict()
    if not detail:
        del data['usage']
        del data['reservation']
    return data


def get_network_quotas(
    app,
    project_id,
    *,
    detail=False,
    default=False,
):
    def _network_quota_to_dict(network_quota, detail=False):
        dict_quota = network_quota.to_dict(computed=False)

        if not detail:
            return dict_quota

        # Neutron returns quota details in dict which is in format like:
        # {'resource_name': {'in_use': X, 'limit': Y, 'reserved': Z},
        #  'resource_name_2': {'in_use': X2, 'limit': Y2, 'reserved': Z2}}
        #
        # but Nova and Cinder returns quota in different format, like:
        # {'resource_name': X,
        #  'resource_name_2': X2,
        #  'usage': {
        #     'resource_name': Y,
        #     'resource_name_2': Y2
        #  },
        #  'reserved': {
        #     'resource_name': Z,
        #     'resource_name_2': Z2
        #  }}
        #
        # so we need to make conversion to have data in same format from
        # all of the services
        result: dict[str, ty.Any] = {"usage": {}, "reservation": {}}
        for key, values in dict_quota.items():
            if values is None:
                continue
            if isinstance(values, dict):
                result[key] = values['limit']
                result["reservation"][key] = values['reserved']
                result["usage"][key] = values['used']

        return result

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
    """List quotas for all projects with non-default quota values.

    Empty output means all projects are using default quotas, which can be
    inspected with 'openstack quota show --default'.
    """

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
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

    def _list_quota_compute(self, parsed_args, project_ids):
        compute_client = self.app.client_manager.compute
        result = []

        for project_id in project_ids:
            try:
                project_data = compute_client.get_quota_set(project_id)
            # NOTE(stephenfin): Unfortunately, Nova raises a HTTP 400 (Bad
            # Request) if the project ID is invalid, even though the project
            # ID is actually the resource's identifier which would normally
            # lead us to expect a HTTP 404 (Not Found).
            except (
                sdk_exceptions.BadRequestException,
                sdk_exceptions.ForbiddenException,
                sdk_exceptions.NotFoundException,
            ) as exc:
                # Project not found, move on to next one
                LOG.warning(f"Project {project_id} not found: {exc}")
                continue

            project_result = _xform_get_quota(
                project_data,
                project_id,
                COMPUTE_QUOTAS.keys(),
            )

            default_data = compute_client.get_quota_set_defaults(project_id)
            default_result = _xform_get_quota(
                default_data,
                project_id,
                COMPUTE_QUOTAS.keys(),
            )

            if default_result != project_result:
                result += project_result

        columns: tuple[str, ...] = (
            'id',
            'cores',
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
        column_headers: tuple[str, ...] = (
            'Project ID',
            'Cores',
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

    def _list_quota_volume(self, parsed_args, project_ids):
        volume_client = self.app.client_manager.sdk_connection.volume
        result = []

        for project_id in project_ids:
            try:
                project_data = volume_client.get_quota_set(project_id)
            except (
                sdk_exceptions.ForbiddenException,
                sdk_exceptions.NotFoundException,
            ) as exc:
                # Project not found, move on to next one
                LOG.warning(f"Project {project_id} not found: {exc}")
                continue

            project_result = _xform_get_quota(
                project_data,
                project_id,
                VOLUME_QUOTAS.keys(),
            )

            default_data = volume_client.get_quota_set_defaults(project_id)
            default_result = _xform_get_quota(
                default_data,
                project_id,
                VOLUME_QUOTAS.keys(),
            )

            if default_result != project_result:
                result += project_result

        columns: tuple[str, ...] = (
            'id',
            'backups',
            'backup_gigabytes',
            'gigabytes',
            'per_volume_gigabytes',
            'snapshots',
            'volumes',
        )
        column_headers: tuple[str, ...] = (
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

    def _list_quota_network(self, parsed_args, project_ids):
        network_client = self.app.client_manager.network
        result = []

        for project_id in project_ids:
            try:
                project_data = network_client.get_quota(project_id)
            except (
                sdk_exceptions.NotFoundException,
                sdk_exceptions.ForbiddenException,
            ) as exc:
                # Project not found, move on to next one
                LOG.warning(f"Project {project_id} not found: {exc}")
                continue

            project_result = _xform_get_quota(
                project_data,
                project_id,
                NETWORK_KEYS,
            )

            default_data = network_client.get_quota_default(project_id)
            default_result = _xform_get_quota(
                default_data,
                project_id,
                NETWORK_KEYS,
            )

            if default_result != project_result:
                result += project_result

        columns: tuple[str, ...] = (
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
        column_headers: tuple[str, ...] = (
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

    def take_action(self, parsed_args):
        project_ids = [
            p.id
            for p in self.app.client_manager.sdk_connection.identity.projects()
        ]
        if parsed_args.compute:
            return self._list_quota_compute(parsed_args, project_ids)
        elif parsed_args.volume:
            return self._list_quota_volume(parsed_args, project_ids)
        elif parsed_args.network:
            return self._list_quota_network(parsed_args, project_ids)

        # will never get here
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
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'project',
            metavar='<project/class>',
            nargs='?',
            help=_(
                'Set quotas for this project or class (name or ID) '
                '(defaults to current project)'
            ),
        )
        # TODO(stephenfin): Remove in OSC 8.0
        type_group = parser.add_mutually_exclusive_group()
        type_group.add_argument(
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
        type_group.add_argument(
            '--default',
            dest='default',
            action='store_true',
            default=False,
            help=_('Set default quotas for <project>'),
        )
        for k, v, h in self._build_options_list():
            parser.add_argument(
                f'--{v}',
                metavar=f'<{v}>',
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
            default=False,
            help=_(
                'Force quota update (only supported by compute and network)'
            ),
        )
        force_group.add_argument(
            '--no-force',
            action='store_false',
            dest='force',
            default=False,
            help=_(
                'Do not force quota update '
                '(only supported by compute and network) (default)'
            ),
        )
        # kept here for backwards compatibility/to keep the neutron folks happy
        force_group.add_argument(
            '--check-limit',
            action='store_false',
            dest='force',
            default=False,
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
                "Please use 'openstack quota set --default' instead."
            )
            self.log.warning(msg)

        if (
            parsed_args.quota_class or parsed_args.default
        ) and parsed_args.force:
            msg = _('--force cannot be used with --class or --default')
            raise exceptions.CommandError(msg)

        compute_kwargs = {}
        volume_kwargs = {}
        network_kwargs = {}

        if self.app.client_manager.is_compute_endpoint_enabled():
            compute_client = self.app.client_manager.compute

            for k, v in COMPUTE_QUOTAS.items():
                value = getattr(parsed_args, k, None)
                if value is not None:
                    compute_kwargs[k] = value

            if compute_kwargs and parsed_args.force is True:
                compute_kwargs['force'] = parsed_args.force

        if self.app.client_manager.is_volume_endpoint_enabled():
            volume_client = self.app.client_manager.sdk_connection.volume

            for k, v in VOLUME_QUOTAS.items():
                value = getattr(parsed_args, k, None)
                if value is not None:
                    if (
                        parsed_args.volume_type
                        and k in IMPACT_VOLUME_TYPE_QUOTAS
                    ):
                        k = k + f'_{parsed_args.volume_type}'
                    volume_kwargs[k] = value

        if self.app.client_manager.is_network_endpoint_enabled():
            network_client = self.app.client_manager.network

            for k, v in NETWORK_QUOTAS.items():
                value = getattr(parsed_args, k, None)
                if value is not None:
                    network_kwargs[k] = value
        elif self.app.client_manager.is_compute_endpoint_enabled():
            for k, v in NOVA_NETWORK_QUOTAS.items():
                value = getattr(parsed_args, k, None)
                if value is not None:
                    compute_kwargs[k] = value

        if network_kwargs:
            if parsed_args.force is True:
                # Unlike compute, network doesn't provide a simple boolean
                # option. Instead, it provides two options: 'force' and
                # 'check_limit' (a.k.a. 'not force')
                network_kwargs['force'] = True
            else:
                network_kwargs['check_limit'] = True

        if parsed_args.quota_class or parsed_args.default:
            if compute_kwargs:
                compute_client.update_quota_class_set(
                    parsed_args.project or 'default',
                    **compute_kwargs,
                )
            if volume_kwargs:
                volume_client.update_quota_class_set(
                    parsed_args.project or 'default',
                    **volume_kwargs,
                )
            if network_kwargs:
                sys.stderr.write(
                    "Network quotas are ignored since quota classes are not "
                    "supported."
                )

            return

        project_info = get_project(self.app, parsed_args.project)
        project = project_info['id']

        if compute_kwargs:
            compute_client.update_quota_set(project, **compute_kwargs)
        if volume_kwargs:
            volume_client.update_quota_set(project, **volume_kwargs)
        if network_kwargs:
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
            metavar='<project>',
            nargs='?',
            help=_(
                'Show quotas for this project (name or ID) '
                '(defaults to current project)'
            ),
        )
        type_group = parser.add_mutually_exclusive_group()
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
                default=parsed_args.default,
            )
        if parsed_args.service in {'all', 'volume'}:
            volume_quota_info = get_volume_quotas(
                self.app,
                project,
                detail=parsed_args.usage,
                default=parsed_args.default,
            )
        if parsed_args.service in {'all', 'network'}:
            network_quota_info = get_network_quotas(
                self.app,
                project,
                detail=parsed_args.usage,
                default=parsed_args.default,
            )

        info = {}
        if parsed_args.usage:
            info["reservation"] = compute_quota_info.pop("reservation", {})
            info["reservation"].update(
                volume_quota_info.pop("reservation", {})
            )
            info["reservation"].update(
                network_quota_info.pop("reservation", {})
            )

            info["usage"] = compute_quota_info.pop("usage", {})
            info["usage"].update(volume_quota_info.pop("usage", {}))
            info["usage"].update(network_quota_info.pop("usage", {}))

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

        # Remove the sdk-derived fields
        for field in ('location', 'name', 'force'):
            if field in info:
                del info[field]

        if not parsed_args.usage:
            result = [{'resource': k, 'limit': v} for k, v in info.items()]
        else:
            result = [
                {
                    'resource': k,
                    'limit': v or 0,
                    'in_use': info['usage'].get(k, 0),
                    'reserved': info['reservation'].get(k, 0),
                }
                for k, v in info.items()
                if k not in ('usage', 'reservation')
            ]

        columns: tuple[str, ...] = (
            'resource',
            'limit',
        )
        column_headers: tuple[str, ...] = (
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
        identity_client = self.app.client_manager.sdk_connection.identity
        project = identity_client.find_project(
            parsed_args.project, ignore_missing=False
        )

        # compute quotas
        if parsed_args.service in {'all', 'compute'}:
            compute_client = self.app.client_manager.compute
            compute_client.revert_quota_set(project.id)

        # volume quotas
        if parsed_args.service in {'all', 'volume'}:
            volume_client = self.app.client_manager.sdk_connection.volume
            volume_client.revert_quota_set(project.id)

        # network quotas (but only if we're not using nova-network, otherwise
        # we already deleted the quotas in the compute step)
        if (
            parsed_args.service in {'all', 'network'}
            and self.app.client_manager.is_network_endpoint_enabled()
        ):
            network_client = self.app.client_manager.network
            network_client.delete_quota(project.id)

        return None
