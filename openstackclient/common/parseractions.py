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
