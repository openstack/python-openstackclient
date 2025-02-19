#   Copyright 2012-2013 OpenStack Foundation
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

"""Image V2 Action Implementations"""

import logging

from osc_lib.cli import format_columns
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _

_formatters = {
    'tags': format_columns.ListColumn,
}

LOG = logging.getLogger(__name__)


def _format_namespace(namespace):
    info = {}

    fields_to_show = [
        'created_at',
        'description',
        'display_name',
        'namespace',
        'owner',
        'protected',
        'schema',
        'updated_at',
        'visibility',
    ]

    namespace = namespace.to_dict(ignore_none=True, original_names=True)

    # split out the usual key and the properties which are top-level
    for key in namespace:
        if key in fields_to_show:
            info[key] = namespace.get(key)
        elif key == "resource_type_associations":
            info[key] = [
                resource_type['name'] for resource_type in namespace.get(key)
            ]
        elif key == 'properties':
            info['properties'] = list(namespace.get(key).keys())

    return info


class CreateMetadefNamespace(command.ShowOne):
    _description = _("Create a metadef namespace")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "namespace",
            metavar="<namespace>",
            help=_("New metadef namespace name"),
        )
        parser.add_argument(
            "--display-name",
            metavar="<display_name>",
            help=_("A user-friendly name for the namespace."),
        )
        parser.add_argument(
            "--description",
            metavar="<description>",
            help=_("A description of the namespace"),
        )
        visibility_group = parser.add_mutually_exclusive_group()
        visibility_group.add_argument(
            "--public",
            action="store_const",
            const="public",
            dest="visibility",
            help=_("Set namespace visibility 'public'"),
        )
        visibility_group.add_argument(
            "--private",
            action="store_const",
            const="private",
            dest="visibility",
            help=_("Set namespace visibility 'private'"),
        )
        protected_group = parser.add_mutually_exclusive_group()
        protected_group.add_argument(
            "--protected",
            action="store_const",
            const=True,
            dest="is_protected",
            help=_("Prevent metadef namespace from being deleted"),
        )
        protected_group.add_argument(
            "--unprotected",
            action="store_const",
            const=False,
            dest="is_protected",
            help=_("Allow metadef namespace to be deleted (default)"),
        )
        return parser

    def take_action(self, parsed_args):
        image_client = self.app.client_manager.image
        filter_keys = ['namespace', 'display_name', 'description']
        kwargs = {}

        for key in filter_keys:
            argument = getattr(parsed_args, key, None)
            if argument is not None:
                kwargs[key] = argument

        if parsed_args.is_protected is not None:
            kwargs['protected'] = parsed_args.is_protected

        if parsed_args.visibility is not None:
            kwargs['visibility'] = parsed_args.visibility

        data = image_client.create_metadef_namespace(**kwargs)
        info = _format_namespace(data)

        return zip(*sorted(info.items()))


class DeleteMetadefNamespace(command.Command):
    _description = _("Delete metadef namespace")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "namespace",
            metavar="<namespace>",
            nargs="+",
            help=_("Metadef namespace(s) to delete (name)"),
        )
        return parser

    def take_action(self, parsed_args):
        image_client = self.app.client_manager.image

        result = 0
        for ns in parsed_args.namespace:
            try:
                namespace = image_client.get_metadef_namespace(ns)
                image_client.delete_metadef_namespace(namespace.id)
            except Exception as e:
                result += 1
                LOG.error(
                    _(
                        "Failed to delete namespace with name or "
                        "ID '%(namespace)s': %(e)s"
                    ),
                    {'namespace': ns, 'e': e},
                )

        if result > 0:
            total = len(parsed_args.namespace)
            msg = _("%(result)s of %(total)s namespace failed to delete.") % {
                'result': result,
                'total': total,
            }
            raise exceptions.CommandError(msg)


class ListMetadefNamespace(command.Lister):
    _description = _("List metadef namespaces")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "--resource-types",
            metavar="<resource_types>",
            help=_("filter resource types"),
        )
        parser.add_argument(
            "--visibility",
            metavar="<visibility>",
            help=_("filter on visibility"),
        )
        return parser

    def take_action(self, parsed_args):
        image_client = self.app.client_manager.image
        filter_keys = ['resource_types', 'visibility']
        kwargs = {}
        for key in filter_keys:
            argument = getattr(parsed_args, key, None)
            if argument is not None:
                kwargs[key] = argument
        # List of namespace data received
        data = list(image_client.metadef_namespaces(**kwargs))
        columns = ['namespace']
        column_headers = columns
        return (
            column_headers,
            (
                utils.get_item_properties(
                    s,
                    columns,
                    formatters=_formatters,
                )
                for s in data
            ),
        )


class SetMetadefNamespace(command.Command):
    _description = _("Set metadef namespace properties")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "namespace",
            metavar="<namespace>",
            help=_("Metadef namespace to modify (name)"),
        )
        parser.add_argument(
            "--display-name",
            metavar="<display_name>",
            help=_("Set a user-friendly name for the namespace."),
        )
        parser.add_argument(
            "--description",
            metavar="<description>",
            help=_("Set the description of the namespace"),
        )
        visibility_group = parser.add_mutually_exclusive_group()
        visibility_group.add_argument(
            "--public",
            action="store_const",
            const="public",
            dest="visibility",
            help=_("Metadef namespace is accessible to the public"),
        )
        visibility_group.add_argument(
            "--private",
            action="store_const",
            const="private",
            dest="visibility",
            help=_(
                "Metadef namespace is inaccessible to the public (default)"
            ),
        )
        protected_group = parser.add_mutually_exclusive_group()
        protected_group.add_argument(
            "--protected",
            action="store_const",
            const=True,
            dest="is_protected",
            help=_("Prevent metadef namespace from being deleted"),
        )
        protected_group.add_argument(
            "--unprotected",
            action="store_const",
            const=False,
            dest="is_protected",
            help=_("Allow metadef namespace to be deleted (default)"),
        )
        return parser

    def take_action(self, parsed_args):
        image_client = self.app.client_manager.image

        namespace = parsed_args.namespace

        filter_keys = ['namespace', 'display_name', 'description']
        kwargs = {}

        for key in filter_keys:
            argument = getattr(parsed_args, key, None)
            if argument is not None:
                kwargs[key] = argument

        if parsed_args.is_protected is not None:
            kwargs['protected'] = parsed_args.is_protected

        if parsed_args.visibility is not None:
            kwargs['visibility'] = parsed_args.visibility

        image_client.update_metadef_namespace(namespace, **kwargs)


class ShowMetadefNamespace(command.ShowOne):
    _description = _("Show a metadef namespace")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "namespace",
            metavar="<namespace>",
            help=_("Metadef namespace to show (name)"),
        )
        return parser

    def take_action(self, parsed_args):
        image_client = self.app.client_manager.image

        namespace = parsed_args.namespace

        data = image_client.get_metadef_namespace(namespace)
        info = _format_namespace(data)

        return zip(*sorted(info.items()))
