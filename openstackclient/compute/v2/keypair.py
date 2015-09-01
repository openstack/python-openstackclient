#   Copyright 2013 OpenStack Foundation
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

"""Keypair action implementations"""

import logging
import os
import six
import sys

from cliff import command
from cliff import lister
from cliff import show

from openstackclient.common import exceptions
from openstackclient.common import utils


class CreateKeypair(show.ShowOne):
    """Create new public key"""

    log = logging.getLogger(__name__ + '.CreateKeypair')

    def get_parser(self, prog_name):
        parser = super(CreateKeypair, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<name>',
            help='New public key name',
        )
        parser.add_argument(
            '--public-key',
            metavar='<file>',
            help='Filename for public key to add',
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute

        public_key = parsed_args.public_key
        if public_key:
            try:
                with open(os.path.expanduser(parsed_args.public_key)) as p:
                    public_key = p.read()
            except IOError as e:
                msg = "Key file %s not found: %s"
                raise exceptions.CommandError(msg
                                              % (parsed_args.public_key, e))

        keypair = compute_client.keypairs.create(
            parsed_args.name,
            public_key=public_key,
        )

        # NOTE(dtroyer): how do we want to handle the display of the private
        #                key when it needs to be communicated back to the user
        #                For now, duplicate nova keypair-add command output
        info = {}
        if public_key:
            info.update(keypair._info)
            del info['public_key']
            return zip(*sorted(six.iteritems(info)))
        else:
            sys.stdout.write(keypair.private_key)
            return ({}, {})


class DeleteKeypair(command.Command):
    """Delete public key"""

    log = logging.getLogger(__name__ + '.DeleteKeypair')

    def get_parser(self, prog_name):
        parser = super(DeleteKeypair, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<key>',
            help='Public key to delete',
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        compute_client.keypairs.delete(parsed_args.name)
        return


class ListKeypair(lister.Lister):
    """List public key fingerprints"""

    log = logging.getLogger(__name__ + ".ListKeypair")

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        compute_client = self.app.client_manager.compute
        columns = (
            "Name",
            "Fingerprint"
        )
        data = compute_client.keypairs.list()

        return (columns,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class ShowKeypair(show.ShowOne):
    """Display public key details"""

    log = logging.getLogger(__name__ + '.ShowKeypair')

    def get_parser(self, prog_name):
        parser = super(ShowKeypair, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<key>',
            help='Public key to display',
        )
        parser.add_argument(
            '--public-key',
            action='store_true',
            default=False,
            help='Show only bare public key',
        )
        return parser

    @utils.log_method(log)
    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        keypair = utils.find_resource(compute_client.keypairs,
                                      parsed_args.name)

        info = {}
        info.update(keypair._info)
        if not parsed_args.public_key:
            del info['public_key']
            return zip(*sorted(six.iteritems(info)))
        else:
            # NOTE(dtroyer): a way to get the public key in a similar form
            #                as the private key in the create command
            sys.stdout.write(keypair.public_key)
            return ({}, {})
