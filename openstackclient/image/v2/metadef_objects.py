#   Copyright 2023 Red Hat
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

from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _


LOG = logging.getLogger(__name__)


def _format_object(md_object):
    fields_to_show = (
        'created_at',
        'description',
        'name',
        'namespace_name',
        'properties',
        'required',
        'updated_at',
    )

    return (
        fields_to_show,
        utils.get_item_properties(
            md_object,
            fields_to_show,
        ),
    )


class CreateMetadefObjects(command.ShowOne):
    _description = _("Create a metadef object")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "--namespace",
            metavar="<namespace>",
            help=_("Metadef namespace to create the object in (name)"),
        )
        parser.add_argument(
            "name",
            metavar='<metadef-object-name>',
            help=_('New metadef object name'),
        )
        return parser

    def take_action(self, parsed_args):
        image_client = self.app.client_manager.image

        namespace = image_client.get_metadef_namespace(
            parsed_args.namespace,
        )
        data = image_client.create_metadef_object(
            namespace=namespace.namespace,
            name=parsed_args.name,
        )

        fields, value = _format_object(data)

        return fields, value


class ShowMetadefObjects(command.ShowOne):
    _description = _("Show a particular metadef object")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "namespace",
            metavar="<namespace>",
            help=_("Metadef namespace of the object (name)"),
        )
        parser.add_argument(
            "object",
            metavar="<object>",
            help=_("Metadef object to show"),
        )
        return parser

    def take_action(self, parsed_args):
        image_client = self.app.client_manager.image

        namespace = parsed_args.namespace
        object = parsed_args.object

        data = image_client.get_metadef_object(object, namespace)

        fields, value = _format_object(data)

        return fields, value


class DeleteMetadefObject(command.Command):
    _description = _("Delete metadata definitions object(s)")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "namespace",
            metavar="<namespace>",
            help=_("Metadef namespace of the object (name)"),
        )
        parser.add_argument(
            "objects",
            metavar="<object>",
            nargs="+",
            help=_("Metadef object(s) to delete (name)"),
        )
        return parser

    def take_action(self, parsed_args):
        image_client = self.app.client_manager.image

        namespace = parsed_args.namespace

        result = 0
        for obj in parsed_args.objects:
            try:
                object = image_client.get_metadef_object(obj, namespace)
                image_client.delete_metadef_object(object, namespace)
            except Exception as e:
                result += 1
                LOG.error(
                    _(
                        "Failed to delete object with name or "
                        "ID '%(object)s': %(e)s"
                    ),
                    {'object': obj, 'e': e},
                )

        if result > 0:
            total = len(parsed_args.namespace)
            msg = _("%(result)s of %(total)s object failed to delete.") % {
                'result': result,
                'total': total,
            }
            raise exceptions.CommandError(msg)


class ListMetadefObjects(command.Lister):
    _description = _("List metadef objects inside a specific namespace.")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "namespace",
            metavar="<namespace>",
            help=_("Namespace (name) for the namespace"),
        )
        return parser

    def take_action(self, parsed_args):
        image_client = self.app.client_manager.image

        namespace = parsed_args.namespace
        columns = ['name', 'description']

        md_objects = list(image_client.metadef_objects(namespace))
        column_headers = columns
        return (
            column_headers,
            (
                utils.get_item_properties(
                    md_object,
                    columns,
                )
                for md_object in md_objects
            ),
        )


class SetMetadefObject(command.Command):
    _description = _("Update a metadef object")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "namespace",
            metavar="<namespace>",
            help=_("Metadef namespace name"),
        )
        parser.add_argument(
            "object",
            metavar="<object>",
            help=_('Metadef object to be updated'),
        )
        parser.add_argument(
            "--name",
            help=_("New name of the object"),
        )
        return parser

    def take_action(self, parsed_args):
        image_client = self.app.client_manager.image

        object = image_client.get_metadef_object(
            parsed_args.object, parsed_args.namespace
        )
        kwargs = {}
        if parsed_args.name:
            kwargs['name'] = parsed_args.name

        image_client.update_metadef_object(
            object, parsed_args.namespace, **kwargs
        )


class ShowMetadefObjectProperty(command.ShowOne):
    _description = _(
        "Describe a specific metadata definitions property inside an object."
    )

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "namespace",
            metavar="<namespace_name>",
            help=_("Namespace (name) for the namespace"),
        )
        parser.add_argument(
            "object",
            metavar="<object_name>",
            help=_("Name of an object."),
        )
        parser.add_argument(
            "property",
            help=_("Name of the property."),
        )
        return parser

    def take_action(self, parsed_args):
        image_client = self.app.client_manager.image

        namespace_name = parsed_args.namespace
        object_name = parsed_args.object

        obj = image_client.get_metadef_object(object_name, namespace_name)
        try:
            prop = obj['properties'][parsed_args.property]
            prop['name'] = parsed_args.property

        except KeyError:
            msg = _(
                'Property %(property)s not found in object %(object)s.'
            ) % {
                'property': parsed_args.property,
                'object': parsed_args.object,
            }
            raise exceptions.CommandError(msg)

        return zip(*sorted(prop.items()))
