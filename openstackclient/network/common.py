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

import abc
import argparse
import contextlib
import logging
import typing as ty

import cliff.app
import openstack.exceptions
from osc_lib.cli import parseractions
from osc_lib.command import command
from osc_lib import exceptions

from openstackclient.i18n import _
from openstackclient.network import utils


LOG = logging.getLogger(__name__)

_required_opt_extensions_map = {
    'allowed_address_pairs': 'allowed-address-pairs',
    'dns_domain': 'dns-integration',
    'dns_name': 'dns-integration',
    'extra_dhcp_opts': 'extra_dhcp_opt',
    'qos_policy_id': 'qos',
    'security_groups': 'security-groups',
}

_NET_TYPE_NEUTRON = 'neutron'
_NET_TYPE_COMPUTE = 'nova-network'
_QUALIFIER_FMT = "%s\n\n*%s*"


@contextlib.contextmanager
def check_missing_extension_if_error(client_manager, attrs):
    # If specified option requires extension, then try to
    # find out if it exists. If it does not exist,
    # then an exception with the appropriate message
    # will be thrown from within client.find_extension
    try:
        yield
    except openstack.exceptions.HttpException:
        for opt, ext in _required_opt_extensions_map.items():
            if opt in attrs:
                client_manager.find_extension(ext, ignore_missing=False)
        raise


class NetDetectionMixin(metaclass=abc.ABCMeta):
    """Convenience methods for nova-network vs. neutron decisions.

    A live environment detects which network type it is running and creates its
    parser with only the options relevant to that network type.

    But the command classes are used for docs builds as well, and docs must
    present the options for both network types, often qualified accordingly.
    """

    app: cliff.app.App

    @property
    def _network_type(self):
        """Discover whether the running cloud is using neutron or nova-network.

        :return:
            * ``NET_TYPE_NEUTRON`` if neutron is detected
            * ``NET_TYPE_COMPUTE`` if running in a cloud but neutron is not
              detected.
            * ``None`` if not running in a cloud, which hopefully means we're
              building docs.
        """
        # Have we set it up yet for this command?
        if not hasattr(self, '_net_type'):
            try:
                if self.app.client_manager.is_network_endpoint_enabled():
                    net_type = _NET_TYPE_NEUTRON
                else:
                    net_type = _NET_TYPE_COMPUTE
            except AttributeError:
                LOG.warning(
                    "%s: Could not detect a network type. Assuming we are "
                    "building docs.",
                    self.__class__.__name__,
                )
                net_type = None
            self._net_type = net_type
        return self._net_type

    @property
    def is_neutron(self):
        return self._network_type is _NET_TYPE_NEUTRON

    @property
    def is_nova_network(self):
        return self._network_type is _NET_TYPE_COMPUTE

    @property
    def is_docs_build(self):
        return self._network_type is None

    def enhance_help_neutron(self, _help):
        if self.is_docs_build:
            # Why can't we say 'neutron'?
            return _QUALIFIER_FMT % (_help, _("Network version 2 only"))
        return _help

    def enhance_help_nova_network(self, _help):
        if self.is_docs_build:
            # Why can't we say 'nova-network'?
            return _QUALIFIER_FMT % (_help, _("Compute version 2 only"))
        return _help

    @staticmethod
    def split_help(network_help, compute_help):
        return (
            "*{network_qualifier}:*\n  {network_help}\n\n"
            "*{compute_qualifier}:*\n  {compute_help}".format(
                **dict(
                    network_qualifier=_("Network version 2"),
                    network_help=network_help,
                    compute_qualifier=_("Compute version 2"),
                    compute_help=compute_help,
                )
            )
        )

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
        LOG.debug('get_parser(%s)', prog_name)
        parser = super().get_parser(prog_name)  # type: ignore
        parser = self.update_parser_common(parser)
        LOG.debug('common parser: %s', parser)
        if self.is_neutron or self.is_docs_build:
            parser = self.update_parser_network(parser)
        if self.is_nova_network or self.is_docs_build:
            # Add nova-net options if running nova-network or building docs
            parser = self.update_parser_compute(parser)
        return parser

    def update_parser_common(self, parser):
        """Default is no updates to parser."""
        return parser

    def update_parser_network(self, parser):
        """Default is no updates to parser."""
        return parser

    def update_parser_compute(self, parser):
        """Default is no updates to parser."""
        return parser

    def take_action(self, parsed_args):
        if self.is_neutron:
            return self.take_action_network(
                self.app.client_manager.network, parsed_args
            )
        elif self.is_nova_network:
            return self.take_action_compute(
                self.app.client_manager.compute, parsed_args
            )

    def take_action_network(self, client, parsed_args):
        """Override to do something useful."""
        pass

    def take_action_compute(self, client, parsed_args):
        """Override to do something useful."""
        pass


class NetworkAndComputeCommand(
    NetDetectionMixin, command.Command, metaclass=abc.ABCMeta
):
    """Network and Compute Command

    Command class for commands that support implementation via
    the network or compute endpoint. Such commands have different
    implementations for take_action() and may even have different
    arguments.
    """

    pass


class NetworkAndComputeDelete(NetworkAndComputeCommand, metaclass=abc.ABCMeta):
    """Network and Compute Delete

    Delete class for commands that support implementation via
    the network or compute endpoint. Such commands have different
    implementations for take_action() and may even have different
    arguments. This class supports bulk deletion, and error handling
    following the rules in doc/source/command-errors.rst.
    """

    def take_action(self, parsed_args):
        ret = 0
        resources = getattr(parsed_args, self.resource, [])

        for r in resources:
            self.r = r
            try:
                if self.app.client_manager.is_network_endpoint_enabled():
                    self.take_action_network(
                        self.app.client_manager.network, parsed_args
                    )
                else:
                    self.take_action_compute(
                        self.app.client_manager.compute,
                        parsed_args,
                    )
            except Exception as e:
                msg = _(
                    "Failed to delete %(resource)s with name or ID "
                    "'%(name_or_id)s': %(e)s"
                ) % {
                    "resource": self.resource,
                    "name_or_id": r,
                    "e": e,
                }
                LOG.error(msg)
                ret += 1

        if ret:
            total = len(resources)
            msg = _("%(num)s of %(total)s %(resource)ss failed to delete.") % {
                "num": ret,
                "total": total,
                "resource": self.resource,
            }
            raise exceptions.CommandError(msg)


class NetworkAndComputeLister(
    NetDetectionMixin, command.Lister, metaclass=abc.ABCMeta
):
    """Network and Compute Lister

    Lister class for commands that support implementation via
    the network or compute endpoint. Such commands have different
    implementations for take_action() and may even have different
    arguments.
    """

    pass


class NetworkAndComputeShowOne(
    NetDetectionMixin, command.ShowOne, metaclass=abc.ABCMeta
):
    """Network and Compute ShowOne

    ShowOne class for commands that support implementation via
    the network or compute endpoint. Such commands have different
    implementations for take_action() and may even have different
    arguments.
    """

    def take_action(self, parsed_args):
        try:
            if self.app.client_manager.is_network_endpoint_enabled():
                return self.take_action_network(
                    self.app.client_manager.network, parsed_args
                )
            else:
                return self.take_action_compute(
                    self.app.client_manager.compute, parsed_args
                )
        except openstack.exceptions.HttpException as exc:
            msg = _("Error while executing command: %s") % exc.message
            if exc.details:
                msg += ", " + str(exc.details)
            raise exceptions.CommandError(msg)


class NeutronCommandWithExtraArgs(command.Command):
    """Create and Update commands with additional extra properties.

    Extra properties can be passed to the command and are then send to the
    Neutron as given to the command.
    """

    # dict of allowed types
    _allowed_types_dict = {
        'bool': utils.str2bool,
        'dict': utils.str2dict,
        'list': utils.str2list,
        'int': int,
        'str': str,
    }

    def _get_property_converter(self, _property):
        if 'type' in _property:
            converter = self._allowed_types_dict.get(_property['type'])
        else:
            converter = str

        if not converter:
            raise exceptions.CommandError(
                _(
                    "Type {property_type} of property {name} is not supported"
                ).format(
                    property_type=_property['type'], name=_property['name']
                )
            )
        return converter

    def _parse_extra_properties(self, extra_properties):
        result: dict[str, ty.Any] = {}
        if extra_properties:
            for _property in extra_properties:
                converter = self._get_property_converter(_property)
                result[_property['name']] = converter(_property['value'])
        return result

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            '--extra-property',
            metavar='type=<property_type>,name=<property_name>,'
            'value=<property_value>',
            dest='extra_properties',
            action=parseractions.MultiKeyValueAction,
            required_keys=['name', 'value'],
            optional_keys=['type'],
            help=_(
                "Additional parameters can be passed using this property. "
                "Default type of the extra property is string ('str'), but "
                "other types can be used as well. Available types are: "
                "'dict', 'list', 'str', 'bool', 'int'. "
                "In case of 'list' type, 'value' can be "
                "semicolon-separated list of values. "
                "For 'dict' value is semicolon-separated list of the "
                "key:value pairs."
            ),
        )
        return parser


class NeutronUnsetCommandWithExtraArgs(NeutronCommandWithExtraArgs):
    def _parse_extra_properties(self, extra_properties):
        result: dict[str, ty.Any] = {}
        if extra_properties:
            for _property in extra_properties:
                result[_property['name']] = None

        return result
