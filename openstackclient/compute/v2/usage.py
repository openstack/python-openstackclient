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
import logging
import sys

from cliff import lister
from cliff import show
import six

from openstackclient.common import utils


class ListUsage(lister.Lister):
    """List resource usage per project"""

    log = logging.getLogger(__name__ + ".ListUsage")

    def get_parser(self, prog_name):
        parser = super(ListUsage, self).get_parser(prog_name)
        parser.add_argument(
            "--start",
            metavar="<start>",
            default=None,
            help="Usage range start date, ex 2012-01-20"
                 " (default: 4 weeks ago)"
        )
        parser.add_argument(
            "--end",
            metavar="<end>",
            default=None,
            help="Usage range end date, ex 2012-01-20 (default: tomorrow)"
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

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

        usage_list = compute_client.usage.list(start, end, detailed=True)

        # Cache the project list
        project_cache = {}
        try:
            for p in self.app.client_manager.identity.tenants.list():
                project_cache[p.id] = p
        except Exception:
            # Just forget it if there's any trouble
            pass

        if parsed_args.formatter == 'table' and len(usage_list) > 0:
            sys.stdout.write("Usage from %s to %s: \n" % (
                start.strftime(dateformat),
                end.strftime(dateformat),
            ))

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


class ShowUsage(show.ShowOne):
    """Show resource usage for a single project"""

    log = logging.getLogger(__name__ + ".ShowUsage")

    def get_parser(self, prog_name):
        parser = super(ShowUsage, self).get_parser(prog_name)
        parser.add_argument(
            "--project",
            metavar="<project>",
            default=None,
            help="Name or ID of project to show usage for"
        )
        parser.add_argument(
            "--start",
            metavar="<start>",
            default=None,
            help="Usage range start date, ex 2012-01-20"
                 " (default: 4 weeks ago)"
        )
        parser.add_argument(
            "--end",
            metavar="<end>",
            default=None,
            help="Usage range end date, ex 2012-01-20 (default: tomorrow)"
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

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
            sys.stdout.write("Usage from %s to %s on project %s: \n" % (
                start.strftime(dateformat),
                end.strftime(dateformat),
                project
            ))

        info = {}
        info['Servers'] = len(usage.server_usages)
        info['RAM MB-Hours'] = float("%.2f" % usage.total_memory_mb_usage)
        info['CPU Hours'] = float("%.2f" % usage.total_vcpus_usage)
        info['Disk GB-Hours'] = float("%.2f" % usage.total_local_gb_usage)
        return zip(*sorted(six.iteritems(info)))


# This is out of order due to the subclass, will eventually be removed

class ListProjectUsage(ListUsage):
    """List resource usage per project"""

    deprecated = True

    log = logging.getLogger('DEPRECATED:')

    def take_action(self, parsed_args):
        self.log.warning(
            "%s is deprecated, use 'usage list'",
            getattr(self, 'cmd_name', 'this command'),
        )
        return super(ListProjectUsage, self).take_action(parsed_args)
