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

import mock

from openstackclient.common import exceptions
from openstackclient.common import utils
from openstackclient.tests import utils as test_utils

PASSWORD = "Pa$$w0rd"
WASSPORD = "Wa$$p0rd"
DROWSSAP = "dr0w$$aP"


class TestUtils(test_utils.TestCase):

    def test_get_password_good(self):
        with mock.patch("getpass.getpass", return_value=PASSWORD):
            mock_stdin = mock.Mock()
            mock_stdin.isatty = mock.Mock()
            mock_stdin.isatty.return_value = True
            self.assertEqual(utils.get_password(mock_stdin), PASSWORD)

    def test_get_password_bad_once(self):
        answers = [PASSWORD, WASSPORD, DROWSSAP, DROWSSAP]
        with mock.patch("getpass.getpass", side_effect=answers):
            mock_stdin = mock.Mock()
            mock_stdin.isatty = mock.Mock()
            mock_stdin.isatty.return_value = True
            self.assertEqual(utils.get_password(mock_stdin), DROWSSAP)

    def test_get_password_no_tty(self):
        mock_stdin = mock.Mock()
        mock_stdin.isatty = mock.Mock()
        mock_stdin.isatty.return_value = False
        self.assertRaises(exceptions.CommandError,
                          utils.get_password,
                          mock_stdin)

    def test_get_password_cntrl_d(self):
        with mock.patch("getpass.getpass", side_effect=EOFError()):
            mock_stdin = mock.Mock()
            mock_stdin.isatty = mock.Mock()
            mock_stdin.isatty.return_value = True
            self.assertRaises(exceptions.CommandError,
                              utils.get_password,
                              mock_stdin)
