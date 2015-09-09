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

import logging
import mock
import os

from openstackclient.common import context
from openstackclient.tests import utils


class TestContext(utils.TestCase):

    TEST_LOG_FILE = "/tmp/test_log_file"

    def setUp(self):
        super(TestContext, self).setUp()

    def tearDown(self):
        super(TestContext, self).tearDown()
        if os.path.exists(self.TEST_LOG_FILE):
            os.remove(self.TEST_LOG_FILE)

    def setup_handler_logging_level(self):
        handler_type = logging.FileHandler
        handler = logging.FileHandler(filename=self.TEST_LOG_FILE)
        handler.setLevel(logging.ERROR)
        logging.getLogger('').addHandler(handler)
        context.setup_handler_logging_level(handler_type, logging.INFO)
        self.log.info("test log")
        ld = open(self.TEST_LOG_FILE)
        line = ld.readlines()
        ld.close()
        if os.path.exists(self.TEST_LOG_FILE):
            os.remove(self.TEST_LOG_FILE)
        self.assertGreaterEqual(line.find("test log"), 0)

    @mock.patch("openstackclient.common.context._setup_handler_for_logging")
    def test_setup_logging(self, setuph):
        setuph.return_value = mock.MagicMock()
        shell = mock.MagicMock()
        cloud_config = mock.MagicMock()
        cloud_config.auth = {
            'project_name': 'heart-o-gold',
            'username': 'zaphod'
        }
        cloud_config.config = {
            'log_level': 'debug',
            'log_file': self.TEST_LOG_FILE,
            'cloud': 'megadodo'
        }
        context.setup_logging(shell, cloud_config)
        self.assertEqual(True, shell.enable_operation_logging)

    def test_log_level_from_options(self):
        opts = mock.Mock()
        opts.verbose_level = 0
        self.assertEqual(logging.ERROR, context.log_level_from_options(opts))
        opts.verbose_level = 1
        self.assertEqual(logging.WARNING, context.log_level_from_options(opts))
        opts.verbose_level = 2
        self.assertEqual(logging.INFO, context.log_level_from_options(opts))
        opts.verbose_level = 3
        self.assertEqual(logging.DEBUG, context.log_level_from_options(opts))

    def test_log_level_from_config(self):
        cfg = {'verbose_level': 0}
        self.assertEqual(logging.ERROR, context.log_level_from_config(cfg))
        cfg = {'verbose_level': 1}
        self.assertEqual(logging.WARNING, context.log_level_from_config(cfg))
        cfg = {'verbose_level': 2}
        self.assertEqual(logging.INFO, context.log_level_from_config(cfg))
        cfg = {'verbose_level': 3}
        self.assertEqual(logging.DEBUG, context.log_level_from_config(cfg))
        cfg = {'verbose_level': 1, 'log_level': 'critical'}
        self.assertEqual(logging.CRITICAL, context.log_level_from_config(cfg))
        cfg = {'verbose_level': 1, 'log_level': 'error'}
        self.assertEqual(logging.ERROR, context.log_level_from_config(cfg))
        cfg = {'verbose_level': 1, 'log_level': 'warning'}
        self.assertEqual(logging.WARNING, context.log_level_from_config(cfg))
        cfg = {'verbose_level': 1, 'log_level': 'info'}
        self.assertEqual(logging.INFO, context.log_level_from_config(cfg))
        cfg = {'verbose_level': 1, 'log_level': 'debug'}
        self.assertEqual(logging.DEBUG, context.log_level_from_config(cfg))
        cfg = {'verbose_level': 1, 'log_level': 'bogus'}
        self.assertEqual(logging.WARNING, context.log_level_from_config(cfg))
        cfg = {'verbose_level': 1, 'log_level': 'info', 'debug': True}
        self.assertEqual(logging.DEBUG, context.log_level_from_config(cfg))

    @mock.patch('warnings.simplefilter')
    def test_set_warning_filter(self, simplefilter):
        context.set_warning_filter(logging.ERROR)
        simplefilter.assert_called_with("ignore")
        context.set_warning_filter(logging.WARNING)
        simplefilter.assert_called_with("ignore")
        context.set_warning_filter(logging.INFO)
        simplefilter.assert_called_with("once")


class TestFileFormatter(utils.TestCase):
    def test_nothing(self):
        formatter = context._FileFormatter()
        self.assertEqual(('%(asctime)s.%(msecs)03d %(process)d %(levelname)s '
                          '%(name)s %(message)s'), formatter.fmt)

    def test_options(self):
        class Opts(object):
            cloud = 'cloudy'
            os_project_name = 'projecty'
            username = 'usernamey'
        options = Opts()
        formatter = context._FileFormatter(options=options)
        self.assertEqual(('%(asctime)s.%(msecs)03d %(process)d %(levelname)s '
                          '%(name)s [cloudy usernamey projecty] %(message)s'),
                         formatter.fmt)

    def test_config(self):
        config = mock.Mock()
        config.config = {'cloud': 'cloudy'}
        config.auth = {'project_name': 'projecty', 'username': 'usernamey'}
        formatter = context._FileFormatter(config=config)
        self.assertEqual(('%(asctime)s.%(msecs)03d %(process)d %(levelname)s '
                          '%(name)s [cloudy usernamey projecty] %(message)s'),
                         formatter.fmt)
