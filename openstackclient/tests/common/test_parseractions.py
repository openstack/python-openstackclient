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
    def test_good_values(self):
        parser = argparse.ArgumentParser()

        # Set up our typical usage
        parser.add_argument(
            '--property',
            metavar='<key=value>',
            action=parseractions.KeyValueAction,
            help='Property to store for this volume '
                 '(repeat option to set multiple properties)',
        )

        results = parser.parse_args([
            '--property', 'red=',
            '--property', 'green=100%',
            '--property', 'blue=50%',
        ])

        actual = getattr(results, 'property', {})
        # All should pass through unmolested
        expect = {'red': '', 'green': '100%', 'blue': '50%'}
        self.assertDictEqual(expect, actual)

    def test_default_values(self):
        parser = argparse.ArgumentParser()

        # Set up our typical usage
        parser.add_argument(
            '--property',
            metavar='<key=value>',
            action=parseractions.KeyValueAction,
            default={'green': '20%', 'format': '#rgb'},
            help='Property to store for this volume '
                 '(repeat option to set multiple properties)',
        )

        results = parser.parse_args([
            '--property', 'red=',
            '--property', 'green=100%',
            '--property', 'blue=50%',
        ])

        actual = getattr(results, 'property', {})
        # Verify green default is changed, format default is unchanged
        expect = {'red': '', 'green': '100%', 'blue': '50%', 'format': '#rgb'}
        self.assertDictEqual(expect, actual)

    def test_error_values(self):
        parser = argparse.ArgumentParser()

        # Set up our typical usage
        parser.add_argument(
            '--property',
            metavar='<key=value>',
            action=parseractions.KeyValueAction,
            default={'green': '20%', 'blue': '40%'},
            help='Property to store for this volume '
                 '(repeat option to set multiple properties)',
        )

        results = parser.parse_args([
            '--property', 'red',
            '--property', 'green=100%',
            '--property', 'blue',
        ])

        failhere = None
        actual = getattr(results, 'property', {})
        # Verify non-existent red key
        try:
            failhere = actual['red']
        except Exception as e:
            self.assertTrue(type(e) == KeyError)
        # Verify removal of blue key
        try:
            failhere = actual['blue']
        except Exception as e:
            self.assertTrue(type(e) == KeyError)
        # There should be no red or blue
        expect = {'green': '100%'}
        self.assertDictEqual(expect, actual)
        self.assertEqual(None, failhere)
