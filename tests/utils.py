import os

import fixtures
import testtools


class TestCase(testtools.TestCase):
    def setUp(self):
        super(TestCase, self).setUp()
        if (os.environ.get("OS_STDOUT_NOCAPTURE") == "True" and
                os.environ.get("OS_STDOUT_NOCAPTURE") == "1"):
            stdout = self.useFixture(fixtures.StringStream("stdout")).stream
            self.useFixture(fixtures.MonkeyPatch("sys.stdout", stdout))
        if (os.environ.get("OS_STDERR_NOCAPTURE") == "True" and
                os.environ.get("OS_STDERR_NOCAPTURE") == "1"):
            stderr = self.useFixture(fixtures.StringStream("stderr")).stream
            self.useFixture(fixtures.MonkeyPatch("sys.stderr", stderr))

    def tearDown(self):
        super(TestCase, self).tearDown()
