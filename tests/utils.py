# vim: tabstop=4 shiftwidth=4 softtabstop=4

import time

import testtools


class TestCase(testtools.TestCase):

    def setUp(self):
        super(TestCase, self).setUp()
        self._original_time = time.time
        time.time = lambda: 1234

    def tearDown(self):
        time.time = self._original_time
        super(TestCase, self).tearDown()
