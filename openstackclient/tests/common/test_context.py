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

from openstackclient.common import context
from openstackclient.tests import utils


class TestContext(utils.TestCase):

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


class TestLogConfigurator(utils.TestCase):
    def setUp(self):
        super(TestLogConfigurator, self).setUp()
        self.options = mock.Mock()
        self.options.verbose_level = 1
        self.options.log_file = None
        self.options.debug = False
        self.root_logger = mock.Mock()
        self.root_logger.setLevel = mock.Mock()
        self.root_logger.addHandler = mock.Mock()
        self.requests_log = mock.Mock()
        self.requests_log.setLevel = mock.Mock()
        self.cliff_log = mock.Mock()
        self.cliff_log.setLevel = mock.Mock()
        self.stevedore_log = mock.Mock()
        self.stevedore_log.setLevel = mock.Mock()
        self.iso8601_log = mock.Mock()
        self.iso8601_log.setLevel = mock.Mock()
        self.loggers = [
            self.root_logger,
            self.requests_log,
            self.cliff_log,
            self.stevedore_log,
            self.iso8601_log]

    @mock.patch('logging.StreamHandler')
    @mock.patch('logging.getLogger')
    @mock.patch('openstackclient.common.context.set_warning_filter')
    def test_init(self, warning_filter, getLogger, handle):
        getLogger.side_effect = self.loggers
        console_logger = mock.Mock()
        console_logger.setFormatter = mock.Mock()
        console_logger.setLevel = mock.Mock()
        handle.return_value = console_logger

        configurator = context.LogConfigurator(self.options)

        getLogger.assert_called_with('iso8601')  # last call
        warning_filter.assert_called_with(logging.WARNING)
        self.root_logger.setLevel.assert_called_with(logging.DEBUG)
        self.root_logger.addHandler.assert_called_with(console_logger)
        self.requests_log.setLevel.assert_called_with(logging.ERROR)
        self.cliff_log.setLevel.assert_called_with(logging.ERROR)
        self.stevedore_log.setLevel.assert_called_with(logging.ERROR)
        self.iso8601_log.setLevel.assert_called_with(logging.ERROR)
        self.assertEqual(False, configurator.dump_trace)

    @mock.patch('logging.getLogger')
    @mock.patch('openstackclient.common.context.set_warning_filter')
    def test_init_no_debug(self, warning_filter, getLogger):
        getLogger.side_effect = self.loggers
        self.options.debug = True

        configurator = context.LogConfigurator(self.options)

        warning_filter.assert_called_with(logging.DEBUG)
        self.requests_log.setLevel.assert_called_with(logging.DEBUG)
        self.assertEqual(True, configurator.dump_trace)

    @mock.patch('logging.FileHandler')
    @mock.patch('logging.getLogger')
    @mock.patch('openstackclient.common.context.set_warning_filter')
    @mock.patch('openstackclient.common.context._FileFormatter')
    def test_init_log_file(self, formatter, warning_filter, getLogger, handle):
        getLogger.side_effect = self.loggers
        self.options.log_file = '/tmp/log_file'
        file_logger = mock.Mock()
        file_logger.setFormatter = mock.Mock()
        file_logger.setLevel = mock.Mock()
        handle.return_value = file_logger
        mock_formatter = mock.Mock()
        formatter.return_value = mock_formatter

        context.LogConfigurator(self.options)

        handle.assert_called_with(filename=self.options.log_file)
        self.root_logger.addHandler.assert_called_with(file_logger)
        file_logger.setFormatter.assert_called_with(mock_formatter)
        file_logger.setLevel.assert_called_with(logging.WARNING)

    @mock.patch('logging.FileHandler')
    @mock.patch('logging.getLogger')
    @mock.patch('openstackclient.common.context.set_warning_filter')
    @mock.patch('openstackclient.common.context._FileFormatter')
    def test_configure(self, formatter, warning_filter, getLogger, handle):
        getLogger.side_effect = self.loggers
        configurator = context.LogConfigurator(self.options)
        cloud_config = mock.Mock()
        config_log = '/tmp/config_log'
        cloud_config.config = {
            'log_file': config_log,
            'verbose_level': 1,
            'log_level': 'info'}
        file_logger = mock.Mock()
        file_logger.setFormatter = mock.Mock()
        file_logger.setLevel = mock.Mock()
        handle.return_value = file_logger
        mock_formatter = mock.Mock()
        formatter.return_value = mock_formatter

        configurator.configure(cloud_config)

        warning_filter.assert_called_with(logging.INFO)
        handle.assert_called_with(filename=config_log)
        self.root_logger.addHandler.assert_called_with(file_logger)
        file_logger.setFormatter.assert_called_with(mock_formatter)
        file_logger.setLevel.assert_called_with(logging.INFO)
        self.assertEqual(False, configurator.dump_trace)
