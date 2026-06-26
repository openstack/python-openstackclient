#   Copyright 2015 iWeb Technologies Inc.
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

"""Volume v3 QoS action implementations"""

import argparse
import logging
from collections.abc import Iterable, Sequence
from typing import Any

from openstack import utils as sdk_utils
from osc_lib.cli import format_columns
from osc_lib.cli import parseractions
from osc_lib import exceptions
from osc_lib import utils

from openstackclient import command
from openstackclient.i18n import _


LOG = logging.getLogger(__name__)


class AssociateQos(command.Command):
    _description = _("Associate a QoS specification to a volume type")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'qos_spec',
            metavar='<qos-spec>',
            help=_('QoS specification to modify (name or ID)'),
        )
        parser.add_argument(
            'volume_type',
            metavar='<volume-type>',
            help=_('Volume type to associate the QoS (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args: argparse.Namespace) -> None:
        volume_client = sdk_utils.ensure_service_version(
            self.app.client_manager.volume, '3'
        )
        qos_spec = volume_client.find_qos_spec(
            parsed_args.qos_spec, ignore_missing=False
        )
        volume_type = volume_client.find_type(
            parsed_args.volume_type, ignore_missing=False
        )
        volume_client.associate_qos_spec(qos_spec.id, volume_type.id)


class CreateQos(command.ShowOne):
    _description = _("Create new QoS specification")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<name>',
            help=_('New QoS specification name'),
        )
        consumer_choices = ['front-end', 'back-end', 'both']
        parser.add_argument(
            '--consumer',
            metavar='<consumer>',
            choices=consumer_choices,
            default='both',
            help=(
                _(
                    'Consumer of the QoS. Valid consumers: %s '
                    "(defaults to 'both')"
                )
                % utils.format_list(consumer_choices)
            ),
        )
        parser.add_argument(
            '--property',
            metavar='<key=value>',
            dest='properties',
            action=parseractions.KeyValueAction,
            help=_(
                'Set a QoS specification property '
                '(repeat option to set multiple properties)'
            ),
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[Any]]:
        volume_client = sdk_utils.ensure_service_version(
            self.app.client_manager.volume, '3'
        )
        attrs: dict[str, Any] = {'consumer': parsed_args.consumer}
        if parsed_args.properties:
            attrs.update(parsed_args.properties)
        qos_spec = volume_client.create_qos_spec(
            name=parsed_args.name, **attrs
        )
        columns = ('consumer', 'id', 'name', 'properties')
        data = (
            qos_spec.consumer,
            qos_spec.id,
            qos_spec.name,
            format_columns.DictColumn(qos_spec.specs),
        )
        return columns, data


class DeleteQos(command.Command):
    _description = _("Delete QoS specification")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'qos_specs',
            metavar='<qos-spec>',
            nargs="+",
            help=_('QoS specification(s) to delete (name or ID)'),
        )
        parser.add_argument(
            '--force',
            action='store_true',
            default=False,
            help=_("Allow to delete in-use QoS specification(s)"),
        )
        return parser

    def take_action(self, parsed_args: argparse.Namespace) -> None:
        volume_client = sdk_utils.ensure_service_version(
            self.app.client_manager.volume, '3'
        )
        result = 0

        for i in parsed_args.qos_specs:
            try:
                qos_spec = volume_client.find_qos_spec(i, ignore_missing=False)
                volume_client.delete_qos_spec(
                    qos_spec.id, ignore_missing=False, force=parsed_args.force
                )
            except Exception as e:
                result += 1
                LOG.error(
                    _(
                        "Failed to delete QoS specification with "
                        "name or ID '%(qos)s': %(e)s"
                    ),
                    {'qos': i, 'e': e},
                )

        if result > 0:
            total = len(parsed_args.qos_specs)
            msg = _(
                "%(result)s of %(total)s QoS specifications failed to delete."
            ) % {'result': result, 'total': total}
            raise exceptions.CommandError(msg)


class DisassociateQos(command.Command):
    _description = _("Disassociate a QoS specification from a volume type")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'qos_spec',
            metavar='<qos-spec>',
            help=_('QoS specification to modify (name or ID)'),
        )
        volume_type_group = parser.add_mutually_exclusive_group()
        volume_type_group.add_argument(
            '--volume-type',
            metavar='<volume-type>',
            help=_('Volume type to disassociate the QoS from (name or ID)'),
        )
        volume_type_group.add_argument(
            '--all',
            action='store_true',
            default=False,
            help=_('Disassociate the QoS from every volume type'),
        )

        return parser

    def take_action(self, parsed_args: argparse.Namespace) -> None:
        volume_client = sdk_utils.ensure_service_version(
            self.app.client_manager.volume, '3'
        )
        qos_spec = volume_client.find_qos_spec(
            parsed_args.qos_spec, ignore_missing=False
        )

        if parsed_args.volume_type:
            volume_type = volume_client.find_type(
                parsed_args.volume_type, ignore_missing=False
            )
            volume_client.disassociate_qos_spec(qos_spec.id, volume_type.id)
        elif parsed_args.all:
            volume_client.disassociate_all_qos_spec(qos_spec.id)


class ListQos(command.Lister):
    _description = _("List QoS specifications")

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[tuple[Any, ...]]]:
        volume_client = sdk_utils.ensure_service_version(
            self.app.client_manager.volume, '3'
        )
        qos_specs_list = list(volume_client.qos_specs())

        display_columns = (
            'ID',
            'Name',
            'Consumer',
            'Associations',
            'Properties',
        )

        data = []
        for qos in qos_specs_list:
            qos_associations = volume_client.qos_spec_associations(qos)
            associations = [a.name for a in qos_associations]
            data.append(
                (
                    qos.id,
                    qos.name,
                    qos.consumer,
                    format_columns.ListColumn(associations),
                    format_columns.DictColumn(qos.specs),
                )
            )

        return display_columns, iter(data)


class SetQos(command.Command):
    _description = _("Set QoS specification properties")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'qos_spec',
            metavar='<qos-spec>',
            help=_('QoS specification to modify (name or ID)'),
        )
        parser.add_argument(
            '--no-property',
            dest='no_property',
            action='store_true',
            help=_(
                'Remove all properties from <qos-spec> '
                '(specify both --no-property and --property to remove the '
                'current properties before setting new properties)'
            ),
        )
        parser.add_argument(
            '--property',
            metavar='<key=value>',
            dest='properties',
            action=parseractions.KeyValueAction,
            help=_(
                'Property to add or modify for this QoS specification '
                '(repeat option to set multiple properties)'
            ),
        )
        return parser

    def take_action(self, parsed_args: argparse.Namespace) -> None:
        volume_client = sdk_utils.ensure_service_version(
            self.app.client_manager.volume, '3'
        )
        qos_spec = volume_client.find_qos_spec(
            parsed_args.qos_spec, ignore_missing=False
        )

        result = 0
        if parsed_args.no_property:
            try:
                key_list = list(qos_spec.specs.keys())
                volume_client.delete_qos_spec_metadata(qos_spec.id, key_list)
            except Exception as e:
                LOG.error(_("Failed to clean qos properties: %s"), e)
                result += 1

        if parsed_args.properties:
            try:
                volume_client.update_qos_spec(
                    qos_spec.id, **parsed_args.properties
                )
            except Exception as e:
                LOG.error(_("Failed to set qos property: %s"), e)
                result += 1

        if result > 0:
            raise exceptions.CommandError(
                _("One or more of the set operations failed")
            )


class ShowQos(command.ShowOne):
    _description = _("Display QoS specification details")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'qos_spec',
            metavar='<qos-spec>',
            help=_('QoS specification to display (name or ID)'),
        )
        return parser

    def take_action(
        self, parsed_args: argparse.Namespace
    ) -> tuple[Sequence[str], Iterable[Any]]:
        volume_client = sdk_utils.ensure_service_version(
            self.app.client_manager.volume, '3'
        )
        qos_spec = volume_client.find_qos_spec(
            parsed_args.qos_spec, ignore_missing=False
        )
        qos_associations = list(volume_client.qos_spec_associations(qos_spec))
        associations = [a.name for a in qos_associations]
        if associations:
            columns: tuple[str, ...] = (
                'associations',
                'consumer',
                'id',
                'name',
                'properties',
            )
            data: tuple[Any, ...] = (
                format_columns.ListColumn(associations),
                qos_spec.consumer,
                qos_spec.id,
                qos_spec.name,
                format_columns.DictColumn(qos_spec.specs),
            )
        else:
            columns = ('consumer', 'id', 'name', 'properties')
            data = (
                qos_spec.consumer,
                qos_spec.id,
                qos_spec.name,
                format_columns.DictColumn(qos_spec.specs),
            )
        return columns, data


class UnsetQos(command.Command):
    _description = _("Unset QoS specification properties")

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'qos_spec',
            metavar='<qos-spec>',
            help=_('QoS specification to modify (name or ID)'),
        )
        parser.add_argument(
            '--property',
            metavar='<key>',
            action='append',
            dest='properties',
            default=[],
            help=_(
                'Property to remove from the QoS specification. '
                '(repeat option to unset multiple properties)'
            ),
        )
        return parser

    def take_action(self, parsed_args: argparse.Namespace) -> None:
        volume_client = sdk_utils.ensure_service_version(
            self.app.client_manager.volume, '3'
        )
        qos_spec = volume_client.find_qos_spec(
            parsed_args.qos_spec, ignore_missing=False
        )
        if parsed_args.properties:
            volume_client.delete_qos_spec_metadata(
                qos_spec.id, parsed_args.properties
            )
