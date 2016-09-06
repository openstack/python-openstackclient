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

# NOTE(dtroyer): This file is deprecated in Jun 2016, remove after 4.x release
#                or Jun 2017.

import argparse

from openstackclient.common import parseractions
from openstackclient.tests.unit import utils


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
        self.assertEqual(expect, actual)

    def test_error_values(self):
        self.assertRaises(
            argparse.ArgumentTypeError,
            self.parser.parse_args,
            [
                '--property', 'red',
            ]
        )


class TestMultiKeyValueAction(utils.TestCase):

    def setUp(self):
        super(TestMultiKeyValueAction, self).setUp()

        self.parser = argparse.ArgumentParser()

        # Set up our typical usage
        self.parser.add_argument(
            '--test',
            metavar='req1=xxx,req2=yyy',
            action=parseractions.MultiKeyValueAction,
            dest='test',
            default=None,
            required_keys=['req1', 'req2'],
            optional_keys=['opt1', 'opt2'],
            help='Test'
        )

    def test_good_values(self):
        results = self.parser.parse_args([
            '--test', 'req1=aaa,req2=bbb',
            '--test', 'req1=,req2=',
        ])

        actual = getattr(results, 'test', [])
        expect = [
            {'req1': 'aaa', 'req2': 'bbb'},
            {'req1': '', 'req2': ''},
        ]
        self.assertItemsEqual(expect, actual)

    def test_empty_required_optional(self):
        self.parser.add_argument(
            '--test-empty',
            metavar='req1=xxx,req2=yyy',
            action=parseractions.MultiKeyValueAction,
            dest='test_empty',
            default=None,
            required_keys=[],
            optional_keys=[],
            help='Test'
        )

        results = self.parser.parse_args([
            '--test-empty', 'req1=aaa,req2=bbb',
            '--test-empty', 'req1=,req2=',
        ])

        actual = getattr(results, 'test_empty', [])
        expect = [
            {'req1': 'aaa', 'req2': 'bbb'},
            {'req1': '', 'req2': ''},
        ]
        self.assertItemsEqual(expect, actual)

    def test_error_values_with_comma(self):
        self.assertRaises(
            argparse.ArgumentTypeError,
            self.parser.parse_args,
            [
                '--test', 'mmm,nnn=zzz',
            ]
        )

    def test_error_values_without_comma(self):
        self.assertRaises(
            argparse.ArgumentTypeError,
            self.parser.parse_args,
            [
                '--test', 'mmmnnn',
            ]
        )

    def test_missing_key(self):
        self.assertRaises(
            argparse.ArgumentTypeError,
            self.parser.parse_args,
            [
                '--test', 'req2=ddd',
            ]
        )

    def test_invalid_key(self):
        self.assertRaises(
            argparse.ArgumentTypeError,
            self.parser.parse_args,
            [
                '--test', 'req1=aaa,req2=bbb,aaa=req1',
            ]
        )

    def test_required_keys_not_list(self):
        self.assertRaises(
            TypeError,
            self.parser.add_argument,
            '--test-required-dict',
            metavar='req1=xxx,req2=yyy',
            action=parseractions.MultiKeyValueAction,
            dest='test_required_dict',
            default=None,
            required_keys={'aaa': 'bbb'},
            optional_keys=['opt1', 'opt2'],
            help='Test'
        )

    def test_optional_keys_not_list(self):
        self.assertRaises(
            TypeError,
            self.parser.add_argument,
            '--test-optional-dict',
            metavar='req1=xxx,req2=yyy',
            action=parseractions.MultiKeyValueAction,
            dest='test_optional_dict',
            default=None,
            required_keys=['req1', 'req2'],
            optional_keys={'aaa': 'bbb'},
            help='Test'
        )


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
