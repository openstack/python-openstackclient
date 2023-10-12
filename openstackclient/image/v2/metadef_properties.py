# Copyright 2023 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from osc_lib.command import command
from osc_lib import utils

from openstackclient.i18n import _


class ListMetadefProperties(command.Lister):
    _description = _("List metadef properties")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "namespace_name",
            metavar="<namespace_name>",
            help=_("An identifier (a name) for the namespace"),
        )
        return parser

    def take_action(self, parsed_args):
        image_client = self.app.client_manager.image
        props = image_client.metadef_properties(parsed_args.namespace_name)
        columns = ['name', 'title', 'type']
        return (
            columns,
            (
                utils.get_item_properties(
                    prop,
                    columns,
                )
                for prop in props
            ),
        )


class ShowMetadefProperty(command.ShowOne):
    _description = _("Describe a specific property from a namespace")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "namespace_name",
            metavar="<namespace_name>",
            help=_("Namespace (name) for the namespace"),
        )
        parser.add_argument(
            "property_name",
            metavar="<property_name>",
            help=_("Property to show"),
        )
        return parser

    def take_action(self, parsed_args):
        image_client = self.app.client_manager.image
        data = image_client.get_metadef_property(
            parsed_args.property_name, parsed_args.namespace_name
        )
        data = data.to_dict(ignore_none=True, original_names=True)
        info = {
            key: data[key]
            for key in [
                'namespace_name',
                'name',
                'type',
                'title',
                'description',
                'operators',
                'default',
                'is_readonly',
                'minimum',
                'maximum',
                'enum',
                'pattern',
                'min_length',
                'max_length',
                'items',
                'require_unique_items',
                'min_items',
                'max_items',
                'allow_additional_items',
            ]
            if key in data
        }

        return zip(*sorted(info.items()))
