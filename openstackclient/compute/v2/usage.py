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

import datetime
import functools

from cliff import columns as cliff_columns
from osc_lib.command import command
from osc_lib import utils

from openstackclient.i18n import _


# TODO(stephenfin): This exists in a couple of places and should be moved to a
# common module
class ProjectColumn(cliff_columns.FormattableColumn):
    """Formattable column for project column.

    Unlike the parent FormattableColumn class, the initializer of the class
    takes project_cache as the second argument.
    ``osc_lib.utils.get_item_properties`` instantiates ``FormattableColumn``
    objects with a single parameter, the column value, so you need to pass a
    partially initialized class like ``functools.partial(ProjectColumn,
    project_cache)`` to use this.
    """

    def __init__(self, value, project_cache=None):
        super().__init__(value)
        self.project_cache = project_cache or {}

    def human_readable(self):
        project = self._value
        if not project:
            return ''

        if project in self.project_cache.keys():
            return self.project_cache[project].name

        return project


class CountColumn(cliff_columns.FormattableColumn):
    def human_readable(self):
        return len(self._value) if self._value is not None else None


class FloatColumn(cliff_columns.FormattableColumn):
    def human_readable(self):
        return float(f"{self._value:.2f}")


def _formatters(project_cache):
    return {
        'project_id': functools.partial(
            ProjectColumn, project_cache=project_cache
        ),
        'server_usages': CountColumn,
        'total_memory_mb_usage': FloatColumn,
        'total_vcpus_usage': FloatColumn,
        'total_local_gb_usage': FloatColumn,
    }


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
        if next_usage.project_id in usages:
            _merge_usage(usages[next_usage.project_id], next_usage)
        else:
            usages[next_usage.project_id] = next_usage


class ListUsage(command.Lister):
    _description = _("List resource usage per project")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "--start",
            metavar="<start>",
            default=None,
            help=_(
                "Usage range start date, ex 2012-01-20 (default: 4 weeks ago)"
            ),
        )
        parser.add_argument(
            "--end",
            metavar="<end>",
            default=None,
            help=_("Usage range end date, ex 2012-01-20 (default: tomorrow)"),
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
            "project_id",
            "server_usages",
            "total_memory_mb_usage",
            "total_vcpus_usage",
            "total_local_gb_usage",
        )
        column_headers = (
            "Project",
            "Servers",
            "RAM MB-Hours",
            "CPU Hours",
            "Disk GB-Hours",
        )

        date_cli_format = "%Y-%m-%d"
        now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)

        if parsed_args.start:
            start = datetime.datetime.strptime(
                parsed_args.start, date_cli_format
            )
        else:
            start = now - datetime.timedelta(weeks=4)

        if parsed_args.end:
            end = datetime.datetime.strptime(parsed_args.end, date_cli_format)
        else:
            end = now + datetime.timedelta(days=1)

        usage_list = list(
            compute_client.usages(
                start=start,
                end=end,
                detailed=True,
            )
        )

        # Cache the project list
        project_cache = {}
        try:
            for p in self.app.client_manager.identity.projects.list():
                project_cache[p.id] = p
        except Exception:  # noqa: S110
            # Just forget it if there's any trouble
            pass

        if parsed_args.formatter == 'table' and len(usage_list) > 0:
            self.app.stdout.write(
                _("Usage from %(start)s to %(end)s: \n")
                % {
                    "start": start.strftime(date_cli_format),
                    "end": end.strftime(date_cli_format),
                }
            )

        return (
            column_headers,
            (
                utils.get_item_properties(
                    s,
                    columns,
                    formatters=_formatters(project_cache),
                )
                for s in usage_list
            ),
        )


class ShowUsage(command.ShowOne):
    _description = _("Show resource usage for a single project")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "--project",
            metavar="<project>",
            default=None,
            help=_("Name or ID of project to show usage for"),
        )
        parser.add_argument(
            "--start",
            metavar="<start>",
            default=None,
            help=_(
                "Usage range start date, ex 2012-01-20 (default: 4 weeks ago)"
            ),
        )
        parser.add_argument(
            "--end",
            metavar="<end>",
            default=None,
            help=_("Usage range end date, ex 2012-01-20 (default: tomorrow)"),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        compute_client = self.app.client_manager.compute
        date_cli_format = "%Y-%m-%d"
        now = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)

        if parsed_args.start:
            start = datetime.datetime.strptime(
                parsed_args.start, date_cli_format
            )
        else:
            start = now - datetime.timedelta(weeks=4)

        if parsed_args.end:
            end = datetime.datetime.strptime(parsed_args.end, date_cli_format)
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

        usage = compute_client.get_usage(
            project=project,
            start=start,
            end=end,
        )

        if parsed_args.formatter == 'table':
            self.app.stdout.write(
                _("Usage from %(start)s to %(end)s on project %(project)s: \n")
                % {
                    "start": start.strftime(date_cli_format),
                    "end": end.strftime(date_cli_format),
                    "project": project,
                }
            )

        columns = (
            "project_id",
            "server_usages",
            "total_memory_mb_usage",
            "total_vcpus_usage",
            "total_local_gb_usage",
        )
        column_headers = (
            "Project",
            "Servers",
            "RAM MB-Hours",
            "CPU Hours",
            "Disk GB-Hours",
        )

        data = utils.get_item_properties(
            usage, columns, formatters=_formatters(None)
        )
        return column_headers, data
