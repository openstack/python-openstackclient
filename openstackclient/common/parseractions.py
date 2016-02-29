#   Copyright 2013 OpenStack Foundation
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

"""argparse Custom Actions"""

import argparse

from openstackclient.i18n import _


class KeyValueAction(argparse.Action):
    """A custom action to parse arguments as key=value pairs

    Ensures that ``dest`` is a dict
    """

    def __call__(self, parser, namespace, values, option_string=None):
        # Make sure we have an empty dict rather than None
        if getattr(namespace, self.dest, None) is None:
            setattr(namespace, self.dest, {})

        # Add value if an assignment else remove it
        if '=' in values:
            getattr(namespace, self.dest, {}).update([values.split('=', 1)])
        else:
            getattr(namespace, self.dest, {}).pop(values, None)


class MultiKeyValueAction(argparse.Action):
    """A custom action to parse arguments as key1=value1,key2=value2 pairs

    Ensure that ``dest`` is a list. The list will finally contain multiple
    dicts, with key=value pairs in them.

    NOTE: The arguments string should be a comma separated key-value pairs.
    And comma(',') and equal('=') may not be used in the key or value.
    """

    def __init__(self, option_strings, dest, nargs=None,
                 required_keys=None, optional_keys=None, **kwargs):
        """Initialize the action object, and parse customized options

        Required keys and optional keys can be specified when initializing
        the action to enable the key validation. If none of them specified,
        the key validation will be skipped.

        :param required_keys: a list of required keys
        :param optional_keys: a list of optional keys
        """
        if nargs:
            raise ValueError("Parameter 'nargs' is not allowed, but got %s"
                             % nargs)

        super(MultiKeyValueAction, self).__init__(option_strings,
                                                  dest, **kwargs)

        # required_keys: A list of keys that is required. None by default.
        if required_keys and not isinstance(required_keys, list):
            raise TypeError("'required_keys' must be a list")
        self.required_keys = set(required_keys or [])

        # optional_keys: A list of keys that is optional. None by default.
        if optional_keys and not isinstance(optional_keys, list):
            raise TypeError("'optional_keys' must be a list")
        self.optional_keys = set(optional_keys or [])

    def __call__(self, parser, namespace, values, metavar=None):
        # Make sure we have an empty list rather than None
        if getattr(namespace, self.dest, None) is None:
            setattr(namespace, self.dest, [])

        params = {}
        for kv in values.split(','):
            # Add value if an assignment else raise ArgumentTypeError
            if '=' in kv:
                params.update([kv.split('=', 1)])
            else:
                msg = ("Expected key=value pairs separated by comma, "
                       "but got: %s" % (str(kv)))
                raise argparse.ArgumentTypeError(msg)

        # Check key validation
        valid_keys = self.required_keys | self.optional_keys
        if valid_keys:
            invalid_keys = [k for k in params if k not in valid_keys]
            if invalid_keys:
                msg = _("Invalid keys %(invalid_keys)s specified.\n"
                        "Valid keys are: %(valid_keys)s.")
                raise argparse.ArgumentTypeError(
                    msg % {'invalid_keys': ', '.join(invalid_keys),
                           'valid_keys': ', '.join(valid_keys)}
                )

        if self.required_keys:
            missing_keys = [k for k in self.required_keys if k not in params]
            if missing_keys:
                msg = _("Missing required keys %(missing_keys)s.\n"
                        "Required keys are: %(required_keys)s.")
                raise argparse.ArgumentTypeError(
                    msg % {'missing_keys': ', '.join(missing_keys),
                           'required_keys': ', '.join(self.required_keys)}
                )

        # Update the dest dict
        getattr(namespace, self.dest, []).append(params)


class RangeAction(argparse.Action):
    """A custom action to parse a single value or a range of values

    Parses single integer values or a range of integer values delimited
    by a colon and returns a tuple of integers:
    '4' sets ``dest`` to (4, 4)
    '6:9' sets ``dest`` to (6, 9)
    """

    def __call__(self, parser, namespace, values, option_string=None):
        range = values.split(':')
        if len(range) == 0:
            # Nothing passed, return a zero default
            setattr(namespace, self.dest, (0, 0))
        elif len(range) == 1:
            # Only a single value is present
            setattr(namespace, self.dest, (int(range[0]), int(range[0])))
        elif len(range) == 2:
            # Range of two values
            if int(range[0]) <= int(range[1]):
                setattr(namespace, self.dest, (int(range[0]), int(range[1])))
            else:
                msg = "Invalid range, %s is not less than %s" % \
                    (range[0], range[1])
                raise argparse.ArgumentError(self, msg)
        else:
            # Too many values
            msg = "Invalid range, too many values"
            raise argparse.ArgumentError(self, msg)


class NonNegativeAction(argparse.Action):
    """A custom action to check whether the value is non-negative or not

    Ensures the value is >= 0.
    """

    def __call__(self, parser, namespace, values, option_string=None):
        try:
            assert(int(values) >= 0)
            setattr(namespace, self.dest, values)
        except Exception:
            msg = "%s expected a non-negative integer" % (str(option_string))
            raise argparse.ArgumentTypeError(msg)
