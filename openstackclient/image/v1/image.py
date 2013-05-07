#   Copyright 2013 OpenStack, LLC.
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
import sys

if os.name == "nt":
    import msvcrt
else:
    msvcrt = None

from cliff import show


class CreateImage(show.ShowOne):
    """Create image command"""

    api = "image"
    log = logging.getLogger(__name__ + ".CreateImage")

    def get_parser(self, prog_name):
        parser = super(CreateImage, self).get_parser(prog_name)
        parser.add_argument(
            "name",
            metavar="<name>",
            help="Name of image.")
        parser.add_argument(
            "--disk_format",
            default="raw",
            metavar="<disk_format>",
            help="Disk format of image.")
        parser.add_argument(
            "--id",
            metavar="<id>",
            help="ID of image to reserve.")
        parser.add_argument(
            "--store",
            metavar="<store>",
            help="Store to upload image to.")
        parser.add_argument(
            "--container-format",
            default="bare",
            metavar="<container_format>",
            help="Container format of image.")
        parser.add_argument(
            "--owner",
            metavar="<tenant_id>",
            help="Owner of the image.")
        parser.add_argument(
            "--size",
            metavar="<size>",
            help="Size of image in bytes. Only used with --location and"
                 " --copy-from.")
        parser.add_argument(
            "--min-disk",
            metavar="<disk_gb>",
            help="Minimum size of disk needed to boot image in gigabytes.")
        parser.add_argument(
            "--min-ram",
            metavar="<disk_ram>",
            help="Minimum amount of ram needed to boot image in megabytes.")
        parser.add_argument(
            "--location",
            metavar="<image_url>",
            help="URL where the data for this image already resides.")
        parser.add_argument(
            "--file",
            metavar="<file>",
            help="Local file that contains disk image.")
        parser.add_argument(
            "--checksum",
            metavar="<checksum>",
            help="Hash of image data used for verification.")
        parser.add_argument(
            "--copy-from",
            metavar="<image_url>",
            help="Similar to --location, but this indicates that the image"
                 " should immediately be copied from the data store.")
        parser.add_argument(
            "--property",
            metavar="<key=value>",
            default=[],
            action="append",
            help="Arbitrary property to associate with image.")
        protected_group = parser.add_mutually_exclusive_group()
        protected_group.add_argument(
            "--protected",
            dest="protected",
            action="store_true",
            help="Prevent image from being deleted (default: False).")
        protected_group.add_argument(
            "--unprotected",
            dest="protected",
            action="store_false",
            default=False,
            help="Allow images to be deleted (default: True).")
        public_group = parser.add_mutually_exclusive_group()
        public_group.add_argument(
            "--public",
            dest="is_public",
            action="store_true",
            default=True,
            help="Image is accessible to the public (default).")
        public_group.add_argument(
            "--private",
            dest="is_public",
            action="store_false",
            help="Image is inaccessible to the public.")
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

        args["properties"] = {}
        for _property in args.pop("property"):
            key, value = _property.split("=", 1)
            args["properties"][key] = value

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
        data = image_client.images.create(**args)._info.copy()

        return zip(*sorted(data.iteritems()))
