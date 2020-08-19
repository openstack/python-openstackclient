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
import contextlib
import logging

import openstack.exceptions
from osc_lib.command import command
from osc_lib import exceptions
import six

from openstackclient.i18n import _


LOG = logging.getLogger(__name__)

_required_opt_extensions_map = {
    'allowed_address_pairs': 'allowed-address-pairs',
    'dns_domain': 'dns-integration',
    'dns_name': 'dns-integration',
    'extra_dhcp_opts': 'extra_dhcp_opt',
    'qos_policy_id': 'qos',
    'security_groups': 'security-groups',
}


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


@six.add_metaclass(abc.ABCMeta)
class NetworkAndComputeCommand(command.Command):
    """Network and Compute Command

    Command class for commands that support implementation via
    the network or compute endpoint. Such commands have different
    implementations for take_action() and may even have different
    arguments.
    """

    def take_action(self, parsed_args):
        if self.app.client_manager.is_network_endpoint_enabled():
            return self.take_action_network(self.app.client_manager.network,
                                            parsed_args)
        else:
            return self.take_action_compute(self.app.client_manager.compute,
                                            parsed_args)

    def get_parser(self, prog_name):
        LOG.debug('get_parser(%s)', prog_name)
        parser = super(NetworkAndComputeCommand, self).get_parser(prog_name)
        parser = self.update_parser_common(parser)
        LOG.debug('common parser: %s', parser)
        if (
            self.app is None or
            self.app.client_manager.is_network_endpoint_enabled()
        ):
            return self.update_parser_network(parser)
        else:
            return self.update_parser_compute(parser)

    def update_parser_common(self, parser):
        """Default is no updates to parser."""
        return parser

    def update_parser_network(self, parser):
        """Default is no updates to parser."""
        return parser

    def update_parser_compute(self, parser):
        """Default is no updates to parser."""
        return parser

    @abc.abstractmethod
    def take_action_network(self, client, parsed_args):
        """Override to do something useful."""
        pass

    @abc.abstractmethod
    def take_action_compute(self, client, parsed_args):
        """Override to do something useful."""
        pass


@six.add_metaclass(abc.ABCMeta)
class NetworkAndComputeDelete(NetworkAndComputeCommand):
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
                    self.take_action_network(self.app.client_manager.network,
                                             parsed_args)
                else:
                    self.take_action_compute(self.app.client_manager.compute,
                                             parsed_args)
            except Exception as e:
                msg = _("Failed to delete %(resource)s with name or ID "
                        "'%(name_or_id)s': %(e)s") % {
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


@six.add_metaclass(abc.ABCMeta)
class NetworkAndComputeLister(command.Lister):
    """Network and Compute Lister

    Lister class for commands that support implementation via
    the network or compute endpoint. Such commands have different
    implementations for take_action() and may even have different
    arguments.
    """

    def take_action(self, parsed_args):
        if self.app.client_manager.is_network_endpoint_enabled():
            return self.take_action_network(self.app.client_manager.network,
                                            parsed_args)
        else:
            return self.take_action_compute(self.app.client_manager.compute,
                                            parsed_args)

    def get_parser(self, prog_name):
        LOG.debug('get_parser(%s)', prog_name)
        parser = super(NetworkAndComputeLister, self).get_parser(prog_name)
        parser = self.update_parser_common(parser)
        LOG.debug('common parser: %s', parser)
        if self.app.client_manager.is_network_endpoint_enabled():
            return self.update_parser_network(parser)
        else:
            return self.update_parser_compute(parser)

    def update_parser_common(self, parser):
        """Default is no updates to parser."""
        return parser

    def update_parser_network(self, parser):
        """Default is no updates to parser."""
        return parser

    def update_parser_compute(self, parser):
        """Default is no updates to parser."""
        return parser

    @abc.abstractmethod
    def take_action_network(self, client, parsed_args):
        """Override to do something useful."""
        pass

    @abc.abstractmethod
    def take_action_compute(self, client, parsed_args):
        """Override to do something useful."""
        pass


@six.add_metaclass(abc.ABCMeta)
class NetworkAndComputeShowOne(command.ShowOne):
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
                    self.app.client_manager.network, parsed_args)
            else:
                return self.take_action_compute(
                    self.app.client_manager.compute, parsed_args)
        except openstack.exceptions.HttpException as exc:
            msg = _("Error while executing command: %s") % exc.message
            if exc.details:
                msg += ", " + six.text_type(exc.details)
            raise exceptions.CommandError(msg)

    def get_parser(self, prog_name):
        LOG.debug('get_parser(%s)', prog_name)
        parser = super(NetworkAndComputeShowOne, self).get_parser(prog_name)
        parser = self.update_parser_common(parser)
        LOG.debug('common parser: %s', parser)
        if self.app.client_manager.is_network_endpoint_enabled():
            return self.update_parser_network(parser)
        else:
            return self.update_parser_compute(parser)

    def update_parser_common(self, parser):
        """Default is no updates to parser."""
        return parser

    def update_parser_network(self, parser):
        """Default is no updates to parser."""
        return parser

    def update_parser_compute(self, parser):
        """Default is no updates to parser."""
        return parser

    @abc.abstractmethod
    def take_action_network(self, client, parsed_args):
        """Override to do something useful."""
        pass

    @abc.abstractmethod
    def take_action_compute(self, client, parsed_args):
        """Override to do something useful."""
        pass
