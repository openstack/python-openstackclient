# vim: tabstop=4 shiftwidth=4 softtabstop=4

import time

import mox
import testtools


class TestCase(testtools.TestCase):

    def setUp(self):
        super(TestCase, self).setUp()
        self.mox = mox.Mox()
        self._original_time = time.time
        time.time = lambda: 1234

    def tearDown(self):
        time.time = self._original_time
        self.mox.UnsetStubs()
        self.mox.VerifyAll()
        super(TestCase, self).tearDown()
