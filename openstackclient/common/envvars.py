# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import os

from openstackclient.i18n import _


def bool_from_str(value, strict=False):
    true_strings = ('1', 't', 'true', 'on', 'y', 'yes')
    false_strings = ('0', 'f', 'false', 'off', 'n', 'no')

    if isinstance(value, bool):
        return value

    lowered = value.strip().lower()
    if lowered in true_strings:
        return True
    elif lowered in false_strings or not strict:
        return False

    msg = _(
        "Unrecognized value '%(value)s'; acceptable values are: %(valid)s"
    ) % {
        'value': value,
        'valid': ', '.join(
            f"'{s}'" for s in sorted(true_strings + false_strings)
        ),
    }
    raise ValueError(msg)


def boolenv(*vars, default=False):
    """Search for the first defined of possibly many bool-like env vars.

    Returns the first environment variable defined in vars, or returns the
    default.

    :param vars: Arbitrary strings to search for. Case sensitive.
    :param default: The default to return if no value found.
    :returns: A boolean corresponding to the value found, else the default if
        no value found.
    """
    for v in vars:
        value = os.environ.get(v, None)
        if value:
            return bool_from_str(value)
    return default
