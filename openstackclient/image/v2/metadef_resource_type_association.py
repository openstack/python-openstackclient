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

import logging

from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _

LOG = logging.getLogger(__name__)


def _get_columns(item):
    hidden_columns = ['location']
    return utils.get_osc_show_columns_for_sdk_resource(
        item, {}, hidden_columns
    )


class CreateMetadefResourceTypeAssociation(command.ShowOne):
    _description = _("Create metadef resource type association")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "namespace",
            metavar="<namespace>",
            help=_(
                "The name of the namespace you want to create the "
                "resource type association in"
            ),
        )
        parser.add_argument(
            "name",
            metavar="<name>",
            help=_("A name of the new resource type"),
        )
        parser.add_argument(
            "--properties-target",
            metavar="<properties_target>",
            help=_(
                "Some resource types allow more than one "
                "key/value pair per instance."
            ),
        )
        return parser

    def take_action(self, parsed_args):
        image_client = self.app.client_manager.image
        kwargs = {}

        kwargs['namespace'] = parsed_args.namespace
        kwargs['name'] = parsed_args.name

        if parsed_args.properties_target:
            kwargs['properties_target'] = parsed_args.properties_target

        obj = image_client.create_metadef_resource_type_association(
            parsed_args.namespace, **kwargs
        )

        display_columns, columns = _get_columns(obj)
        data = utils.get_item_properties(obj, columns, formatters={})

        return (display_columns, data)


class DeleteMetadefResourceTypeAssociation(command.Command):
    _description = _("Delete metadef resource type association")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "metadef_namespace",
            metavar="<metadef_namespace>",
            help=_("The name of the namespace whose details you want to see"),
        )
        parser.add_argument(
            "name",
            metavar="<name>",
            nargs="+",
            help=_(
                "The name of the resource type(s) (repeat option to delete"
                "multiple metadef resource type associations)"
            ),
        )
        parser.add_argument(
            "--force",
            dest='force',
            action='store_true',
            default=False,
            help=_(
                "Force delete the resource type association if the"
                "namespace is protected"
            ),
        )
        return parser

    def take_action(self, parsed_args):
        image_client = self.app.client_manager.image

        result = 0
        for resource_type in parsed_args.name:
            try:
                metadef_namespace = image_client.get_metadef_namespace(
                    parsed_args.metadef_namespace
                )

                kwargs = {}
                is_initially_protected = (
                    True if metadef_namespace.is_protected else False
                )
                if is_initially_protected and parsed_args.force:
                    kwargs['is_protected'] = False

                    image_client.update_metadef_namespace(
                        metadef_namespace.namespace, **kwargs
                    )

                try:
                    image_client.delete_metadef_resource_type_association(
                        resource_type, metadef_namespace, ignore_missing=False
                    )
                finally:
                    if is_initially_protected:
                        kwargs['is_protected'] = True
                        image_client.update_metadef_namespace(
                            metadef_namespace.namespace, **kwargs
                        )

            except Exception as e:
                result += 1
                LOG.error(
                    _(
                        "Failed to delete resource type with name or "
                        "ID '%(resource_type)s': %(e)s"
                    ),
                    {'resource_type': resource_type, 'e': e},
                )

        if result > 0:
            total = len(parsed_args.metadef_namespace)
            msg = _(
                "%(result)s of %(total)s resource type failed to delete."
            ) % {'result': result, 'total': total}
            raise exceptions.CommandError(msg)


class ListMetadefResourceTypeAssociations(command.Lister):
    _description = _("List metadef resource type associations")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "metadef_namespace",
            metavar="<metadef_namespace>",
            help=_("The name of the namespace whose details you want to see"),
        )
        return parser

    def take_action(self, parsed_args):
        image_client = self.app.client_manager.image
        data = image_client.metadef_resource_type_associations(
            parsed_args.metadef_namespace,
        )
        columns = ['Name']
        column_headers = columns
        return (
            column_headers,
            (
                utils.get_item_properties(
                    s,
                    columns,
                )
                for s in data
            ),
        )
