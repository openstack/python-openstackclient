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

    @mock.patch('warnings.simplefilter')
    def test_set_warning_filter(self, simplefilter):
        context.set_warning_filter(logging.ERROR)
        simplefilter.assert_called_with("ignore")
        context.set_warning_filter(logging.WARNING)
        simplefilter.assert_called_with("ignore")
        context.set_warning_filter(logging.INFO)
        simplefilter.assert_called_with("once")


class Test_LogContext(utils.TestCase):
    def setUp(self):
        super(Test_LogContext, self).setUp()

    def test_context(self):
        ctx = context._LogContext()
        self.assertTrue(ctx)

    def test_context_to_dict(self):
        ctx = context._LogContext('cloudsName', 'projectName', 'userNmae')
        ctx_dict = ctx.to_dict()
        self.assertEqual('cloudsName', ctx_dict['clouds_name'])
        self.assertEqual('projectName', ctx_dict['project_name'])
        self.assertEqual('userNmae', ctx_dict['username'])


class Test_LogContextFormatter(utils.TestCase):
    def setUp(self):
        super(Test_LogContextFormatter, self).setUp()
        self.ctx = context._LogContext('cloudsName', 'projectName', 'userNmae')
        self.addfmt = "%(clouds_name)s %(project_name)s %(username)s"

    def test_contextrrormatter(self):
        ctxfmt = context._LogContextFormatter()
        self.assertTrue(ctxfmt)

    def test_context_format(self):
        record = mock.MagicMock()
        logging.Formatter.format = mock.MagicMock()
        logging.Formatter.format.return_value = record

        ctxfmt = context._LogContextFormatter(context=self.ctx,
                                              fmt=self.addfmt)
        addctx = ctxfmt.format(record)
        self.assertEqual('cloudsName', addctx.clouds_name)
        self.assertEqual('projectName', addctx.project_name)
        self.assertEqual('userNmae', addctx.username)
