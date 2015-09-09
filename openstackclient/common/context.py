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

"""Context and Formatter"""

import logging
import warnings


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

    log_level = {
        'critical': logging.CRITICAL,
        'error': logging.ERROR,
        'warning': logging.WARNING,
        'info': logging.INFO,
        'debug': logging.DEBUG,
    }.get(verbose_level, logging.WARNING)
    return log_level


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


def setup_handler_logging_level(handler_type, level):
    """Setup of the handler for set the logging level

        :param handler_type: type of logging handler
        :param level: logging level
        :return: None
    """
    # Set the handler logging level of FileHandler(--log-file)
    # and StreamHandler
    for h in logging.getLogger('').handlers:
        if type(h) is handler_type:
            h.setLevel(level)


def setup_logging(shell, cloud_config):
    """Get one cloud configuration from configuration file and setup logging

        :param shell: instance of openstackclient shell
        :param cloud_config:
            instance of the cloud specified by --os-cloud
            in the configuration file
        :return: None
    """

    log_level = log_level_from_config(cloud_config.config)
    set_warning_filter(log_level)

    log_file = cloud_config.config.get('log_file', None)
    if log_file:
        # setup the logging context
        formatter = _FileFormatter(config=cloud_config)
        # setup the logging handler
        log_handler = _setup_handler_for_logging(
            logging.FileHandler,
            log_level,
            file_name=log_file,
            formatter=formatter,
        )
        if log_level == logging.DEBUG:
            # DEBUG only.
            # setup the operation_log
            shell.enable_operation_logging = True
            shell.operation_log.setLevel(logging.DEBUG)
            shell.operation_log.addHandler(log_handler)


def _setup_handler_for_logging(handler_type, level, file_name, formatter):
    """Setup of the handler

       Setup of the handler for addition of the logging handler,
       changes of the logging format, change of the logging level,

        :param handler_type: type of logging handler
        :param level: logging level
        :param file_name: name of log-file
        :param formatter: instance of logging.Formatter
        :return: logging handler
    """

    root_logger = logging.getLogger('')
    handler = None
    # Setup handler for FileHandler(--os-cloud)
    handler = logging.FileHandler(
        filename=file_name,
    )
    handler.setFormatter(formatter)
    handler.setLevel(level)

    # If both `--log-file` and `--os-cloud` are specified,
    # the log is output to each file.
    root_logger.addHandler(handler)

    return handler
