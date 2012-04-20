# Copyright 2011 OpenStack LLC.
# All Rights Reserved
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
#
# vim: tabstop=4 shiftwidth=4 softtabstop=4

"""
Command-line interface to the OpenStack Identity, Compute and Storage APIs
"""

import argparse
import httplib2
import os
import sys

from openstackclient.common import utils


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


class OpenStackShell(object):

    def _find_actions(self, subparsers, actions_module):
        if self.debug:
            print "_find_actions(module: %s)" % actions_module
        for attr in (a for a in dir(actions_module) if a.startswith('do_')):
            # I prefer to be hypen-separated instead of underscores.
            command = attr[3:].replace('_', '-')
            cmd = command.split('-', 1)
            action = cmd[0]
            if len(cmd) > 1:
                subject = cmd[1]
            else:
                subject = ''
            callback = getattr(actions_module, attr)
            desc = callback.__doc__ or ''
            help = desc.strip().split('\n')[0]
            arguments = getattr(callback, 'arguments', [])

            if self.debug:
                print " command: %s" % command
                print " action: %s" % action
                print " subject: %s" % subject
                print " arguments: %s" % arguments

            subparser = subparsers.add_parser(command,
                help=help,
                description=desc,
                add_help=False,
                formatter_class=OpenStackHelpFormatter
            )
            subparser.add_argument('-h', '--help',
                action='help',
                help=argparse.SUPPRESS,
            )
            self.subcommands[command] = subparser
            for (args, kwargs) in arguments:
                subparser.add_argument(*args, **kwargs)
            subparser.set_defaults(func=callback)

    @utils.arg('command', metavar='<subcommand>', nargs='?',
                          help='Display help for <subcommand>')
    def do_help(self, args):
        """
        Display help about this program or one of its subcommands.
        """
        if getattr(args, 'command', None):
            if args.command in self.subcommands:
                self.subcommands[args.command].print_help()
            else:
                raise exc.CommandError("'%s' is not a valid subcommand" %
                                       args.command)
        else:
            self.parser.print_help()

    def get_base_parser(self):
        parser = argparse.ArgumentParser(
            prog='stack',
            description=__doc__.strip(),
            epilog='See "stack help COMMAND" '
                   'for help on a specific command.',
            add_help=False,
            formatter_class=OpenStackHelpFormatter,
        )

        # Global arguments
        parser.add_argument('-h', '--help',
            action='store_true',
            help=argparse.SUPPRESS,
        )

        parser.add_argument('--os-auth-url', metavar='<auth-url>',
            default=env('OS_AUTH_URL'),
            help='Authentication URL (Env: OS_AUTH_URL)')

        parser.add_argument('--os-tenant-name', metavar='<auth-tenant-name>',
            default=env('OS_TENANT_NAME'),
            help='Authentication tenant name (Env: OS_TENANT_NAME)')

        parser.add_argument('--os-tenant-id', metavar='<auth-tenant-id>',
            default=env('OS_TENANT_ID'),
            help='Authentication tenant ID (Env: OS_TENANT_ID)')

        parser.add_argument('--os-username', metavar='<auth-username>',
            default=utils.env('OS_USERNAME'),
            help='Authentication username (Env: OS_USERNAME)')

        parser.add_argument('--os-password', metavar='<auth-password>',
            default=utils.env('OS_PASSWORD'),
            help='Authentication password (Env: OS_PASSWORD)')

        parser.add_argument('--os-region-name', metavar='<auth-region-name>',
            default=env('OS_REGION_NAME'),
            help='Authentication region name (Env: OS_REGION_NAME)')

        parser.add_argument('--debug',
            default=False,
            action='store_true',
            help=argparse.SUPPRESS)

        parser.add_argument('--os-identity-api-version',
            metavar='<identity-api-version>',
            default=env('OS_IDENTITY_API_VERSION', default='2.0'),
            help='Identity API version, default=2.0 (Env: OS_IDENTITY_API_VERSION)')

        parser.add_argument('--os-compute-api-version',
            metavar='<compute-api-version>',
            default=env('OS_COMPUTE_API_VERSION', default='2'),
            help='Compute API version, default=2.0 (Env: OS_COMPUTE_API_VERSION)')

        parser.add_argument('--os-image-api-version',
            metavar='<image-api-version>',
            default=env('OS_IMAGE_API_VERSION', default='1.0'),
            help='Image API version, default=1.0 (Env: OS_IMAGE_API_VERSION)')

        parser.add_argument('--service-token', metavar='<service-token>',
            default=env('SERVICE_TOKEN'),
            help=argparse.SUPPRESS)

        parser.add_argument('--service-endpoint', metavar='<service-endpoint>',
            default=env('SERVICE_ENDPOINT'),
            help=argparse.SUPPRESS)

        parser.add_argument('action', metavar='<action>',
            default='help',
            help=argparse.SUPPRESS)

        parser.add_argument('subject', metavar='<subject>',
            default='', nargs='?',
            help=argparse.SUPPRESS)

        return parser

    def get_subcommand_parser(self, cmd_subject):
        parser = self.get_base_parser()

        self.subcommands = {}
        subparsers = parser.add_subparsers(metavar='<subcommand>')

        if cmd_subject is None or cmd_subject == '':
            # TODO(dtroyer): iterate over all known subjects to produce 
            #                the complete help list
            print "Get all subjects here - exit"
            exit(1)

        (module, version) = self._map_subject(cmd_subject)
        if module is None or cmd_subject is None:
            print "Module %s not found - exit" % cmd_subject
            exit(1)
        if self.debug:
            print "module: %s" % module
        exec("from %s.v%s import %s as cmd" % (module, self.api_version[module], cmd_subject))
        self._find_actions(subparsers, cmd)

        self._find_actions(subparsers, self)

        return parser

    def _map_subject(self, cmd_subject):
        '''Convert from subject to the module that implements it'''
        COMPUTE = ['server']
        IDENTITY = ['key']
        IMAGE = ['image']
        if cmd_subject in COMPUTE:
            version = self.api_version['compute'].replace('.', '_')
            return ('compute', version)
        elif cmd_subject in IDENTITY:
            version = self.api_version['identity'].replace('.', '_')
            return ('identity', version)
        elif cmd_subject in IMAGE:
            version = self.api_version['imade'].replace('.', '_')
            return ('image', version)
        else:
            return None

    def main(self, argv):
        '''
        - get api version
        - get version command set
        - import version-subject module
        - is verb-subject supported?
        '''
        # Parse global args to find version
        parser = self.get_base_parser()
        (options, args) = parser.parse_known_args(argv)

        # stash selected API versions for later
        # TODO(dtroyer): how do extenstions add their version requirements?
        self.api_version = {
            'compute': options.os_compute_api_version,
            'identity': options.os_identity_api_version,
            'image': options.os_image_api_version,
        }

        # Setup debugging
        if getattr(options, 'debug', None):
            self.debug = 1
        else:
            self.debug = 0

        if self.debug:
            print "API: Identity=%s Compute=%s Image=%s" % (self.api_version['identity'], self.api_version['compute'], self.api_version['image'])
            print "Action: %s" % options.action
            print "subject: %s" % getattr(options, 'subject', '')
            print "args: %s" % args

        # Handle top-level --help/-h before attempting to parse
        # a command off the command line
        if getattr(options, 'help', None) or getattr(options, 'action', None) == 'help':
            print "top-level help"
            # Build available subcommands
            self.parser = self.get_subcommand_parser(options.subject)
            self.do_help(options)
            return 0

        # Build selected subcommands
        self.parser = self.get_subcommand_parser(options.subject)

        # Parse args again and call whatever callback was selected
        args.insert(0, '%s-%s' % (options.action, options.subject))
        if self.debug:
            print "args: %s" % args
        args = self.parser.parse_args(args)

        if self.debug:
            print "Testing command parsing"
            print "Auth username: %s" % options.os_username
            #print "Action: %s" % options.action
            #print "Subject: %s" % options.subject
            print "args: %s" % args

class OpenStackHelpFormatter(argparse.HelpFormatter):
    def start_section(self, heading):
        # Title-case the headings
        heading = '%s%s' % (heading[0].upper(), heading[1:])
        super(OpenStackHelpFormatter, self).start_section(heading)


def main():
    try:
        OpenStackShell().main(sys.argv[1:])

    except Exception, e:
        if httplib2.debuglevel == 1:
            raise  # dump stack.
        else:
            print >> sys.stderr, e
        sys.exit(1)

def test_main(argv):
    # The argparse/optparse/cmd2 modules muck about with sys.argv
    # so we save it and restore at the end to let the tests
    # run repeatedly without concatenating the args on each run
    save_argv = sys.argv

    main()

    # Put it back so the next test has a clean copy
    sys.argv = save_argv

if __name__ == "__main__":
    main()
