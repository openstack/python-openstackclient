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

"""Volume v1 QoS action implementations"""

import logging
import six

from cliff import command
from cliff import lister
from cliff import show

from openstackclient.common import parseractions
from openstackclient.common import utils


class AssociateQos(command.Command):
    """Associate a QoS specification to a volume type"""

    log = logging.getLogger(__name__ + '.AssociateQos')

    def get_parser(self, prog_name):
        parser = super(AssociateQos, self).get_parser(prog_name)
        parser.add_argument(
            'qos_spec',
            metavar='<qos-spec>',
            help='QoS specification to modify (name or ID)',
        )
        parser.add_argument(
            'volume_type',
            metavar='<volume-type>',
            help='Volume type to associate the QoS (name or ID)',
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        qos_spec = utils.find_resource(volume_client.qos_specs,
                                       parsed_args.qos_spec)
        volume_type = utils.find_resource(volume_client.volume_types,
                                          parsed_args.volume_type)

        volume_client.qos_specs.associate(qos_spec.id, volume_type.id)

        return


class CreateQos(show.ShowOne):
    """Create new QoS specification"""

    log = logging.getLogger(__name__ + '.CreateQos')

    def get_parser(self, prog_name):
        parser = super(CreateQos, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<name>',
            help='New QoS specification name',
        )
        consumer_choices = ['front-end', 'back-end', 'both']
        parser.add_argument(
            '--consumer',
            metavar='<consumer>',
            choices=consumer_choices,
            default='both',
            help='Consumer of the QoS. Valid consumers: %s '
                 "(defaults to 'both')" % utils.format_list(consumer_choices)
        )
        parser.add_argument(
            '--property',
            metavar='<key=value>',
            action=parseractions.KeyValueAction,
            help='Set a QoS specification property '
                 '(repeat option to set multiple properties)',
        )
        return parser

    @utils.log_method(log)
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

    log = logging.getLogger(__name__ + '.DeleteQos')

    def get_parser(self, prog_name):
        parser = super(DeleteQos, self).get_parser(prog_name)
        parser.add_argument(
            'qos_specs',
            metavar='<qos-spec>',
            nargs="+",
            help='QoS specification(s) to delete (name or ID)',
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        for qos in parsed_args.qos_specs:
            qos_spec = utils.find_resource(volume_client.qos_specs, qos)
            volume_client.qos_specs.delete(qos_spec.id)
        return


class DisassociateQos(command.Command):
    """Disassociate a QoS specification from a volume type"""

    log = logging.getLogger(__name__ + '.DisassociateQos')

    def get_parser(self, prog_name):
        parser = super(DisassociateQos, self).get_parser(prog_name)
        parser.add_argument(
            'qos_spec',
            metavar='<qos-spec>',
            help='QoS specification to modify (name or ID)',
        )
        volume_type_group = parser.add_mutually_exclusive_group()
        volume_type_group.add_argument(
            '--volume-type',
            metavar='<volume-type>',
            help='Volume type to disassociate the QoS from (name or ID)',
        )
        volume_type_group.add_argument(
            '--all',
            action='store_true',
            default=False,
            help='Disassociate the QoS from every volume type',
        )

        return parser

    @utils.log_method(log)
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

        return


class ListQos(lister.Lister):
    """List QoS specifications"""

    log = logging.getLogger(__name__ + '.ListQos')

    @utils.log_method(log)
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

    log = logging.getLogger(__name__ + '.SetQos')

    def get_parser(self, prog_name):
        parser = super(SetQos, self).get_parser(prog_name)
        parser.add_argument(
            'qos_spec',
            metavar='<qos-spec>',
            help='QoS specification to modify (name or ID)',
        )
        parser.add_argument(
            '--property',
            metavar='<key=value>',
            action=parseractions.KeyValueAction,
            help='Property to add or modify for this QoS specification '
                 '(repeat option to set multiple properties)',
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        qos_spec = utils.find_resource(volume_client.qos_specs,
                                       parsed_args.qos_spec)

        if parsed_args.property:
            volume_client.qos_specs.set_keys(qos_spec.id,
                                             parsed_args.property)
        else:
            self.app.log.error("No changes requested\n")

        return


class ShowQos(show.ShowOne):
    """Display QoS specification details"""

    log = logging.getLogger(__name__ + '.ShowQos')

    def get_parser(self, prog_name):
        parser = super(ShowQos, self).get_parser(prog_name)
        parser.add_argument(
            'qos_spec',
            metavar='<qos-spec>',
            help='QoS specification to display (name or ID)',
        )
        return parser

    @utils.log_method(log)
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

    log = logging.getLogger(__name__ + '.SetQos')

    def get_parser(self, prog_name):
        parser = super(UnsetQos, self).get_parser(prog_name)
        parser.add_argument(
            'qos_spec',
            metavar='<qos-spec>',
            help='QoS specification to modify (name or ID)',
        )
        parser.add_argument(
            '--property',
            metavar='<key>',
            action='append',
            default=[],
            help='Property to remove from the QoS specification. '
                 '(repeat option to unset multiple properties)',
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
        volume_client = self.app.client_manager.volume
        qos_spec = utils.find_resource(volume_client.qos_specs,
                                       parsed_args.qos_spec)

        if parsed_args.property:
            volume_client.qos_specs.unset_keys(qos_spec.id,
                                               parsed_args.property)
        else:
            self.app.log.error("No changes requested\n")

        return
