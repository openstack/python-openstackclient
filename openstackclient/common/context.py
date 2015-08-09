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

_LOG_MESSAGE_FORMAT = ('%(asctime)s.%(msecs)03d %(process)d '
                       '%(levelname)s %(name)s [%(clouds_name)s '
                       '%(username)s %(project_name)s] %(message)s')
_LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


def set_warning_filter(log_level):
    if log_level == logging.ERROR:
        warnings.simplefilter("ignore")
    elif log_level == logging.WARNING:
        warnings.simplefilter("ignore")
    elif log_level == logging.INFO:
        warnings.simplefilter("once")


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

    log_level = logging.WARNING
    log_file = cloud_config.config.get('log_file', None)
    if log_file:
        # setup the logging level
        get_log_level = cloud_config.config.get('log_level')
        if get_log_level:
            log_level = {
                'error': logging.ERROR,
                'info': logging.INFO,
                'debug': logging.DEBUG,
            }.get(get_log_level, logging.WARNING)

        # setup the logging context
        log_cont = _LogContext(
            clouds_name=cloud_config.config.get('cloud'),
            project_name=cloud_config.auth.get('project_name'),
            username=cloud_config.auth.get('username'),
        )
        # setup the logging handler
        log_handler = _setup_handler_for_logging(
            logging.FileHandler,
            log_level,
            file_name=log_file,
            context=log_cont,
        )
        if log_level == logging.DEBUG:
            # DEBUG only.
            # setup the operation_log
            shell.enable_operation_logging = True
            shell.operation_log.setLevel(logging.DEBUG)
            shell.operation_log.addHandler(log_handler)


def _setup_handler_for_logging(handler_type, level, file_name, context):
    """Setup of the handler

       Setup of the handler for addition of the logging handler,
       changes of the logging format, change of the logging level,

        :param handler_type: type of logging handler
        :param level: logging level
        :param file_name: name of log-file
        :param context: instance of _LogContext()
        :return: logging handler
    """

    root_logger = logging.getLogger('')
    handler = None
    # Setup handler for FileHandler(--os-cloud)
    handler = logging.FileHandler(
        filename=file_name,
    )
    formatter = _LogContextFormatter(
        context=context,
        fmt=_LOG_MESSAGE_FORMAT,
        datefmt=_LOG_DATE_FORMAT,
    )
    handler.setFormatter(formatter)
    handler.setLevel(level)

    # If both `--log-file` and `--os-cloud` are specified,
    # the log is output to each file.
    root_logger.addHandler(handler)

    return handler


class _LogContext(object):
    """Helper class to represent useful information about a logging context"""

    def __init__(self, clouds_name=None, project_name=None, username=None):
        """Initialize _LogContext instance

            :param clouds_name: one of the cloud name in configuration file
            :param project_name: the project name in cloud(clouds_name)
            :param username: the user name in cloud(clouds_name)
        """

        self.clouds_name = clouds_name
        self.project_name = project_name
        self.username = username

    def to_dict(self):
        return {
            'clouds_name': self.clouds_name,
            'project_name': self.project_name,
            'username': self.username
        }


class _LogContextFormatter(logging.Formatter):
    """Customize the logging format for logging handler"""

    def __init__(self, *args, **kwargs):
        self.context = kwargs.pop('context', None)
        logging.Formatter.__init__(self, *args, **kwargs)

    def format(self, record):
        d = self.context.to_dict()
        for k, v in d.items():
            setattr(record, k, v)
        return logging.Formatter.format(self, record)
