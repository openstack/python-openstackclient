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

"""Image V1 Action Implementations"""

import logging
import os
import six
import sys

if os.name == "nt":
    import msvcrt
else:
    msvcrt = None

from cliff import command
from cliff import lister
from cliff import show

from glanceclient.common import utils as gc_utils
from openstackclient.common import exceptions
from openstackclient.common import parseractions
from openstackclient.common import utils


class CreateImage(show.ShowOne):
    """Create/upload an image"""

    log = logging.getLogger(__name__ + ".CreateImage")

    def get_parser(self, prog_name):
        parser = super(CreateImage, self).get_parser(prog_name)
        parser.add_argument(
            "name",
            metavar="<name>",
            help="Name of image",
        )
        parser.add_argument(
            "--disk-format",
            default="raw",
            metavar="<disk-format>",
            help="Disk format of image",
        )
        parser.add_argument(
            "--id",
            metavar="<id>",
            help="ID of image to reserve",
        )
        parser.add_argument(
            "--store",
            metavar="<store>",
            help="Store to upload image to",
        )
        parser.add_argument(
            "--container-format",
            default="bare",
            metavar="<container-format>",
            help="Container format of image",
        )
        parser.add_argument(
            "--owner",
            metavar="<project>",
            help="Image owner (project name or ID)",
        )
        parser.add_argument(
            "--size",
            metavar="<size>",
            help="Size of image in bytes. Only used with --location and"
                 " --copy-from",
        )
        parser.add_argument(
            "--min-disk",
            metavar="<disk-gb>",
            help="Minimum size of disk needed to boot image in gigabytes",
        )
        parser.add_argument(
            "--min-ram",
            metavar="<disk-ram>",
            help="Minimum amount of ram needed to boot image in megabytes",
        )
        parser.add_argument(
            "--location",
            metavar="<image-url>",
            help="URL where the data for this image already resides",
        )
        parser.add_argument(
            "--file",
            metavar="<file>",
            help="Local file that contains disk image",
        )
        parser.add_argument(
            "--checksum",
            metavar="<checksum>",
            help="Hash of image data used for verification",
        )
        parser.add_argument(
            "--copy-from",
            metavar="<image-url>",
            help="Similar to --location, but this indicates that the image"
                 " should immediately be copied from the data store",
        )
        parser.add_argument(
            "--property",
            dest="properties",
            metavar="<key=value>",
            action=parseractions.KeyValueAction,
            help="Set property on this image "
                 '(repeat option to set multiple properties)',
        )
        protected_group = parser.add_mutually_exclusive_group()
        protected_group.add_argument(
            "--protected",
            dest="protected",
            action="store_true",
            help="Prevent image from being deleted (default: False)",
        )
        protected_group.add_argument(
            "--unprotected",
            dest="protected",
            action="store_false",
            default=False,
            help="Allow images to be deleted (default: True)",
        )
        public_group = parser.add_mutually_exclusive_group()
        public_group.add_argument(
            "--public",
            dest="is_public",
            action="store_true",
            default=True,
            help="Image is accessible to the public (default)",
        )
        public_group.add_argument(
            "--private",
            dest="is_public",
            action="store_false",
            help="Image is inaccessible to the public",
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)" % parsed_args)

        # NOTE(jk0): Since create() takes kwargs, it's easiest to just make a
        # copy of parsed_args and remove what we don't need.
        args = vars(parsed_args)
        args = dict(filter(lambda x: x[1] is not None, args.items()))
        args.pop("columns")
        args.pop("formatter")
        args.pop("prefix")
        args.pop("variables")

        if "location" not in args and "copy_from" not in args:
            if "file" in args:
                args["data"] = open(args.pop("file"), "rb")
            else:
                args["data"] = None
                if sys.stdin.isatty() is not True:
                    if msvcrt:
                        msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
                    args["data"] = sys.stdin

        image_client = self.app.client_manager.image
        try:
            image = utils.find_resource(
                image_client.images,
                parsed_args.name,
            )
        except exceptions.CommandError:
            # This is normal for a create or reserve (create w/o an image)
            image = image_client.images.create(**args)
        else:
            # It must be an update
            # If an image is specified via --file, --location or --copy-from
            # let the API handle it
            image = image_client.images.update(image, **args)

        info = {}
        info.update(image._info)
        return zip(*sorted(six.iteritems(info)))


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
        self.log.debug("take_action(%s)" % parsed_args)

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
            help="Name or ID of image to delete",
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)" % parsed_args)

        image_client = self.app.client_manager.image
        image = utils.find_resource(
            image_client.images,
            parsed_args.image,
        )
        data = image_client.images.data(image)

        gc_utils.save_image(data, parsed_args.file)


class SetImage(show.ShowOne):
    """Change image properties"""

    log = logging.getLogger(__name__ + ".SetImage")

    def get_parser(self, prog_name):
        parser = super(SetImage, self).get_parser(prog_name)
        parser.add_argument(
            "image",
            metavar="<image>",
            help="Name or ID of image to change",
        )
        parser.add_argument(
            "--name",
            metavar="<name>",
            help="Name of image",
        )
        parser.add_argument(
            "--owner",
            metavar="<project>",
            help="Image owner (project name or ID)",
        )
        parser.add_argument(
            "--min-disk",
            metavar="<disk-gb>",
            help="Minimum size of disk needed to boot image in gigabytes",
        )
        parser.add_argument(
            "--min-ram",
            metavar="<disk-ram>",
            help="Minimum amount of ram needed to boot image in megabytes",
        )
        parser.add_argument(
            "--property",
            dest="properties",
            metavar="<key=value>",
            default={},
            action=parseractions.KeyValueAction,
            help="Set property on this image "
                 '(repeat option to set multiple properties)',
        )
        protected_group = parser.add_mutually_exclusive_group()
        protected_group.add_argument(
            "--protected",
            dest="protected",
            action="store_true",
            help="Prevent image from being deleted (default: False)",
        )
        protected_group.add_argument(
            "--unprotected",
            dest="protected",
            action="store_false",
            default=False,
            help="Allow images to be deleted (default: True)",
        )
        public_group = parser.add_mutually_exclusive_group()
        public_group.add_argument(
            "--public",
            dest="is_public",
            action="store_true",
            default=True,
            help="Image is accessible to the public (default)",
        )
        public_group.add_argument(
            "--private",
            dest="is_public",
            action="store_false",
            help="Image is inaccessible to the public",
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)" % parsed_args)

        # NOTE(jk0): Since create() takes kwargs, it's easiest to just make a
        # copy of parsed_args and remove what we don't need.
        args = vars(parsed_args)
        args = dict(filter(lambda x: x[1] is not None, args.items()))
        args.pop("columns")
        args.pop("formatter")
        args.pop("prefix")
        args.pop("variables")
        image_arg = args.pop("image")

        image_client = self.app.client_manager.image
        image = utils.find_resource(
            image_client.images,
            image_arg,
        )
        # Merge properties
        args["properties"].update(image.properties)
        image = image_client.images.update(image, **args)

        info = {}
        info.update(image._info)
        return zip(*sorted(six.iteritems(info)))


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
        self.log.debug("take_action(%s)" % parsed_args)

        image_client = self.app.client_manager.image
        image = utils.find_resource(
            image_client.images,
            parsed_args.image,
        )

        info = {}
        info.update(image._info)
        return zip(*sorted(six.iteritems(info)))
