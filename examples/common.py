#!/usr/bin/env python
# common.py - Common bits for API examples

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""
API Examples

This is a collection of common functions used by the example scripts.
It may also be run directly as a script to do basic testing of itself.

common.object_parser() provides the common set of command-line arguments
used in the library CLIs for setting up authentication.  This should make
playing with the example scripts against a running OpenStack simpler.

common.configure_logging() provides the same basic logging control as
the OSC shell.

common.make_session() does the minimal loading of a Keystone authentication
plugin and creates a Keystone client Session.

"""

import argparse
import logging
import os
import sys
import traceback

from keystoneclient import session as ksc_session

from openstackclient.api import auth


CONSOLE_MESSAGE_FORMAT = '%(levelname)s: %(name)s %(message)s'
DEFAULT_VERBOSE_LEVEL = 1
USER_AGENT = 'osc-examples'

PARSER_DESCRIPTION = 'A demonstration framework'

DEFAULT_IDENTITY_API_VERSION = '2.0'

_logger = logging.getLogger(__name__)

# --debug sets this True
dump_stack_trace = False


# Generally useful stuff often found in a utils module

def env(*vars, **kwargs):
    """Search for the first defined of possibly many env vars

    Returns the first environment variable defined in vars, or
    returns the default defined in kwargs.

    """
    for v in vars:
        value = os.environ.get(v, None)
        if value:
            return value
    return kwargs.get('default', '')


# Common Example functions

def base_parser(parser):
    """Set up some of the common CLI options

    These are the basic options that match the library CLIs so
    command-line/environment setups for those also work with these
    demonstration programs.

    """

    # Global arguments
    parser.add_argument(
        '--os-cloud',
        metavar='<cloud-config-name>',
        dest='cloud',
        default=env('OS_CLOUD'),
        help='Cloud name in clouds.yaml (Env: OS_CLOUD)',
    )
    parser.add_argument(
        '--os-region-name',
        metavar='<auth-region-name>',
        dest='region_name',
        default=env('OS_REGION_NAME'),
        help='Authentication region name (Env: OS_REGION_NAME)',
    )
    parser.add_argument(
        '--os-cacert',
        metavar='<ca-bundle-file>',
        dest='cacert',
        default=env('OS_CACERT'),
        help='CA certificate bundle file (Env: OS_CACERT)',
    )
    parser.add_argument(
        '--os-default-domain',
        metavar='<auth-domain>',
        default='default',
        help='Default domain ID, default=default (Env: OS_DEFAULT_DOMAIN)',
    )
    verify_group = parser.add_mutually_exclusive_group()
    verify_group.add_argument(
        '--verify',
        action='store_true',
        help='Verify server certificate (default)',
    )
    verify_group.add_argument(
        '--insecure',
        action='store_true',
        help='Disable server certificate verification',
    )
    parser.add_argument(
        '--timing',
        default=False,
        action='store_true',
        help="Print API call timing info",
    )
    parser.add_argument(
        '-v', '--verbose',
        action='count',
        dest='verbose_level',
        default=1,
        help='Increase verbosity of output. Can be repeated.',
    )
    parser.add_argument(
        '--debug',
        default=False,
        action='store_true',
        help='show tracebacks on errors',
    )
    parser.add_argument(
        'rest',
        nargs='*',
        help='the rest of the args',
    )
    return parser


def configure_logging(opts):
    """Typical app logging setup

    Based on OSC/cliff

    """

    global dump_stack_trace

    root_logger = logging.getLogger('')

    # Requests logs some stuff at INFO that we don't want
    # unless we have DEBUG
    requests_log = logging.getLogger("requests")
    requests_log.setLevel(logging.ERROR)

    # Other modules we don't want DEBUG output for so
    # don't reset them below
    iso8601_log = logging.getLogger("iso8601")
    iso8601_log.setLevel(logging.ERROR)

    # Always send higher-level messages to the console via stderr
    console = logging.StreamHandler(sys.stderr)
    formatter = logging.Formatter(CONSOLE_MESSAGE_FORMAT)
    console.setFormatter(formatter)
    root_logger.addHandler(console)

    # Set logging to the requested level
    dump_stack_trace = False
    if opts.verbose_level == 0:
        # --quiet
        root_logger.setLevel(logging.ERROR)
    elif opts.verbose_level == 1:
        # This is the default case, no --debug, --verbose or --quiet
        root_logger.setLevel(logging.WARNING)
    elif opts.verbose_level == 2:
        # One --verbose
        root_logger.setLevel(logging.INFO)
    elif opts.verbose_level >= 3:
        # Two or more --verbose
        root_logger.setLevel(logging.DEBUG)
        requests_log.setLevel(logging.DEBUG)

    if opts.debug:
        # --debug forces traceback
        dump_stack_trace = True
        root_logger.setLevel(logging.DEBUG)
        requests_log.setLevel(logging.DEBUG)

    return


def make_session(opts, **kwargs):
    """Create our base session using simple auth from ksc plugins

    The arguments required in opts varies depending on the auth plugin
    that is used.  This example assumes Identity v2 will be used
    and selects token auth if both os_url and os_token have been
    provided, otherwise it uses password.

    :param Namespace opts:
        A parser options Namespace containing the authentication
        options to be used
    :param dict kwargs:
        Additional options passed directly to Session constructor
    """

    # If no auth type is named by the user, select one based on
    # the supplied options
    auth_plugin_name = auth.select_auth_plugin(opts)

    (auth_plugin, auth_params) = auth.build_auth_params(
        auth_plugin_name,
        opts,
    )
    auth_p = auth_plugin.load_from_options(**auth_params)

    session = ksc_session.Session(
        auth=auth_p,
        **kwargs
    )

    return session


# Top-level functions

def run(opts):
    """Default run command"""

    # Do some basic testing here
    sys.stdout.write("Default run command\n")
    sys.stdout.write("Verbose level: %s\n" % opts.verbose_level)
    sys.stdout.write("Debug: %s\n" % opts.debug)
    sys.stdout.write("dump_stack_trace: %s\n" % dump_stack_trace)


def setup():
    """Parse command line and configure logging"""
    opts = base_parser(
        auth.build_auth_plugins_option_parser(
            argparse.ArgumentParser(description='Object API Example')
        )
    ).parse_args()
    configure_logging(opts)
    return opts


def main(opts, run):
    try:
        return run(opts)
    except Exception as e:
        if dump_stack_trace:
            _logger.error(traceback.format_exc(e))
        else:
            _logger.error('Exception raised: ' + str(e))
        return 1


if __name__ == "__main__":
    opts = setup()
    sys.exit(main(opts, run))
