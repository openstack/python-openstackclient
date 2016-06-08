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

"""Application logging"""

import logging
import sys
import warnings


def get_loggers():
    loggers = {}
    for logkey in logging.Logger.manager.loggerDict.keys():
        loggers[logkey] = logging.getLevelName(logging.getLogger(logkey).level)
    return loggers


def log_level_from_options(options):
    # if --debug, --quiet or --verbose is not specified,
    # the default logging level is warning
    log_level = logging.WARNING
    if options.verbose_level == 0:
        # --quiet
        log_level = logging.ERROR
    elif options.verbose_level == 2:
        # One --verbose
        log_level = logging.INFO
    elif options.verbose_level >= 3:
        # Two or more --verbose
        log_level = logging.DEBUG
    return log_level


def log_level_from_string(level_string):
    log_level = {
        'critical': logging.CRITICAL,
        'error': logging.ERROR,
        'warning': logging.WARNING,
        'info': logging.INFO,
        'debug': logging.DEBUG,
    }.get(level_string, logging.WARNING)
    return log_level


def log_level_from_config(config):
    # Check the command line option
    verbose_level = config.get('verbose_level')
    if config.get('debug', False):
        verbose_level = 3
    if verbose_level == 0:
        verbose_level = 'error'
    elif verbose_level == 1:
        # If a command line option has not been specified, check the
        # configuration file
        verbose_level = config.get('log_level', 'warning')
    elif verbose_level == 2:
        verbose_level = 'info'
    else:
        verbose_level = 'debug'
    return log_level_from_string(verbose_level)


def set_warning_filter(log_level):
    if log_level == logging.ERROR:
        warnings.simplefilter("ignore")
    elif log_level == logging.WARNING:
        warnings.simplefilter("ignore")
    elif log_level == logging.INFO:
        warnings.simplefilter("once")


class _FileFormatter(logging.Formatter):
    """Customize the logging format for logging handler"""
    _LOG_MESSAGE_BEGIN = (
        '%(asctime)s.%(msecs)03d %(process)d %(levelname)s %(name)s ')
    _LOG_MESSAGE_CONTEXT = '[%(cloud)s %(username)s %(project)s] '
    _LOG_MESSAGE_END = '%(message)s'
    _LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

    def __init__(self, options=None, config=None, **kwargs):
        context = {}
        if options:
            context = {
                'cloud': getattr(options, 'cloud', ''),
                'project': getattr(options, 'os_project_name', ''),
                'username': getattr(options, 'username', ''),
            }
        elif config:
            context = {
                'cloud': config.config.get('cloud', ''),
                'project': config.auth.get('project_name', ''),
                'username': config.auth.get('username', ''),
            }
        if context:
            self.fmt = (self._LOG_MESSAGE_BEGIN +
                        (self._LOG_MESSAGE_CONTEXT % context) +
                        self._LOG_MESSAGE_END)
        else:
            self.fmt = self._LOG_MESSAGE_BEGIN + self._LOG_MESSAGE_END
        logging.Formatter.__init__(self, self.fmt, self._LOG_DATE_FORMAT)


class LogConfigurator(object):

    _CONSOLE_MESSAGE_FORMAT = '%(message)s'

    def __init__(self, options):
        self.root_logger = logging.getLogger('')
        self.root_logger.setLevel(logging.DEBUG)

        # Force verbose_level 3 on --debug
        self.dump_trace = False
        if options.debug:
            options.verbose_level = 3
            self.dump_trace = True

        # Always send higher-level messages to the console via stderr
        self.console_logger = logging.StreamHandler(sys.stderr)
        log_level = log_level_from_options(options)
        self.console_logger.setLevel(log_level)
        formatter = logging.Formatter(self._CONSOLE_MESSAGE_FORMAT)
        self.console_logger.setFormatter(formatter)
        self.root_logger.addHandler(self.console_logger)

        # Set the warning filter now
        set_warning_filter(log_level)

        # Set up logging to a file
        self.file_logger = None
        log_file = options.log_file
        if log_file:
            self.file_logger = logging.FileHandler(filename=log_file)
            self.file_logger.setFormatter(_FileFormatter(options=options))
            self.file_logger.setLevel(log_level)
            self.root_logger.addHandler(self.file_logger)

        # Requests logs some stuff at INFO that we don't want
        # unless we have DEBUG
        requests_log = logging.getLogger("requests")

        # Other modules we don't want DEBUG output for
        cliff_log = logging.getLogger('cliff')
        stevedore_log = logging.getLogger('stevedore')
        iso8601_log = logging.getLogger("iso8601")

        if options.debug:
            # --debug forces traceback
            requests_log.setLevel(logging.DEBUG)
        else:
            requests_log.setLevel(logging.ERROR)

        cliff_log.setLevel(logging.ERROR)
        stevedore_log.setLevel(logging.ERROR)
        iso8601_log.setLevel(logging.ERROR)

    def configure(self, cloud_config):
        log_level = log_level_from_config(cloud_config.config)
        set_warning_filter(log_level)
        self.dump_trace = cloud_config.config.get('debug', self.dump_trace)
        self.console_logger.setLevel(log_level)

        log_file = cloud_config.config.get('log_file')
        if log_file:
            if not self.file_logger:
                self.file_logger = logging.FileHandler(filename=log_file)
            self.file_logger.setFormatter(_FileFormatter(config=cloud_config))
            self.file_logger.setLevel(log_level)
            self.root_logger.addHandler(self.file_logger)

        logconfig = cloud_config.config.get('logging')
        if logconfig:
            highest_level = logging.NOTSET
            for k in logconfig.keys():
                level = log_level_from_string(logconfig[k])
                logging.getLogger(k).setLevel(level)
                if (highest_level < level):
                    highest_level = level
            self.console_logger.setLevel(highest_level)
            if self.file_logger:
                self.file_logger.setLevel(highest_level)
            # loggers that are not set will use the handler level, so we
            # need to set the global level for all the loggers
            for logkey in logging.Logger.manager.loggerDict.keys():
                logger = logging.getLogger(logkey)
                if logger.level == logging.NOTSET:
                    logger.setLevel(log_level)
