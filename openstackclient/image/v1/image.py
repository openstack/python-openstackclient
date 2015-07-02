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

import argparse
import io
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
from openstackclient.api import utils as api_utils
from openstackclient.common import parseractions
from openstackclient.common import utils


DEFAULT_CONTAINER_FORMAT = 'bare'
DEFAULT_DISK_FORMAT = 'raw'


def _format_visibility(data):
    """Return a formatted visibility string

    :param data:
        The server's visibility (is_public) status value: True, False
    :rtype:
        A string formatted to public/private
    """

    if data:
        return 'public'
    else:
        return 'private'


class CreateImage(show.ShowOne):
    """Create/upload an image"""

    log = logging.getLogger(__name__ + ".CreateImage")

    def get_parser(self, prog_name):
        parser = super(CreateImage, self).get_parser(prog_name)
        parser.add_argument(
            "name",
            metavar="<image-name>",
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
            help="Set a property on this image "
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
                      'location', 'copy_from', 'volume', 'force',
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
                kwargs["data"] = io.open(parsed_args.file, "rb")
            else:
                # Read file from stdin
                if sys.stdin.isatty() is not True:
                    if msvcrt:
                        msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
                    # Send an open file handle to glanceclient so it will
                    # do a chunked transfer
                    kwargs["data"] = sys.stdin

        # Wrap the call to catch exceptions in order to close files
        try:
            image = image_client.images.create(**kwargs)
        finally:
            # Clean up open files - make sure data isn't a string
            if ('data' in kwargs and hasattr(kwargs['data'], 'close') and
               kwargs['data'] != sys.stdin):
                    kwargs['data'].close()

        info = {}
        info.update(image._info)
        info['properties'] = utils.format_dict(info.get('properties', {}))
        return zip(*sorted(six.iteritems(info)))


class DeleteImage(command.Command):
    """Delete image(s)"""

    log = logging.getLogger(__name__ + ".DeleteImage")

    def get_parser(self, prog_name):
        parser = super(DeleteImage, self).get_parser(prog_name)
        parser.add_argument(
            "images",
            metavar="<image>",
            nargs="+",
            help="Image(s) to delete (name or ID)",
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        image_client = self.app.client_manager.image
        for image in parsed_args.images:
            image_obj = utils.find_resource(
                image_client.images,
                image,
            )
            image_client.images.delete(image_obj.id)


class ListImage(lister.Lister):
    """List available images"""

    log = logging.getLogger(__name__ + ".ListImage")

    def get_parser(self, prog_name):
        parser = super(ListImage, self).get_parser(prog_name)
        public_group = parser.add_mutually_exclusive_group()
        public_group.add_argument(
            "--public",
            dest="public",
            action="store_true",
            default=False,
            help="List only public images",
        )
        public_group.add_argument(
            "--private",
            dest="private",
            action="store_true",
            default=False,
            help="List only private images",
        )
        # Included for silent CLI compatibility with v2
        public_group.add_argument(
            "--shared",
            dest="shared",
            action="store_true",
            default=False,
            help=argparse.SUPPRESS,
        )
        parser.add_argument(
            '--property',
            metavar='<key=value>',
            action=parseractions.KeyValueAction,
            help='Filter output based on property',
        )
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help='List additional fields in output',
        )

        # --page-size has never worked, leave here for silent compatibility
        # We'll implement limit/marker differently later
        parser.add_argument(
            "--page-size",
            metavar="<size>",
            help=argparse.SUPPRESS,
        )
        parser.add_argument(
            '--sort',
            metavar="<key>[:<direction>]",
            help="Sort output by selected keys and directions(asc or desc) "
                 "(default: asc), multiple keys and directions can be "
                 "specified separated by comma",
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)

        image_client = self.app.client_manager.image

        kwargs = {}
        if parsed_args.public:
            kwargs['public'] = True
        if parsed_args.private:
            kwargs['private'] = True
        kwargs['detailed'] = bool(parsed_args.property or parsed_args.long)

        if parsed_args.long:
            columns = (
                'ID',
                'Name',
                'Disk Format',
                'Container Format',
                'Size',
                'Status',
                'is_public',
                'protected',
                'owner',
                'properties',
            )
            column_headers = (
                'ID',
                'Name',
                'Disk Format',
                'Container Format',
                'Size',
                'Status',
                'Visibility',
                'Protected',
                'Owner',
                'Properties',
            )
        else:
            columns = ("ID", "Name")
            column_headers = columns

        # List of image data received
        data = []
        # No pages received yet, so start the page marker at None.
        marker = None
        while True:
            page = image_client.api.image_list(marker=marker, **kwargs)
            if not page:
                break
            data.extend(page)
            # Set the marker to the id of the last item we received
            marker = page[-1]['id']

        if parsed_args.property:
            # NOTE(dtroyer): coerce to a list to subscript it in py3
            attr, value = list(parsed_args.property.items())[0]
            api_utils.simple_filter(
                data,
                attr=attr,
                value=value,
                property_field='properties',
            )

        data = utils.sort_items(data, parsed_args.sort)

        return (
            column_headers,
            (utils.get_dict_properties(
                s,
                columns,
                formatters={
                    'is_public': _format_visibility,
                    'properties': utils.format_dict,
                },
            ) for s in data)
        )


class SaveImage(command.Command):
    """Save an image locally"""

    log = logging.getLogger(__name__ + ".SaveImage")

    def get_parser(self, prog_name):
        parser = super(SaveImage, self).get_parser(prog_name)
        parser.add_argument(
            "--file",
            metavar="<filename>",
            help="Downloaded image save filename (default: stdout)",
        )
        parser.add_argument(
            "image",
            metavar="<image>",
            help="Image to save (name or ID)",
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
    """Set image properties"""

    log = logging.getLogger(__name__ + ".SetImage")

    def get_parser(self, prog_name):
        parser = super(SetImage, self).get_parser(prog_name)
        parser.add_argument(
            "image",
            metavar="<image>",
            help="Image to modify (name or ID)",
        )
        parser.add_argument(
            "--name",
            metavar="<name>",
            help="New image name",
        )
        parser.add_argument(
            "--owner",
            metavar="<project>",
            help="New image owner project (name or ID)",
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
        container_choices = ["ami", "ari", "aki", "bare", "ovf"]
        parser.add_argument(
            "--container-format",
            metavar="<container-format>",
            help=("Container format of image. Acceptable formats: %s" %
                  container_choices),
            choices=container_choices
        )
        disk_choices = ["ami", "ari", "aki", "vhd", "vmdk", "raw", "qcow2",
                        "vdi", "iso"]
        parser.add_argument(
            "--disk-format",
            metavar="<disk-format>",
            help="Disk format of image. Acceptable formats: %s" % disk_choices,
            choices=disk_choices
        )
        parser.add_argument(
            "--size",
            metavar="<size>",
            type=int,
            help="Size of image data (in bytes)"
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
            help="Set a property on this image "
                 "(repeat option to set multiple properties)",
        )
        parser.add_argument(
            "--store",
            metavar="<store>",
            help="Upload image to this store",
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
            help="Force image change if volume is in use "
            "(only meaningful with --volume)",
        )
        parser.add_argument(
            "--stdin",
            dest='stdin',
            action='store_true',
            default=False,
            help="Read image data from standard input",
        )
        parser.add_argument(
            "--checksum",
            metavar="<checksum>",
            help="Image hash used for verification",
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)", parsed_args)
        image_client = self.app.client_manager.image

        kwargs = {}
        copy_attrs = ('name', 'owner', 'min_disk', 'min_ram', 'properties',
                      'container_format', 'disk_format', 'size', 'store',
                      'location', 'copy_from', 'volume', 'force', 'checksum')
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

        # Wrap the call to catch exceptions in order to close files
        try:
            image = utils.find_resource(
                image_client.images,
                parsed_args.image,
            )

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
                        parsed_args.image,
                        (parsed_args.container_format
                         if parsed_args.container_format
                         else image.container_format),
                        (parsed_args.disk_format
                         if parsed_args.disk_format
                         else image.disk_format),
                    )
                    info = body['os-volume_upload_image']
                elif parsed_args.file:
                    # Send an open file handle to glanceclient so it will
                    # do a chunked transfer
                    kwargs["data"] = io.open(parsed_args.file, "rb")
                else:
                    # Read file from stdin
                    if sys.stdin.isatty() is not True:
                        if parsed_args.stdin:
                            if msvcrt:
                                msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
                            # Send an open file handle to glanceclient so it
                            # will do a chunked transfer
                            kwargs["data"] = sys.stdin
                        else:
                            self.log.warning('Use --stdin to enable read image'
                                             ' data from standard input')

            if image.properties and parsed_args.properties:
                image.properties.update(kwargs['properties'])
                kwargs['properties'] = image.properties

            if not kwargs:
                self.log.warning('no arguments specified')
                return {}, {}

            image = image_client.images.update(image.id, **kwargs)
        finally:
            # Clean up open files - make sure data isn't a string
            if ('data' in kwargs and hasattr(kwargs['data'], 'close') and
               kwargs['data'] != sys.stdin):
                    kwargs['data'].close()

        info = {}
        info.update(image._info)
        info['properties'] = utils.format_dict(info.get('properties', {}))
        return zip(*sorted(six.iteritems(info)))


class ShowImage(show.ShowOne):
    """Display image details"""

    log = logging.getLogger(__name__ + ".ShowImage")

    def get_parser(self, prog_name):
        parser = super(ShowImage, self).get_parser(prog_name)
        parser.add_argument(
            "image",
            metavar="<image>",
            help="Image to display (name or ID)",
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
        info['properties'] = utils.format_dict(info.get('properties', {}))
        return zip(*sorted(six.iteritems(info)))
