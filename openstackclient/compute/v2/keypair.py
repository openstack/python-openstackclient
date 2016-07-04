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

import io
import logging
import os
import sys

from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils
import six

from openstackclient.i18n import _


LOG = logging.getLogger(__name__)


class CreateKeypair(command.ShowOne):
    """Create new public key"""

    def get_parser(self, prog_name):
        parser = super(CreateKeypair, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<name>',
            help=_("New public key name")
        )
        parser.add_argument(
            '--public-key',
            metavar='<file>',
            help=_("Filename for public key to add")
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute

        public_key = parsed_args.public_key
        if public_key:
            try:
                with io.open(os.path.expanduser(parsed_args.public_key)) as p:
                    public_key = p.read()
            except IOError as e:
                msg = _("Key file %(public_key)s not found: %(exception)s")
                raise exceptions.CommandError(
                    msg % {"public_key": parsed_args.public_key,
                           "exception": e}
                )

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
    """Delete public key(s)"""

    def get_parser(self, prog_name):
        parser = super(DeleteKeypair, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<key>',
            nargs='+',
            help=_("Public key(s) to delete (name only)")
        )
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        result = 0
        for n in parsed_args.name:
            try:
                data = utils.find_resource(
                    compute_client.keypairs, n)
                compute_client.keypairs.delete(data.name)
            except Exception as e:
                result += 1
                LOG.error(_("Failed to delete public key with name "
                          "'%(name)s': %(e)s")
                          % {'name': n, 'e': e})

        if result > 0:
            total = len(parsed_args.name)
            msg = (_("%(result)s of %(total)s public keys failed "
                   "to delete.") % {'result': result, 'total': total})
            raise exceptions.CommandError(msg)


class ListKeypair(command.Lister):
    """List public key fingerprints"""

    def take_action(self, parsed_args):
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


class ShowKeypair(command.ShowOne):
    """Display public key details"""

    def get_parser(self, prog_name):
        parser = super(ShowKeypair, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<key>',
            help=_("Public key to display (name only)")
        )
        parser.add_argument(
            '--public-key',
            action='store_true',
            default=False,
            help=_("Show only bare public key (name only)")
        )
        return parser

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
