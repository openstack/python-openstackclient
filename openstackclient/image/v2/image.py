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

"""Image V2 Action Implementations"""

import logging
import six

from cliff import command
from cliff import lister
from cliff import show

from glanceclient.common import utils as gc_utils
from openstackclient.common import utils


class DeleteImage(command.Command):
    """Delete an image"""

    log = logging.getLogger(__name__ + ".DeleteImage")

    def get_parser(self, prog_name):
        parser = super(DeleteImage, self).get_parser(prog_name)
        parser.add_argument(
            "image",
            metavar="<image>",
            help="Name or ID of image to delete",
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        image_client = self.app.client_manager.image
        image = utils.find_resource(
            image_client.images,
            parsed_args.image,
        )
        image_client.images.delete(image.id)


class ListImage(lister.Lister):
    """List available images"""

    log = logging.getLogger(__name__ + ".ListImage")

    def get_parser(self, prog_name):
        parser = super(ListImage, self).get_parser(prog_name)
        parser.add_argument(
            "--page-size",
            metavar="<size>",
            help="Number of images to request in each paginated request",
        )
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help='List additional fields in output',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        image_client = self.app.client_manager.image

        kwargs = {}
        if parsed_args.page_size is not None:
            kwargs["page_size"] = parsed_args.page_size

        data = image_client.images.list(**kwargs)
        if parsed_args.long:
            columns = ('ID', 'Name', 'Disk Format', 'Container Format',
                       'Size', 'Status')
        else:
            columns = ("ID", "Name")

        return (columns, (utils.get_item_properties(s, columns) for s in data))


class SaveImage(command.Command):
    """Save an image locally"""

    log = logging.getLogger(__name__ + ".SaveImage")

    def get_parser(self, prog_name):
        parser = super(SaveImage, self).get_parser(prog_name)
        parser.add_argument(
            "--file",
            metavar="<filename>",
            help="Downloaded image save filename [default: stdout]",
        )
        parser.add_argument(
            "image",
            metavar="<image>",
            help="Name or ID of image to save",
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        image_client = self.app.client_manager.image
        image = utils.find_resource(
            image_client.images,
            parsed_args.image,
        )
        data = image_client.images.data(image)

        gc_utils.save_image(data, parsed_args.file)


class ShowImage(show.ShowOne):
    """Show image details"""

    log = logging.getLogger(__name__ + ".ShowImage")

    def get_parser(self, prog_name):
        parser = super(ShowImage, self).get_parser(prog_name)
        parser.add_argument(
            "image",
            metavar="<image>",
            help="Name or ID of image to display",
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        image_client = self.app.client_manager.image
        image = utils.find_resource(
            image_client.images,
            parsed_args.image,
        )

        info = {}
        info.update(image._info)
        return zip(*sorted(six.iteritems(info)))
