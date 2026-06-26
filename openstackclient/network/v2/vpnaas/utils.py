#    Copyright 2017 FUJITSU LIMITED
#    All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""VPN Utilities and helper functions."""

import argparse
from collections.abc import Callable
import functools
from typing import Any

from osc_lib import exceptions

from openstackclient.i18n import _

DPD_SUPPORTED_ACTIONS = [
    'hold',
    'clear',
    'restart',
    'restart-by-peer',
    'disabled',
]
DPD_SUPPORTED_KEYS = ['action', 'interval', 'timeout']

lifetime_keys = ['units', 'value']
lifetime_units = ['seconds']


def validate_dpd_dict(dpd_dict: dict[str, Any]) -> None:
    for key, value in dpd_dict.items():
        if key not in DPD_SUPPORTED_KEYS:
            message = _(
                "DPD Dictionary KeyError: "
                "Reason-Invalid DPD key : "
                "'%(key)s' not in %(supported_key)s"
            ) % {'key': key, 'supported_key': DPD_SUPPORTED_KEYS}
            raise exceptions.CommandError(message)
        if key == 'action' and value not in DPD_SUPPORTED_ACTIONS:
            message = _(
                "DPD Dictionary ValueError: "
                "Reason-Invalid DPD action : "
                "'%(key_value)s' not in %(supported_action)s"
            ) % {'key_value': value, 'supported_action': DPD_SUPPORTED_ACTIONS}
            raise exceptions.CommandError(message)
        if key in ('interval', 'timeout'):
            try:
                if int(value) <= 0:
                    raise ValueError()
            except ValueError:
                message = _(
                    "DPD Dictionary ValueError: "
                    "Reason-Invalid positive integer value: "
                    "'%(key)s' = %(value)s"
                ) % {'key': key, 'value': value}
                raise exceptions.CommandError(message)
            else:
                dpd_dict[key] = int(value)
    return


def validate_lifetime_dict(lifetime_dict: dict[str, Any]) -> None:

    for key, value in lifetime_dict.items():
        if key not in lifetime_keys:
            message = _(
                "Lifetime Dictionary KeyError: "
                "Reason-Invalid unit key : "
                "'%(key)s' not in %(supported_key)s"
            ) % {'key': key, 'supported_key': lifetime_keys}
            raise exceptions.CommandError(message)
        if key == 'units' and value not in lifetime_units:
            message = _(
                "Lifetime Dictionary ValueError: "
                "Reason-Invalid units : "
                "'%(key_value)s' not in %(supported_units)s"
            ) % {'key_value': key, 'supported_units': lifetime_units}
            raise exceptions.CommandError(message)
        if key == 'value':
            try:
                if int(value) < 60:
                    raise ValueError()
            except ValueError:
                message = _(
                    "Lifetime Dictionary ValueError: "
                    "Reason-Invalid value should be at least 60:"
                    "'%(key_value)s' = %(value)s"
                ) % {'key_value': key, 'value': value}
                raise exceptions.CommandError(message)
            else:
                lifetime_dict['value'] = int(value)
    return


def lifetime_help(policy: str) -> str:
    lifetime = (
        _(
            "%s lifetime attributes. "
            "'units'-seconds, default:seconds. "
            "'value'-non negative integer, default:3600."
        )
        % policy
    )
    return lifetime


def dpd_help(policy: str) -> str:
    dpd = (
        _(
            " %s Dead Peer Detection attributes."
            " 'action'-hold,clear,disabled,restart,restart-by-peer."
            " 'interval' and 'timeout' are non negative integers. "
            " 'interval' should be less than 'timeout' value. "
            " 'action', default:hold 'interval', default:30, "
            " 'timeout', default:120."
        )
        % policy.capitalize()
    )
    return dpd


def str2dict(
    strdict: str,
    required_keys: list[str] | None = None,
    optional_keys: list[str] | None = None,
) -> dict[str, str]:
    """Convert key1=value1,key2=value2,... string into dictionary.

    :param strdict: string in the form of key1=value1,key2=value2
    :param required_keys: list of required keys. All keys in this list must be
                       specified. Otherwise ArgumentTypeError will be raised.
                       If this parameter is unspecified, no required key check
                       will be done.
    :param optional_keys: list of optional keys.
                       This parameter is used for valid key check.
                       When at least one of required_keys and optional_keys,
                       a key must be a member of either of required_keys or
                       optional_keys. Otherwise, ArgumentTypeError will be
                       raised. When both required_keys and optional_keys are
                       unspecified, no valid key check will be done.
    """
    result = {}
    if strdict:
        i = 0
        kvlist = []
        for kv in strdict.split(','):
            if '=' in kv:
                kvlist.append(kv)
                i += 1
            elif i == 0:
                msg = _("missing value for key '%s'")
                raise argparse.ArgumentTypeError(msg % kv)
            else:
                kvlist[i - 1] = f"{kvlist[i - 1]},{kv}"
        for kv in kvlist:
            key, sep, value = kv.partition('=')
            if not sep:
                msg = _("invalid key-value '%s', expected format: key=value")
                raise argparse.ArgumentTypeError(msg % kv)
            result[key] = value
    valid_keys = set(required_keys or []) | set(optional_keys or [])
    if valid_keys:
        invalid_keys = [k for k in result if k not in valid_keys]
        if invalid_keys:
            msg = _(
                "Invalid key(s) '%(invalid_keys)s' specified. "
                "Valid key(s): '%(valid_keys)s'."
            )
            raise argparse.ArgumentTypeError(
                msg
                % {
                    'invalid_keys': ', '.join(sorted(invalid_keys)),
                    'valid_keys': ', '.join(sorted(valid_keys)),
                }
            )
    if required_keys:
        not_found_keys = [k for k in required_keys if k not in result]
        if not_found_keys:
            msg = _("Required key(s) '%s' not specified.")
            raise argparse.ArgumentTypeError(msg % ', '.join(not_found_keys))
    return result


def str2dict_type(
    optional_keys: list[str] | None = None,
    required_keys: list[str] | None = None,
) -> Callable[[str], dict[str, str]]:
    return functools.partial(
        str2dict, optional_keys=optional_keys, required_keys=required_keys
    )
