#   Copyright 2012-2013 OpenStack Foundation
#   Copyright 2013 Nebula Inc.
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

import argparse
import io
import os

import fixtures
import testtools

from openstackclient.tests.unit import fakes


class ParserException(Exception):
    pass


class CompareBySet(list):
    """Class to compare value using set."""

    def __eq__(self, other):
        return set(self) == set(other)


class TestCase(testtools.TestCase):
    # provide additional context for failures
    maxDiff = None

    def setUp(self):
        testtools.TestCase.setUp(self)

        if (
            os.environ.get("OS_STDOUT_CAPTURE") == "True"
            or os.environ.get("OS_STDOUT_CAPTURE") == "1"
        ):
            stdout = self.useFixture(fixtures.StringStream("stdout")).stream
            self.useFixture(fixtures.MonkeyPatch("sys.stdout", stdout))

        if (
            os.environ.get("OS_STDERR_CAPTURE") == "True"
            or os.environ.get("OS_STDERR_CAPTURE") == "1"
        ):
            stderr = self.useFixture(fixtures.StringStream("stderr")).stream
            self.useFixture(fixtures.MonkeyPatch("sys.stderr", stderr))

        self.log = self.useFixture(fixtures.LoggerFixture())

    def assertNotCalled(self, m, msg=None):
        """Assert a function was not called"""

        if m.called:
            if not msg:
                msg = f'method {m} should not have been called'
            self.fail(msg)


class TestCommand(TestCase):
    """Test cliff command classes"""

    def setUp(self):
        super().setUp()
        # Build up a fake app
        self.fake_stdout = fakes.FakeStdout()
        self.fake_log = fakes.FakeLog()
        self.app = fakes.FakeApp(self.fake_stdout, self.fake_log)
        self.app.client_manager = fakes.FakeClientManager()
        self.app.options = fakes.FakeOptions()

    def check_parser(self, cmd, args, verify_args):
        cmd_parser = cmd.get_parser('check_parser')
        stderr = io.StringIO()
        with fixtures.MonkeyPatch('sys.stderr', stderr):
            try:
                parsed_args = cmd_parser.parse_args(args)
            except (
                SystemExit,
                argparse.ArgumentTypeError,
                argparse.ArgumentError,
            ):
                raise ParserException(
                    f"Argument parse failed: {stderr.getvalue()}"
                )
        for av in verify_args:
            attr, expected_value = av
            if attr:
                actual_value = getattr(parsed_args, attr)
                self.assertIn(attr, parsed_args)
                self.assertEqual(
                    expected_value,
                    actual_value,
                    f'args.{attr}: expected: {expected_value}, got: '
                    f'{actual_value}',
                )
        return parsed_args
