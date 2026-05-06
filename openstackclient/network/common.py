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

import argparse
from collections.abc import Generator
import contextlib
import logging
from typing import Any

import openstack.exceptions
from osc_lib.cli import parseractions
from osc_lib import exceptions

from openstackclient import command
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


@contextlib.contextmanager
def check_missing_extension_if_error(
    client_manager: Any, attrs: dict[str, Any]
) -> Generator[None, None, None]:
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

    def _get_property_converter(self, _property: dict[str, Any]) -> Any:
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

    def _parse_extra_properties(
        self, extra_properties: list[dict[str, Any]] | None
    ) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if extra_properties:
            for _property in extra_properties:
                converter = self._get_property_converter(_property)
                result[_property['name']] = converter(_property['value'])
        return result

    def get_parser(self, prog_name: str) -> argparse.ArgumentParser:
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
    def _parse_extra_properties(
        self, extra_properties: list[dict[str, Any]] | None
    ) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if extra_properties:
            for _property in extra_properties:
                result[_property['name']] = None

        return result
