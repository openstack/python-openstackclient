#   Copyright 2012-2013 OpenStack, LLC.
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

"""Image Action Implementations"""

import logging

from cliff import command
from cliff import lister
from cliff import show

from glanceclient.common import utils as gc_utils
from openstackclient.common import utils


class ListImage(lister.Lister):
    """List image command"""

    api = "image"
    log = logging.getLogger(__name__ + ".ListImage")

    def get_parser(self, prog_name):
        parser = super(ListImage, self).get_parser(prog_name)
        parser.add_argument(
            "--page-size",
            metavar="<size>",
            help="Number of images to request in each paginated request.")
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)" % parsed_args)

        image_client = self.app.client_manager.image

        kwargs = {}
        if parsed_args.page_size is not None:
            kwargs["page_size"] = parsed_args.page_size

        data = image_client.images.list(**kwargs)
        columns = ["ID", "Name"]

        return (columns, (utils.get_item_properties(s, columns) for s in data))


class SaveImage(command.Command):
    """Save image command"""

    api = "image"
    log = logging.getLogger(__name__ + ".SaveImage")

    def get_parser(self, prog_name):
        parser = super(SaveImage, self).get_parser(prog_name)
        parser.add_argument(
            "--file",
            metavar="<file>",
            help="Local file to save downloaded image data "
                 "to. If this is not specified the image "
                 "data will be written to stdout.")
        parser.add_argument(
            "id",
            metavar="<image_id>",
            help="ID of image to describe.")
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)" % parsed_args)

        image_client = self.app.client_manager.image
        data = image_client.images.data(parsed_args.id)

        gc_utils.save_image(data, parsed_args.file)


class ShowImage(show.ShowOne):
    """Show image command"""

    api = "image"
    log = logging.getLogger(__name__ + ".ShowImage")

    def get_parser(self, prog_name):
        parser = super(ShowImage, self).get_parser(prog_name)
        parser.add_argument(
            "id",
            metavar="<image_id>",
            help="ID of image to describe.")
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)" % parsed_args)

        image_client = self.app.client_manager.image
        data = image_client.images.get(parsed_args.id)

        return zip(*sorted(data.iteritems()))
