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
#

"""Volume v2 QoS action implementations"""

import logging

from osc_lib.cli import parseractions
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils
import six

from openstackclient.i18n import _


LOG = logging.getLogger(__name__)


class AssociateQos(command.Command):
    """Associate a QoS specification to a volume type"""

    def get_parser(self, prog_name):
        parser = super(AssociateQos, self).get_parser(prog_name)
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

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        qos_spec = utils.find_resource(volume_client.qos_specs,
                                       parsed_args.qos_spec)
        volume_type = utils.find_resource(volume_client.volume_types,
                                          parsed_args.volume_type)

        volume_client.qos_specs.associate(qos_spec.id, volume_type.id)


class CreateQos(command.ShowOne):
    """Create new QoS specification"""

    def get_parser(self, prog_name):
        parser = super(CreateQos, self).get_parser(prog_name)
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
            help=(_('Consumer of the QoS. Valid consumers: %s '
                  "(defaults to 'both')") %
                  utils.format_list(consumer_choices))
        )
        parser.add_argument(
            '--property',
            metavar='<key=value>',
            action=parseractions.KeyValueAction,
            help=_('Set a QoS specification property '
                   '(repeat option to set multiple properties)'),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        specs = {}
        specs.update({'consumer': parsed_args.consumer})

        if parsed_args.property:
            specs.update(parsed_args.property)

        qos_spec = volume_client.qos_specs.create(parsed_args.name, specs)

        return zip(*sorted(six.iteritems(qos_spec._info)))


class DeleteQos(command.Command):
    """Delete QoS specification"""

    def get_parser(self, prog_name):
        parser = super(DeleteQos, self).get_parser(prog_name)
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
            help=_("Allow to delete in-use QoS specification(s)")
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        result = 0

        for i in parsed_args.qos_specs:
            try:
                qos_spec = utils.find_resource(volume_client.qos_specs, i)
                volume_client.qos_specs.delete(qos_spec.id, parsed_args.force)
            except Exception as e:
                result += 1
                LOG.error(_("Failed to delete QoS specification with "
                            "name or ID '%(qos)s': %(e)s")
                          % {'qos': i, 'e': e})

        if result > 0:
            total = len(parsed_args.qos_specs)
            msg = (_("%(result)s of %(total)s QoS specifications failed"
                   " to delete.") % {'result': result, 'total': total})
            raise exceptions.CommandError(msg)


class DisassociateQos(command.Command):
    """Disassociate a QoS specification from a volume type"""

    def get_parser(self, prog_name):
        parser = super(DisassociateQos, self).get_parser(prog_name)
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

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        qos_spec = utils.find_resource(volume_client.qos_specs,
                                       parsed_args.qos_spec)

        if parsed_args.volume_type:
            volume_type = utils.find_resource(volume_client.volume_types,
                                              parsed_args.volume_type)
            volume_client.qos_specs.disassociate(qos_spec.id, volume_type.id)
        elif parsed_args.all:
            volume_client.qos_specs.disassociate_all(qos_spec.id)


class ListQos(command.Lister):
    """List QoS specifications"""

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        qos_specs_list = volume_client.qos_specs.list()

        for qos in qos_specs_list:
            qos_associations = volume_client.qos_specs.get_associations(qos)
            if qos_associations:
                associations = [association.name
                                for association in qos_associations]
                qos._info.update({'associations': associations})

        columns = ('ID', 'Name', 'Consumer', 'Associations', 'Specs')
        return (columns,
                (utils.get_dict_properties(
                    s._info, columns,
                    formatters={
                        'Specs': utils.format_dict,
                        'Associations': utils.format_list
                    },
                ) for s in qos_specs_list))


class SetQos(command.Command):
    """Set QoS specification properties"""

    def get_parser(self, prog_name):
        parser = super(SetQos, self).get_parser(prog_name)
        parser.add_argument(
            'qos_spec',
            metavar='<qos-spec>',
            help=_('QoS specification to modify (name or ID)'),
        )
        parser.add_argument(
            '--property',
            metavar='<key=value>',
            action=parseractions.KeyValueAction,
            help=_('Property to add or modify for this QoS specification '
                   '(repeat option to set multiple properties)'),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        qos_spec = utils.find_resource(volume_client.qos_specs,
                                       parsed_args.qos_spec)

        if parsed_args.property:
            volume_client.qos_specs.set_keys(qos_spec.id,
                                             parsed_args.property)


class ShowQos(command.ShowOne):
    """Display QoS specification details"""

    def get_parser(self, prog_name):
        parser = super(ShowQos, self).get_parser(prog_name)
        parser.add_argument(
            'qos_spec',
            metavar='<qos-spec>',
            help=_('QoS specification to display (name or ID)'),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        qos_spec = utils.find_resource(volume_client.qos_specs,
                                       parsed_args.qos_spec)

        qos_associations = volume_client.qos_specs.get_associations(qos_spec)
        if qos_associations:
            associations = [association.name
                            for association in qos_associations]
            qos_spec._info.update({
                'associations': utils.format_list(associations)
            })
        qos_spec._info.update({'specs': utils.format_dict(qos_spec.specs)})

        return zip(*sorted(six.iteritems(qos_spec._info)))


class UnsetQos(command.Command):
    """Unset QoS specification properties"""

    def get_parser(self, prog_name):
        parser = super(UnsetQos, self).get_parser(prog_name)
        parser.add_argument(
            'qos_spec',
            metavar='<qos-spec>',
            help=_('QoS specification to modify (name or ID)'),
        )
        parser.add_argument(
            '--property',
            metavar='<key>',
            action='append',
            default=[],
            help=_('Property to remove from the QoS specification. '
                   '(repeat option to unset multiple properties)'),
        )
        return parser

    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        qos_spec = utils.find_resource(volume_client.qos_specs,
                                       parsed_args.qos_spec)

        if parsed_args.property:
            volume_client.qos_specs.unset_keys(qos_spec.id,
                                               parsed_args.property)
