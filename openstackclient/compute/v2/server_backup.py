#   Copyright 2012-2013 OpenStack Foundation
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

"""Compute v2 Server action implementations"""

from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils
from oslo_utils import importutils
import six

from openstackclient.i18n import _


class CreateServerBackup(command.ShowOne):
    _description = _("Create a server backup image")

    IMAGE_API_VERSIONS = {
        "1": "openstackclient.image.v1.image",
        "2": "openstackclient.image.v2.image",
    }

    def get_parser(self, prog_name):
        parser = super(CreateServerBackup, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help=_('Server to back up (name or ID)'),
        )
        parser.add_argument(
            '--name',
            metavar='<image-name>',
            help=_('Name of the backup image (default: server name)'),
        )
        parser.add_argument(
            '--type',
            metavar='<backup-type>',
            help=_(
                'Used to populate the backup_type property of the backup '
                'image (default: empty)'
            ),
        )
        parser.add_argument(
            '--rotate',
            metavar='<count>',
            type=int,
            help=_('Number of backups to keep (default: 1)'),
        )
        parser.add_argument(
            '--wait',
            action='store_true',
            help=_('Wait for backup image create to complete'),
        )
        return parser

    def take_action(self, parsed_args):

        def _show_progress(progress):
            if progress:
                self.app.stderr.write('\rProgress: %s' % progress)
                self.app.stderr.flush()

        compute_client = self.app.client_manager.compute

        server = utils.find_resource(
            compute_client.servers,
            parsed_args.server,
        )

        # Set sane defaults as this API wants all mouths to be fed
        if parsed_args.name is None:
            backup_name = server.name
        else:
            backup_name = parsed_args.name
        if parsed_args.type is None:
            backup_type = ""
        else:
            backup_type = parsed_args.type
        if parsed_args.rotate is None:
            backup_rotation = 1
        else:
            backup_rotation = parsed_args.rotate

        compute_client.servers.backup(
            server.id,
            backup_name,
            backup_type,
            backup_rotation,
        )

        image_client = self.app.client_manager.image
        image = utils.find_resource(
            image_client.images,
            backup_name,
        )

        if parsed_args.wait:
            if utils.wait_for_status(
                image_client.images.get,
                image.id,
                callback=_show_progress,
            ):
                self.app.stdout.write('\n')
            else:
                msg = _('Error creating server backup: %s') % parsed_args.name
                raise exceptions.CommandError(msg)

        if self.app.client_manager._api_version['image'] == '1':
            info = {}
            info.update(image._info)
            info['properties'] = utils.format_dict(info.get('properties', {}))
        else:
            # Get the right image module to format the output
            image_module = importutils.import_module(
                self.IMAGE_API_VERSIONS[
                    self.app.client_manager._api_version['image']
                ]
            )
            info = image_module._format_image(image)
        return zip(*sorted(six.iteritems(info)))
