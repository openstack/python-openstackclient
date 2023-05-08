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

import io
import sys

from openstackclient.common import progressbar
from openstackclient.tests.unit import utils


class TestProgressBarWrapper(utils.TestCase):
    def test_iter_file_display_progress_bar(self):
        size = 98304
        file_obj = io.StringIO('X' * size)
        saved_stdout = sys.stdout
        try:
            sys.stdout = output = FakeTTYStdout()
            file_obj = progressbar.VerboseFileWrapper(file_obj, size)
            chunksize = 1024
            chunk = file_obj.read(chunksize)
            while chunk:
                chunk = file_obj.read(chunksize)
            self.assertEqual('[%s>] 100%%\n' % ('=' * 29), output.getvalue())
        finally:
            sys.stdout = saved_stdout

    def test_iter_file_no_tty(self):
        size = 98304
        file_obj = io.StringIO('X' * size)
        saved_stdout = sys.stdout
        try:
            sys.stdout = output = FakeNoTTYStdout()
            file_obj = progressbar.VerboseFileWrapper(file_obj, size)
            chunksize = 1024
            chunk = file_obj.read(chunksize)
            while chunk:
                chunk = file_obj.read(chunksize)
            # If stdout is not a tty progress bar should do nothing.
            self.assertEqual('', output.getvalue())
        finally:
            sys.stdout = saved_stdout


class FakeTTYStdout(io.StringIO):
    """A Fake stdout that try to emulate a TTY device as much as possible."""

    def isatty(self):
        return True

    def write(self, data):
        # When a CR (carriage return) is found reset file.
        if data.startswith('\r'):
            self.seek(0)
            data = data[1:]
        return io.StringIO.write(self, data)


class FakeNoTTYStdout(FakeTTYStdout):
    """A Fake stdout that is not a TTY device."""

    def isatty(self):
        return False
