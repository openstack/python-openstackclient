# Copyright 2023 Red Hat.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import copy
import datetime
import logging

from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils

from openstackclient.i18n import _


LOG = logging.getLogger(__name__)


def _format_image_cache(cached_images):
    """Format image cache to make it more consistent with OSC operations."""

    image_list = []
    for item in cached_images:
        if item == "cached_images":
            for image in cached_images[item]:
                image_obj = copy.deepcopy(image)
                image_obj['state'] = 'cached'
                image_obj['last_accessed'] = (
                    datetime.datetime.utcfromtimestamp(
                        image['last_accessed']
                    ).isoformat()
                )
                image_obj['last_modified'] = (
                    datetime.datetime.utcfromtimestamp(
                        image['last_modified']
                    ).isoformat()
                )
                image_list.append(image_obj)
        elif item == "queued_images":
            for image in cached_images[item]:
                image = {'image_id': image}
                image.update(
                    {
                        'state': 'queued',
                        'last_accessed': 'N/A',
                        'last_modified': 'N/A',
                        'size': 'N/A',
                        'hits': 'N/A',
                    }
                )
                image_list.append(image)
    return image_list


class ListCachedImage(command.Lister):
    _description = _("Get Cache State")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        return parser

    def take_action(self, parsed_args):
        image_client = self.app.client_manager.image

        # List of Cache data received
        data = _format_image_cache(dict(image_client.get_image_cache()))
        columns = [
            'image_id',
            'state',
            'last_accessed',
            'last_modified',
            'size',
            'hits',
        ]
        column_headers = [
            "ID",
            "State",
            "Last Accessed (UTC)",
            "Last Modified (UTC)",
            "Size",
            "Hits",
        ]

        return (
            column_headers,
            (
                utils.get_dict_properties(
                    image,
                    columns,
                )
                for image in data
            ),
        )


class QueueCachedImage(command.Command):
    _description = _("Queue image(s) for caching.")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "images",
            metavar="<image>",
            nargs="+",
            help=_("Image to display (name or ID)"),
        )
        return parser

    def take_action(self, parsed_args):
        image_client = self.app.client_manager.image

        failures = 0
        for image in parsed_args.images:
            try:
                image_obj = image_client.find_image(
                    image,
                    ignore_missing=False,
                )
                image_client.queue_image(image_obj.id)
            except Exception as e:
                failures += 1
                msg = _(
                    "Failed to queue image with name or ID '%(image)s': %(e)s"
                )
                LOG.error(msg, {'image': image, 'e': e})

        if failures > 0:
            total = len(parsed_args.images)
            msg = _("Failed to queue %(failures)s of %(total)s images") % {
                'failures': failures,
                'total': total,
            }
            raise exceptions.CommandError(msg)


class DeleteCachedImage(command.Command):
    _description = _("Delete image(s) from cache")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "images",
            metavar="<image>",
            nargs="+",
            help=_("Image(s) to delete (name or ID)"),
        )
        return parser

    def take_action(self, parsed_args):
        failures = 0
        image_client = self.app.client_manager.image
        for image in parsed_args.images:
            try:
                image_obj = image_client.find_image(
                    image,
                    ignore_missing=False,
                )
                image_client.cache_delete_image(image_obj.id)
            except Exception as e:
                failures += 1
                msg = _(
                    "Failed to delete image with name or ID '%(image)s': %(e)s"
                )
                LOG.error(msg, {'image': image, 'e': e})

        if failures > 0:
            total = len(parsed_args.images)
            msg = _("Failed to delete %(failures)s of %(total)s images.") % {
                'failures': failures,
                'total': total,
            }
            raise exceptions.CommandError(msg)


class ClearCachedImage(command.Command):
    _description = _("Clear all images from cache, queue or both")

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument(
            "--cache",
            action="store_const",
            const="cache",
            default="both",
            dest="target",
            help=_("Clears all the cached images"),
        )
        parser.add_argument(
            "--queue",
            action="store_const",
            const="queue",
            default="both",
            dest="target",
            help=_("Clears all the queued images"),
        )
        return parser

    def take_action(self, parsed_args):
        image_client = self.app.client_manager.image

        target = parsed_args.target
        try:
            image_client.clear_cache(target)
        except Exception:
            msg = _("Failed to clear image cache")
            LOG.error(msg)
            raise exceptions.CommandError(msg)
