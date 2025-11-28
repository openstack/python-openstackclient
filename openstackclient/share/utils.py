# Copyright 2019 Red Hat, Inc.
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

from collections.abc import Sequence
import logging
from typing import Any

from manilaclient.common import constants
from osc_lib import exceptions

from openstackclient.common import envvars
from openstackclient.i18n import _

LOG = logging.getLogger(__name__)


def extract_key_value_options(
    pairs: dict[str, str] | None,
) -> dict[str, str]:
    result_dict = {}
    duplicate_options = []
    pairs = pairs or {}

    for attr, value in pairs.items():
        if attr not in result_dict:
            result_dict[attr] = value
        else:
            duplicate_options.append(attr)

    if pairs and len(duplicate_options) > 0:
        duplicate_str = ', '.join(duplicate_options)
        msg = f"Following options were duplicated: {duplicate_str}"
        raise exceptions.CommandError(msg)

    return result_dict


def format_properties(properties: dict[str, str]) -> str:
    formatted_data = []

    for item in properties:
        formatted_data.append(f"{item} : {properties[item]}")
    return "\n".join(formatted_data)


def extract_properties(properties: list[str]) -> dict[str, str]:
    result_dict = {}
    for item in properties:
        try:
            (key, value) = item.split('=', 1)
            if key in result_dict:
                raise exceptions.CommandError(
                    f"Argument '{key}' is specified twice."
                )
            else:
                result_dict[key] = value
        except ValueError:
            raise exceptions.CommandError(
                "Parsing error, expected format 'key=value' for " + item
            )
    return result_dict


def extract_extra_specs(
    extra_specs: dict[str, Any],
    specs_to_add: list[str],
    bool_specs: Sequence[str] = constants.BOOL_SPECS,
) -> dict[str, Any]:
    try:
        for item in specs_to_add:
            (key, value) = item.split('=', 1)
            if key in extra_specs:
                msg = f"Argument '{key}' value specified twice."
                raise exceptions.CommandError(msg)
            elif key in bool_specs:
                if envvars.bool_from_str(value):
                    extra_specs[key] = value.capitalize()
                else:
                    msg = (
                        f"Argument '{key}' is of boolean "
                        f"type and has invalid value: {value!s}"
                    )
                    raise exceptions.CommandError(msg)
            else:
                extra_specs[key] = value
    except ValueError:
        msg = _("Wrong format: specs should be key=value pairs.")
        raise exceptions.CommandError(msg)
    return extra_specs


def extract_group_specs(
    extra_specs: dict[str, Any], specs_to_add: list[str]
) -> dict[str, Any]:
    return extract_extra_specs(
        extra_specs, specs_to_add, constants.GROUP_BOOL_SPECS
    )


def format_column_headers(columns: list[str]) -> list[str]:
    column_headers = []
    for column in columns:
        column_headers.append(
            column.replace('_', ' ').title().replace('Id', 'ID')
        )
    return column_headers


def format_share_group_type(
    share_group_type: Any, formatter: str = 'table'
) -> dict[str, Any]:
    printable_share_group_type = share_group_type._info

    is_public = printable_share_group_type.pop('is_public')

    printable_share_group_type['visibility'] = (
        'public' if is_public else 'private'
    )

    if formatter == 'table':
        printable_share_group_type['group_specs'] = format_properties(
            share_group_type.group_specs
        )
        printable_share_group_type['share_types'] = "\n".join(
            printable_share_group_type['share_types']
        )

    return printable_share_group_type
