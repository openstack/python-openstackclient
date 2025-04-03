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

import importlib
import logging

from osc_lib.cli import parseractions
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _


LOG = logging.getLogger(__name__)


class CreateServerImage(command.ShowOne):
    _description = _("Create a new server disk image from an existing server")

    IMAGE_API_VERSIONS = {
        "1": "openstackclient.image.v1.image",
        "2": "openstackclient.image.v2.image",
    }

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help=_('Server to create image (name or ID)'),
        )
        parser.add_argument(
            '--name',
            metavar='<image-name>',
            help=_('Name of new disk image (default: server name)'),
        )
        parser.add_argument(
            '--property',
            metavar='<key=value>',
            dest='properties',
            action=parseractions.KeyValueAction,
            help=_(
                'Set a new property to meta_data.json on the metadata server '
                '(repeat option to set multiple values)'
            ),
        )
        parser.add_argument(
            '--wait',
            action='store_true',
            help=_('Wait for operation to complete'),
        )
        return parser

    def take_action(self, parsed_args):
        def _show_progress(progress):
            if progress:
                self.app.stdout.write(f'\rProgress: {progress}')
                self.app.stdout.flush()

        compute_client = self.app.client_manager.compute
        image_client = self.app.client_manager.image

        server = compute_client.find_server(
            parsed_args.server,
            ignore_missing=False,
        )

        if parsed_args.name:
            image_name = parsed_args.name
        else:
            image_name = server.name

        image_id = compute_client.create_server_image(
            server.id,
            image_name,
            parsed_args.properties,
        ).id

        if parsed_args.wait:
            if utils.wait_for_status(
                image_client.get_image,
                image_id,
                callback=_show_progress,
            ):
                self.app.stdout.write('\n')
            else:
                LOG.error(
                    _('Error creating server image: %s'), parsed_args.server
                )
                raise exceptions.CommandError

        image = image_client.find_image(image_id, ignore_missing=False)

        if self.app.client_manager._api_version['image'] == '1':
            info = {}
            info.update(image._info)
            info['properties'] = utils.format_dict(info.get('properties', {}))
        else:
            # Get the right image module to format the output
            image_module = importlib.import_module(
                self.IMAGE_API_VERSIONS[
                    self.app.client_manager._api_version['image']
                ]
            )
            info = image_module._format_image(image)

        return zip(*sorted(info.items()))
