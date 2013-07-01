#   Copyright 2012-2013 OpenStack, LLC.
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

import os

import fixtures
import sys
import testtools


class TestCase(testtools.TestCase):
    def setUp(self):
        testtools.TestCase.setUp(self)

        if (os.environ.get("OS_STDOUT_NOCAPTURE") == "True" and
                os.environ.get("OS_STDOUT_NOCAPTURE") == "1"):
            stdout = self.useFixture(fixtures.StringStream("stdout")).stream
            self.useFixture(fixtures.MonkeyPatch("sys.stdout", stdout))

        if (os.environ.get("OS_STDERR_NOCAPTURE") == "True" and
                os.environ.get("OS_STDERR_NOCAPTURE") == "1"):
            stderr = self.useFixture(fixtures.StringStream("stderr")).stream
            self.useFixture(fixtures.MonkeyPatch("sys.stderr", stderr))

    # 2.6 doesn't have the assert dict equals so make sure that it exists
    if tuple(sys.version_info)[0:2] < (2, 7):

        def assertIsInstance(self, obj, cls, msg=None):
            """Same as self.assertTrue(isinstance(obj, cls)), with a nicer
            default message
            """
            if not isinstance(obj, cls):
                standardMsg = '%s is not an instance of %r' % (obj, cls)
                self.fail(self._formatMessage(msg, standardMsg))

        def assertDictEqual(self, d1, d2, msg=None):
            # Simple version taken from 2.7
            self.assertIsInstance(d1, dict,
                                  'First argument is not a dictionary')
            self.assertIsInstance(d2, dict,
                                  'Second argument is not a dictionary')
            if d1 != d2:
                if msg:
                    self.fail(msg)
                else:
                    standardMsg = '%r != %r' % (d1, d2)
                    self.fail(standardMsg)
