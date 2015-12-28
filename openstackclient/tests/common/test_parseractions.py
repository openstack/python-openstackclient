#   Copyright 2012-2013 OpenStack Foundation
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

import argparse

from openstackclient.common import parseractions
from openstackclient.tests import utils


class TestKeyValueAction(utils.TestCase):

    def setUp(self):
        super(TestKeyValueAction, self).setUp()

        self.parser = argparse.ArgumentParser()

        # Set up our typical usage
        self.parser.add_argument(
            '--property',
            metavar='<key=value>',
            action=parseractions.KeyValueAction,
            default={'green': '20%', 'format': '#rgb'},
            help='Property to store for this volume '
                 '(repeat option to set multiple properties)',
        )

    def test_good_values(self):
        results = self.parser.parse_args([
            '--property', 'red=',
            '--property', 'green=100%',
            '--property', 'blue=50%',
        ])

        actual = getattr(results, 'property', {})
        # All should pass through unmolested
        expect = {'red': '', 'green': '100%', 'blue': '50%', 'format': '#rgb'}
        self.assertDictEqual(expect, actual)

    def test_error_values(self):
        results = self.parser.parse_args([
            '--property', 'red',
            '--property', 'green=100%',
            '--property', 'blue',
        ])

        actual = getattr(results, 'property', {})
        # There should be no red or blue
        expect = {'green': '100%', 'format': '#rgb'}
        self.assertDictEqual(expect, actual)


class TestNonNegativeAction(utils.TestCase):

    def setUp(self):
        super(TestNonNegativeAction, self).setUp()

        self.parser = argparse.ArgumentParser()

        # Set up our typical usage
        self.parser.add_argument(
            '--foo',
            metavar='<foo>',
            type=int,
            action=parseractions.NonNegativeAction,
        )

    def test_negative_values(self):
        self.assertRaises(
            argparse.ArgumentTypeError,
            self.parser.parse_args,
            "--foo -1".split()
        )

    def test_zero_values(self):
        results = self.parser.parse_args(
            '--foo 0'.split()
        )

        actual = getattr(results, 'foo', None)
        self.assertEqual(actual, 0)

    def test_positive_values(self):
        results = self.parser.parse_args(
            '--foo 1'.split()
        )

        actual = getattr(results, 'foo', None)
        self.assertEqual(actual, 1)
