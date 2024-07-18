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

import collections
import logging
import os

from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
from openstack import utils as sdk_utils
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.common import pagination
from openstackclient.i18n import _
from openstackclient.identity import common as identity_common


LOG = logging.getLogger(__name__)
Keypair = collections.namedtuple('Keypair', 'private_key public_key')


def _generate_keypair():
    """Generate a Ed25519 keypair in OpenSSH format.

    :returns: A `Keypair` named tuple with the generated private and public
    keys.
    """
    key = ed25519.Ed25519PrivateKey.generate()
    private_key = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.OpenSSH,
        serialization.NoEncryption(),
    ).decode()
    public_key = (
        key.public_key()
        .public_bytes(
            serialization.Encoding.OpenSSH, serialization.PublicFormat.OpenSSH
        )
        .decode()
    )

    return Keypair(private_key, public_key)


def _get_keypair_columns(item, hide_pub_key=False, hide_priv_key=False):
    # To maintain backwards compatibility we need to rename sdk props to
    # whatever OSC was using before
    hidden_columns = ['links', 'location']
    if hide_pub_key:
        hidden_columns.append('public_key')
    if hide_priv_key:
        hidden_columns.append('private_key')
    return utils.get_osc_show_columns_for_sdk_resource(
        item, {}, hidden_columns
    )


class CreateKeypair(command.ShowOne):
    _description = _("Create new public or private key for server ssh access")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'name', metavar='<name>', help=_("New public or private key name")
        )
        key_group = parser.add_mutually_exclusive_group()
        key_group.add_argument(
            '--public-key',
            metavar='<file>',
            help=_(
                "Filename for public key to add. "
                "If not used, generates a private key in ssh-ed25519 format. "
                "To generate keys in other formats, including the legacy "
                "ssh-rsa format, you must use an external tool such as "
                "ssh-keygen and specify this argument."
            ),
        )
        key_group.add_argument(
            '--private-key',
            metavar='<file>',
            help=_(
                "Filename for private key to save. "
                "If not used, print private key in console."
            ),
        )
        parser.add_argument(
            '--type',
            metavar='<type>',
            choices=['ssh', 'x509'],
            help=_(
                'Keypair type '
                '(supported by --os-compute-api-version 2.2 or above)'
            ),
        )
        parser.add_argument(
            '--user',
            metavar='<user>',
            help=_(
                'The owner of the keypair (admin only) (name or ID) '
                '(supported by --os-compute-api-version 2.10 or above)'
            ),
        )
        identity_common.add_user_domain_option_to_parser(parser)
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        identity_client = self.app.client_manager.identity

        kwargs = {'name': parsed_args.name}

        if parsed_args.public_key:
            try:
                with open(os.path.expanduser(parsed_args.public_key)) as p:
                    public_key = p.read()
            except OSError as e:
                msg = _("Key file %(public_key)s not found: %(exception)s")
                raise exceptions.CommandError(
                    msg
                    % {
                        "public_key": parsed_args.public_key,
                        "exception": e,
                    }
                )

            kwargs['public_key'] = public_key
        else:
            generated_keypair = _generate_keypair()
            kwargs['public_key'] = generated_keypair.public_key

            # If user have us a file, save private key into specified file
            if parsed_args.private_key:
                try:
                    with open(
                        os.path.expanduser(parsed_args.private_key), 'w+'
                    ) as p:
                        p.write(generated_keypair.private_key)
                except OSError as e:
                    msg = _(
                        "Key file %(private_key)s can not be saved: "
                        "%(exception)s"
                    )
                    raise exceptions.CommandError(
                        msg
                        % {
                            "private_key": parsed_args.private_key,
                            "exception": e,
                        }
                    )

        if parsed_args.type:
            if not sdk_utils.supports_microversion(compute_client, '2.2'):
                msg = _(
                    '--os-compute-api-version 2.2 or greater is required to '
                    'support the --type option'
                )
                raise exceptions.CommandError(msg)

            kwargs['key_type'] = parsed_args.type

        if parsed_args.user:
            if not sdk_utils.supports_microversion(compute_client, '2.10'):
                msg = _(
                    '--os-compute-api-version 2.10 or greater is required to '
                    'support the --user option'
                )
                raise exceptions.CommandError(msg)

            kwargs['user_id'] = identity_common.find_user(
                identity_client,
                parsed_args.user,
                parsed_args.user_domain,
            ).id

        keypair = compute_client.create_keypair(**kwargs)

        # NOTE(dtroyer): how do we want to handle the display of the private
        #                key when it needs to be communicated back to the user
        #                For now, duplicate nova keypair-add command output
        if parsed_args.public_key or parsed_args.private_key:
            display_columns, columns = _get_keypair_columns(
                keypair, hide_pub_key=True, hide_priv_key=True
            )
            data = utils.get_item_properties(keypair, columns)

            return (display_columns, data)
        else:
            self.app.stdout.write(generated_keypair.private_key)
            return ({}, {})


class DeleteKeypair(command.Command):
    _description = _("Delete public or private key(s)")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<key>',
            nargs='+',
            help=_("Name of key(s) to delete (name only)"),
        )
        parser.add_argument(
            '--user',
            metavar='<user>',
            help=_(
                'The owner of the keypair. (admin only) (name or ID). '
                'Requires ``--os-compute-api-version`` 2.10 or greater.'
            ),
        )
        identity_common.add_user_domain_option_to_parser(parser)
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        identity_client = self.app.client_manager.identity

        kwargs = {}
        result = 0

        if parsed_args.user:
            if not sdk_utils.supports_microversion(compute_client, '2.10'):
                msg = _(
                    '--os-compute-api-version 2.10 or greater is required to '
                    'support the --user option'
                )
                raise exceptions.CommandError(msg)

            kwargs['user_id'] = identity_common.find_user(
                identity_client,
                parsed_args.user,
                parsed_args.user_domain,
            ).id

        for n in parsed_args.name:
            try:
                compute_client.delete_keypair(
                    n, **kwargs, ignore_missing=False
                )
            except Exception as e:
                result += 1
                LOG.error(
                    _("Failed to delete key with name '%(name)s': %(e)s"),
                    {'name': n, 'e': e},
                )

        if result > 0:
            total = len(parsed_args.name)
            msg = _("%(result)s of %(total)s keys failed to delete.") % {
                'result': result,
                'total': total,
            }
            raise exceptions.CommandError(msg)


class ListKeypair(command.Lister):
    _description = _("List key fingerprints")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        user_group = parser.add_mutually_exclusive_group()
        user_group.add_argument(
            '--user',
            metavar='<user>',
            help=_(
                'Show keypairs for another user (admin only) (name or ID). '
                'Requires ``--os-compute-api-version`` 2.10 or greater.'
            ),
        )
        identity_common.add_user_domain_option_to_parser(parser)
        user_group.add_argument(
            '--project',
            metavar='<project>',
            help=_(
                'Show keypairs for all users associated with project '
                '(admin only) (name or ID). '
                'Requires ``--os-compute-api-version`` 2.10 or greater.'
            ),
        )
        identity_common.add_project_domain_option_to_parser(parser)
        pagination.add_marker_pagination_option_to_parser(parser)
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        identity_client = self.app.client_manager.identity

        kwargs = {}

        if parsed_args.marker:
            if not sdk_utils.supports_microversion(compute_client, '2.35'):
                msg = _(
                    '--os-compute-api-version 2.35 or greater is required '
                    'to support the --marker option'
                )
                raise exceptions.CommandError(msg)

            kwargs['marker'] = parsed_args.marker

        if parsed_args.limit:
            if not sdk_utils.supports_microversion(compute_client, '2.35'):
                msg = _(
                    '--os-compute-api-version 2.35 or greater is required '
                    'to support the --limit option'
                )
                raise exceptions.CommandError(msg)

            kwargs['limit'] = parsed_args.limit

        if parsed_args.project:
            if not sdk_utils.supports_microversion(compute_client, '2.10'):
                msg = _(
                    '--os-compute-api-version 2.10 or greater is required to '
                    'support the --project option'
                )
                raise exceptions.CommandError(msg)

            if parsed_args.marker:
                # NOTE(stephenfin): Because we're doing this client-side, we
                # can't really rely on the marker, because we don't know what
                # user the marker is associated with
                msg = _('--project is not compatible with --marker')

            # NOTE(stephenfin): This is done client side because nova doesn't
            # currently support doing so server-side. If this is slow, we can
            # think about spinning up a threadpool or similar.
            project = identity_common.find_project(
                identity_client,
                parsed_args.project,
                parsed_args.project_domain,
            ).id
            users = identity_client.users.list(tenant_id=project)

            data = []
            for user in users:
                kwargs['user_id'] = user.id
                data.extend(compute_client.keypairs(**kwargs))
        elif parsed_args.user:
            if not sdk_utils.supports_microversion(compute_client, '2.10'):
                msg = _(
                    '--os-compute-api-version 2.10 or greater is required to '
                    'support the --user option'
                )
                raise exceptions.CommandError(msg)

            user = identity_common.find_user(
                identity_client,
                parsed_args.user,
                parsed_args.user_domain,
            )
            kwargs['user_id'] = user.id

            data = compute_client.keypairs(**kwargs)
        else:
            data = compute_client.keypairs(**kwargs)

        columns: tuple[str, ...] = ("Name", "Fingerprint")

        if sdk_utils.supports_microversion(compute_client, '2.2'):
            columns += ("Type",)

        return (
            columns,
            (utils.get_item_properties(s, columns) for s in data),
        )


class ShowKeypair(command.ShowOne):
    _description = _("Display key details")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<key>',
            help=_("Public or private key to display (name only)"),
        )
        parser.add_argument(
            '--public-key',
            action='store_true',
            default=False,
            help=_("Show only bare public key paired with the generated key"),
        )
        parser.add_argument(
            '--user',
            metavar='<user>',
            help=_(
                'The owner of the keypair. (admin only) (name or ID). '
                'Requires ``--os-compute-api-version`` 2.10 or greater.'
            ),
        )
        identity_common.add_user_domain_option_to_parser(parser)
        return parser

    def take_action(self, parsed_args):
        compute_client = self.app.client_manager.compute
        identity_client = self.app.client_manager.identity

        kwargs = {}

        if parsed_args.user:
            if not sdk_utils.supports_microversion(compute_client, '2.10'):
                msg = _(
                    '--os-compute-api-version 2.10 or greater is required to '
                    'support the --user option'
                )
                raise exceptions.CommandError(msg)

            kwargs['user_id'] = identity_common.find_user(
                identity_client,
                parsed_args.user,
                parsed_args.user_domain,
            ).id

        keypair = compute_client.find_keypair(
            parsed_args.name, **kwargs, ignore_missing=False
        )

        if not parsed_args.public_key:
            display_columns, columns = _get_keypair_columns(
                keypair, hide_pub_key=True
            )
            data = utils.get_item_properties(keypair, columns)
            return (display_columns, data)
        else:
            self.app.stdout.write(keypair.public_key)
            return ({}, {})
