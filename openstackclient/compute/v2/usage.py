#   Copyright 2013 OpenStack Foundation.
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

"""Usage action implementations"""

import collections
import datetime

from novaclient import api_versions
from osc_lib.command import command
from osc_lib import utils
import six

from openstackclient.i18n import _


def _get_usage_marker(usage):
    marker = None
    if hasattr(usage, 'server_usages') and usage.server_usages:
        marker = usage.server_usages[-1]['instance_id']
    return marker


def _get_usage_list_marker(usage_list):
    marker = None
    if usage_list:
        marker = _get_usage_marker(usage_list[-1])
    return marker


def _merge_usage(usage, next_usage):
    usage.server_usages.extend(next_usage.server_usages)
    usage.total_hours += next_usage.total_hours
    usage.total_memory_mb_usage += next_usage.total_memory_mb_usage
    usage.total_vcpus_usage += next_usage.total_vcpus_usage
    usage.total_local_gb_usage += next_usage.total_local_gb_usage


def _merge_usage_list(usages, next_usage_list):
    for next_usage in next_usage_list:
        if next_usage.tenant_id in usages:
            _merge_usage(usages[next_usage.tenant_id], next_usage)
        else:
            usages[next_usage.tenant_id] = next_usage


class ListUsage(command.Lister):
    _description = _("List resource usage per project")

    def get_parser(self, prog_name):
        parser = super(ListUsage, self).get_parser(prog_name)
        parser.add_argument(
            "--start",
            metavar="<start>",
            default=None,
            help=_("Usage range start date, ex 2012-01-20"
                   " (default: 4 weeks ago)")
        )
        parser.add_argument(
            "--end",
            metavar="<end>",
            default=None,
            help=_("Usage range end date, ex 2012-01-20 (default: tomorrow)")
        )
        return parser

    def take_action(self, parsed_args):

        def _format_project(project):
            if not project:
                return ""
            if project in project_cache.keys():
                return project_cache[project].name
            else:
                return project

        compute_client = self.app.client_manager.compute
        columns = (
            "tenant_id",
            "server_usages",
            "total_memory_mb_usage",
            "total_vcpus_usage",
            "total_local_gb_usage"
        )
        column_headers = (
            "Project",
            "Servers",
            "RAM MB-Hours",
            "CPU Hours",
            "Disk GB-Hours"
        )

        dateformat = "%Y-%m-%d"
        now = datetime.datetime.utcnow()

        if parsed_args.start:
            start = datetime.datetime.strptime(parsed_args.start, dateformat)
        else:
            start = now - datetime.timedelta(weeks=4)

        if parsed_args.end:
            end = datetime.datetime.strptime(parsed_args.end, dateformat)
        else:
            end = now + datetime.timedelta(days=1)

        if compute_client.api_version < api_versions.APIVersion("2.40"):
            usage_list = compute_client.usage.list(start, end, detailed=True)
        else:
            # If the number of instances used to calculate the usage is greater
            # than CONF.api.max_limit, the usage will be split across multiple
            # requests and the responses will need to be merged back together.
            usages = collections.OrderedDict()
            usage_list = compute_client.usage.list(start, end, detailed=True)
            _merge_usage_list(usages, usage_list)
            marker = _get_usage_list_marker(usage_list)
            while marker:
                next_usage_list = compute_client.usage.list(
                    start, end, detailed=True, marker=marker)
                marker = _get_usage_list_marker(next_usage_list)
                if marker:
                    _merge_usage_list(usages, next_usage_list)
            usage_list = list(usages.values())

        # Cache the project list
        project_cache = {}
        try:
            for p in self.app.client_manager.identity.projects.list():
                project_cache[p.id] = p
        except Exception:
            # Just forget it if there's any trouble
            pass

        if parsed_args.formatter == 'table' and len(usage_list) > 0:
            self.app.stdout.write(_("Usage from %(start)s to %(end)s: \n") % {
                "start": start.strftime(dateformat),
                "end": end.strftime(dateformat),
            })

        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                    formatters={
                        'tenant_id': _format_project,
                        'server_usages': lambda x: len(x),
                        'total_memory_mb_usage': lambda x: float("%.2f" % x),
                        'total_vcpus_usage': lambda x: float("%.2f" % x),
                        'total_local_gb_usage': lambda x: float("%.2f" % x),
                    },
                ) for s in usage_list))


class ShowUsage(command.ShowOne):
    _description = _("Show resource usage for a single project")

    def get_parser(self, prog_name):
        parser = super(ShowUsage, self).get_parser(prog_name)
        parser.add_argument(
            "--project",
            metavar="<project>",
            default=None,
            help=_("Name or ID of project to show usage for")
        )
        parser.add_argument(
            "--start",
            metavar="<start>",
            default=None,
            help=_("Usage range start date, ex 2012-01-20"
                   " (default: 4 weeks ago)")
        )
        parser.add_argument(
            "--end",
            metavar="<end>",
            default=None,
            help=_("Usage range end date, ex 2012-01-20 (default: tomorrow)")
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        compute_client = self.app.client_manager.compute
        dateformat = "%Y-%m-%d"
        now = datetime.datetime.utcnow()

        if parsed_args.start:
            start = datetime.datetime.strptime(parsed_args.start, dateformat)
        else:
            start = now - datetime.timedelta(weeks=4)

        if parsed_args.end:
            end = datetime.datetime.strptime(parsed_args.end, dateformat)
        else:
            end = now + datetime.timedelta(days=1)

        if parsed_args.project:
            project = utils.find_resource(
                identity_client.projects,
                parsed_args.project,
            ).id
        else:
            # Get the project from the current auth
            project = self.app.client_manager.auth_ref.project_id

        usage = compute_client.usage.get(project, start, end)

        if parsed_args.formatter == 'table':
            self.app.stdout.write(_(
                "Usage from %(start)s to %(end)s on project %(project)s: \n"
            ) % {
                "start": start.strftime(dateformat),
                "end": end.strftime(dateformat),
                "project": project,
            })

        info = {}
        info['Servers'] = (
            len(usage.server_usages)
            if hasattr(usage, "server_usages") else None)
        info['RAM MB-Hours'] = (
            float("%.2f" % usage.total_memory_mb_usage)
            if hasattr(usage, "total_memory_mb_usage") else None)
        info['CPU Hours'] = (
            float("%.2f" % usage.total_vcpus_usage)
            if hasattr(usage, "total_vcpus_usage") else None)
        info['Disk GB-Hours'] = (
            float("%.2f" % usage.total_local_gb_usage)
            if hasattr(usage, "total_local_gb_usage") else None)
        return zip(*sorted(six.iteritems(info)))
