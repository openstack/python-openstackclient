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


DEFAULT_CONTAINER_FORMAT = 'bare'
DEFAULT_DISK_FORMAT = 'raw'


class CreateImage(show.ShowOne):
    """Create/upload an image"""

    log = logging.getLogger(__name__ + ".CreateImage")

    def get_parser(self, prog_name):
        parser = super(CreateImage, self).get_parser(prog_name)
        parser.add_argument(
            "name",
            metavar="<name>",
            help="New image name",
        )
        parser.add_argument(
            "--id",
            metavar="<id>",
            help="Image ID to reserve",
        )
        parser.add_argument(
            "--store",
            metavar="<store>",
            help="Upload image to this store",
        )
        parser.add_argument(
            "--container-format",
            default=DEFAULT_CONTAINER_FORMAT,
            metavar="<container-format>",
            help="Image container format "
                 "(default: %s)" % DEFAULT_CONTAINER_FORMAT,
        )
        parser.add_argument(
            "--disk-format",
            default=DEFAULT_DISK_FORMAT,
            metavar="<disk-format>",
            help="Image disk format "
                 "(default: %s)" % DEFAULT_DISK_FORMAT,
        )
        parser.add_argument(
            "--owner",
            metavar="<project>",
            help="Image owner project name or ID",
        )
        parser.add_argument(
            "--size",
            metavar="<size>",
            help="Image size, in bytes (only used with --location and"
                 " --copy-from)",
        )
        parser.add_argument(
            "--min-disk",
            metavar="<disk-gb>",
            type=int,
            help="Minimum disk size needed to boot image, in gigabytes",
        )
        parser.add_argument(
            "--min-ram",
            metavar="<ram-mb>",
            type=int,
            help="Minimum RAM size needed to boot image, in megabytes",
        )
        parser.add_argument(
            "--location",
            metavar="<image-url>",
            help="Download image from an existing URL",
        )
        parser.add_argument(
            "--copy-from",
            metavar="<image-url>",
            help="Copy image from the data store (similar to --location)",
        )
        parser.add_argument(
            "--file",
            metavar="<file>",
            help="Upload image from local file",
        )
        parser.add_argument(
            "--volume",
            metavar="<volume>",
            help="Create image from a volume",
        )
        parser.add_argument(
            "--force",
            dest='force',
            action='store_true',
            default=False,
            help="Force image creation if volume is in use "
                 "(only meaningful with --volume)",
        )
        parser.add_argument(
            "--checksum",
            metavar="<checksum>",
            help="Image hash used for verification",
        )
        protected_group = parser.add_mutually_exclusive_group()
        protected_group.add_argument(
            "--protected",
            action="store_true",
            help="Prevent image from being deleted",
        )
        protected_group.add_argument(
            "--unprotected",
            action="store_true",
            help="Allow image to be deleted (default)",
        )
        public_group = parser.add_mutually_exclusive_group()
        public_group.add_argument(
            "--public",
            action="store_true",
            help="Image is accessible to the public",
        )
        public_group.add_argument(
            "--private",
            action="store_true",
            help="Image is inaccessible to the public (default)",
        )
        parser.add_argument(
            "--property",
            dest="properties",
            metavar="<key=value>",
            action=parseractions.KeyValueAction,
            help="Set an image property "
                 "(repeat option to set multiple properties)",
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        image_client = self.app.client_manager.image

        # Build an attribute dict from the parsed args, only include
        # attributes that were actually set on the command line
        kwargs = {}
        copy_attrs = ('name', 'id', 'store', 'container_format',
                      'disk_format', 'owner', 'size', 'min_disk', 'min_ram',
                      'localtion', 'copy_from', 'volume', 'force',
                      'checksum', 'properties')
        for attr in copy_attrs:
            if attr in parsed_args:
                val = getattr(parsed_args, attr, None)
                if val:
                    # Only include a value in kwargs for attributes that are
                    # actually present on the command line
                    kwargs[attr] = val
        # Handle exclusive booleans with care
        # Avoid including attributes in kwargs if an option is not
        # present on the command line.  These exclusive booleans are not
        # a single value for the pair of options because the default must be
        # to do nothing when no options are present as opposed to always
        # setting a default.
        if parsed_args.protected:
            kwargs['protected'] = True
        if parsed_args.unprotected:
            kwargs['protected'] = False
        if parsed_args.public:
            kwargs['is_public'] = True
        if parsed_args.private:
            kwargs['is_public'] = False

        if not parsed_args.location and not parsed_args.copy_from:
            if parsed_args.volume:
                volume_client = self.app.client_manager.volume
                source_volume = utils.find_resource(
                    volume_client.volumes,
                    parsed_args.volume,
                )
                response, body = volume_client.volumes.upload_to_image(
                    source_volume.id,
                    parsed_args.force,
                    parsed_args.name,
                    parsed_args.container_format,
                    parsed_args.disk_format,
                )
                info = body['os-volume_upload_image']
            elif parsed_args.file:
                # Send an open file handle to glanceclient so it will
                # do a chunked transfer
                kwargs["data"] = open(parsed_args.file, "rb")
            else:
                # Read file from stdin
                kwargs["data"] = None
                if sys.stdin.isatty() is not True:
                    if msvcrt:
                        msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
                    # Send an open file handle to glanceclient so it will
                    # do a chunked transfer
                    kwargs["data"] = sys.stdin

        try:
            image = utils.find_resource(
                image_client.images,
                parsed_args.name,
            )

            # Preserve previous properties if any are being set now
            if image.properties:
                if parsed_args.properties:
                    image.properties.update(kwargs['properties'])
                kwargs['properties'] = image.properties

        except exceptions.CommandError:
            if not parsed_args.volume:
                # This is normal for a create or reserve (create w/o an image)
                # But skip for create from volume
                image = image_client.images.create(**kwargs)
        else:
            # Update an existing reservation

            # If an image is specified via --file, --location or
            # --copy-from let the API handle it
            image = image_client.images.update(image.id, **kwargs)

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
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

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
        self.log.debug("take_action(%s)", parsed_args)

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
            help="Image name or ID to change",
        )
        parser.add_argument(
            "--name",
            metavar="<name>",
            help="New image name",
        )
        parser.add_argument(
            "--owner",
            metavar="<project>",
            help="New image owner project name or ID",
        )
        parser.add_argument(
            "--min-disk",
            metavar="<disk-gb>",
            type=int,
            help="Minimum disk size needed to boot image, in gigabytes",
        )
        parser.add_argument(
            "--min-ram",
            metavar="<disk-ram>",
            type=int,
            help="Minimum RAM size needed to boot image, in megabytes",
        )
        protected_group = parser.add_mutually_exclusive_group()
        protected_group.add_argument(
            "--protected",
            action="store_true",
            help="Prevent image from being deleted",
        )
        protected_group.add_argument(
            "--unprotected",
            action="store_true",
            help="Allow image to be deleted (default)",
        )
        public_group = parser.add_mutually_exclusive_group()
        public_group.add_argument(
            "--public",
            action="store_true",
            help="Image is accessible to the public",
        )
        public_group.add_argument(
            "--private",
            action="store_true",
            help="Image is inaccessible to the public (default)",
        )
        parser.add_argument(
            "--property",
            dest="properties",
            metavar="<key=value>",
            action=parseractions.KeyValueAction,
            help="Set an image property "
                 "(repeat option to set multiple properties)",
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        image_client = self.app.client_manager.image

        kwargs = {}
        copy_attrs = ('name', 'owner', 'min_disk', 'min_ram', 'properties')
        for attr in copy_attrs:
            if attr in parsed_args:
                val = getattr(parsed_args, attr, None)
                if val:
                    # Only include a value in kwargs for attributes that are
                    # actually present on the command line
                    kwargs[attr] = val
        # Handle exclusive booleans with care
        # Avoid including attributes in kwargs if an option is not
        # present on the command line.  These exclusive booleans are not
        # a single value for the pair of options because the default must be
        # to do nothing when no options are present as opposed to always
        # setting a default.
        if parsed_args.protected:
            kwargs['protected'] = True
        if parsed_args.unprotected:
            kwargs['protected'] = False
        if parsed_args.public:
            kwargs['is_public'] = True
        if parsed_args.private:
            kwargs['is_public'] = False

        if not kwargs:
            self.log.warning('no arguments specified')
            return {}, {}

        image = utils.find_resource(
            image_client.images,
            parsed_args.image,
        )

        if image.properties and parsed_args.properties:
            image.properties.update(kwargs['properties'])
            kwargs['properties'] = image.properties

        image = image_client.images.update(image.id, **kwargs)

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
        self.log.debug("take_action(%s)", parsed_args)

        image_client = self.app.client_manager.image
        image = utils.find_resource(
            image_client.images,
            parsed_args.image,
        )

        info = {}
        info.update(image._info)
        return zip(*sorted(six.iteritems(info)))
