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
import sys

from cliff import columns as cliff_columns
from glanceclient.common import utils as gc_utils
from osc_lib.api import utils as api_utils
from osc_lib.cli import format_columns
from osc_lib.cli import parseractions
from osc_lib.command import command
from osc_lib import utils
import six

from openstackclient.i18n import _

if os.name == "nt":
    import msvcrt
else:
    msvcrt = None


CONTAINER_CHOICES = ["ami", "ari", "aki", "bare", "docker", "ova", "ovf"]
DEFAULT_CONTAINER_FORMAT = 'bare'
DEFAULT_DISK_FORMAT = 'raw'
DISK_CHOICES = ["ami", "ari", "aki", "vhd", "vmdk", "raw", "qcow2", "vhdx",
                "vdi", "iso", "ploop"]


LOG = logging.getLogger(__name__)


class VisibilityColumn(cliff_columns.FormattableColumn):
    def human_readable(self):
        """Return a formatted visibility string

        :rtype:
            A string formatted to public/private
        """

        if self._value:
            return 'public'
        else:
            return 'private'


class CreateImage(command.ShowOne):
    _description = _("Create/upload an image")

    def get_parser(self, prog_name):
        parser = super(CreateImage, self).get_parser(prog_name)
        parser.add_argument(
            "name",
            metavar="<image-name>",
            help=_("New image name"),
        )
        parser.add_argument(
            "--id",
            metavar="<id>",
            help=_("Image ID to reserve"),
        )
        parser.add_argument(
            "--store",
            metavar="<store>",
            help=_("Upload image to this store"),
        )
        parser.add_argument(
            "--container-format",
            default=DEFAULT_CONTAINER_FORMAT,
            metavar="<container-format>",
            choices=CONTAINER_CHOICES,
            help=(_("Image container format. "
                    "The supported options are: %(option_list)s. "
                    "The default format is: %(default_opt)s") %
                  {'option_list': ', '.join(CONTAINER_CHOICES),
                   'default_opt': DEFAULT_CONTAINER_FORMAT})
        )
        parser.add_argument(
            "--disk-format",
            default=DEFAULT_DISK_FORMAT,
            metavar="<disk-format>",
            choices=DISK_CHOICES,
            help=_("Image disk format. The supported options are: %s. "
                   "The default format is: raw") % ', '.join(DISK_CHOICES)
        )
        parser.add_argument(
            "--size",
            metavar="<size>",
            help=_("Image size, in bytes (only used with --location and"
                   " --copy-from)"),
        )
        parser.add_argument(
            "--min-disk",
            metavar="<disk-gb>",
            type=int,
            help=_("Minimum disk size needed to boot image, in gigabytes"),
        )
        parser.add_argument(
            "--min-ram",
            metavar="<ram-mb>",
            type=int,
            help=_("Minimum RAM size needed to boot image, in megabytes"),
        )
        parser.add_argument(
            "--location",
            metavar="<image-url>",
            help=_("Download image from an existing URL"),
        )
        parser.add_argument(
            "--copy-from",
            metavar="<image-url>",
            help=_("Copy image from the data store (similar to --location)"),
        )
        source_group = parser.add_mutually_exclusive_group()
        source_group.add_argument(
            "--file",
            metavar="<file>",
            help=_("Upload image from local file"),
        )
        source_group.add_argument(
            "--volume",
            metavar="<volume>",
            help=_("Create image from a volume"),
        )
        parser.add_argument(
            "--force",
            dest='force',
            action='store_true',
            default=False,
            help=_("Force image creation if volume is in use "
                   "(only meaningful with --volume)"),
        )
        parser.add_argument(
            "--checksum",
            metavar="<checksum>",
            help=_("Image hash used for verification"),
        )
        protected_group = parser.add_mutually_exclusive_group()
        protected_group.add_argument(
            "--protected",
            action="store_true",
            help=_("Prevent image from being deleted"),
        )
        protected_group.add_argument(
            "--unprotected",
            action="store_true",
            help=_("Allow image to be deleted (default)"),
        )
        public_group = parser.add_mutually_exclusive_group()
        public_group.add_argument(
            "--public",
            action="store_true",
            help=_("Image is accessible to the public"),
        )
        public_group.add_argument(
            "--private",
            action="store_true",
            help=_("Image is inaccessible to the public (default)"),
        )
        parser.add_argument(
            "--property",
            dest="properties",
            metavar="<key=value>",
            action=parseractions.KeyValueAction,
            help=_("Set a property on this image "
                   "(repeat option to set multiple properties)"),
        )
        parser.add_argument(
            "--project",
            metavar="<project>",
            help=_("Set an alternate project on this image (name or ID)"),
        )
        return parser

    def take_action(self, parsed_args):
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

        # Special case project option back to API attribute name 'owner'
        val = getattr(parsed_args, 'project', None)
        if val:
            kwargs['owner'] = val

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

        info = {}

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

        if not parsed_args.volume:
            # Wrap the call to catch exceptions in order to close files
            try:
                image = image_client.images.create(**kwargs)
            finally:
                # Clean up open files - make sure data isn't a string
                if ('data' in kwargs and hasattr(kwargs['data'], 'close') and
                        kwargs['data'] != sys.stdin):
                    kwargs['data'].close()

            info.update(image._info)
            info['properties'] = format_columns.DictColumn(
                info.get('properties', {}))
        return zip(*sorted(six.iteritems(info)))


class DeleteImage(command.Command):
    _description = _("Delete image(s)")

    def get_parser(self, prog_name):
        parser = super(DeleteImage, self).get_parser(prog_name)
        parser.add_argument(
            "images",
            metavar="<image>",
            nargs="+",
            help=_("Image(s) to delete (name or ID)"),
        )
        return parser

    def take_action(self, parsed_args):
        image_client = self.app.client_manager.image
        for image in parsed_args.images:
            image_obj = utils.find_resource(
                image_client.images,
                image,
            )
            image_client.images.delete(image_obj.id)


class ListImage(command.Lister):
    _description = _("List available images")

    def get_parser(self, prog_name):
        parser = super(ListImage, self).get_parser(prog_name)
        public_group = parser.add_mutually_exclusive_group()
        public_group.add_argument(
            "--public",
            dest="public",
            action="store_true",
            default=False,
            help=_("List only public images"),
        )
        public_group.add_argument(
            "--private",
            dest="private",
            action="store_true",
            default=False,
            help=_("List only private images"),
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
            help=_('Filter output based on property'),
        )
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_('List additional fields in output'),
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
            default='name:asc',
            help=_("Sort output by selected keys and directions(asc or desc) "
                   "(default: name:asc), multiple keys and directions can be "
                   "specified separated by comma"),
        )
        return parser

    def take_action(self, parsed_args):
        image_client = self.app.client_manager.image

        kwargs = {}
        if parsed_args.public:
            kwargs['public'] = True
        if parsed_args.private:
            kwargs['private'] = True
        # Note: We specifically need to do that below to get the 'status'
        #       column.
        #
        # Always set kwargs['detailed'] to True, and then filter the columns
        # according to whether the --long option is specified or not.
        kwargs['detailed'] = True

        if parsed_args.long:
            columns = (
                'ID',
                'Name',
                'Disk Format',
                'Container Format',
                'Size',
                'Checksum',
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
                'Checksum',
                'Status',
                'Visibility',
                'Protected',
                'Project',
                'Properties',
            )
        else:
            columns = ("ID", "Name", "Status")
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
                    'is_public': VisibilityColumn,
                    'properties': format_columns.DictColumn,
                },
            ) for s in data)
        )


class SaveImage(command.Command):
    _description = _("Save an image locally")

    def get_parser(self, prog_name):
        parser = super(SaveImage, self).get_parser(prog_name)
        parser.add_argument(
            "--file",
            metavar="<filename>",
            help=_("Downloaded image save filename (default: stdout)"),
        )
        parser.add_argument(
            "image",
            metavar="<image>",
            help=_("Image to save (name or ID)"),
        )
        return parser

    def take_action(self, parsed_args):
        image_client = self.app.client_manager.image
        image = utils.find_resource(
            image_client.images,
            parsed_args.image,
        )
        data = image_client.images.data(image)

        gc_utils.save_image(data, parsed_args.file)


class SetImage(command.Command):
    _description = _("Set image properties")

    def get_parser(self, prog_name):
        parser = super(SetImage, self).get_parser(prog_name)
        parser.add_argument(
            "image",
            metavar="<image>",
            help=_("Image to modify (name or ID)"),
        )
        parser.add_argument(
            "--name",
            metavar="<name>",
            help=_("New image name"),
        )
        parser.add_argument(
            "--min-disk",
            metavar="<disk-gb>",
            type=int,
            help=_("Minimum disk size needed to boot image, in gigabytes"),
        )
        parser.add_argument(
            "--min-ram",
            metavar="<disk-ram>",
            type=int,
            help=_("Minimum RAM size needed to boot image, in megabytes"),
        )
        parser.add_argument(
            "--container-format",
            metavar="<container-format>",
            choices=CONTAINER_CHOICES,
            help=_("Image container format. The supported options are: %s") %
            ', '.join(CONTAINER_CHOICES)
        )
        parser.add_argument(
            "--disk-format",
            metavar="<disk-format>",
            choices=DISK_CHOICES,
            help=_("Image disk format. The supported options are: %s.") %
            ', '.join(DISK_CHOICES)
        )
        parser.add_argument(
            "--size",
            metavar="<size>",
            type=int,
            help=_("Size of image data (in bytes)")
        )
        protected_group = parser.add_mutually_exclusive_group()
        protected_group.add_argument(
            "--protected",
            action="store_true",
            help=_("Prevent image from being deleted"),
        )
        protected_group.add_argument(
            "--unprotected",
            action="store_true",
            help=_("Allow image to be deleted (default)"),
        )
        public_group = parser.add_mutually_exclusive_group()
        public_group.add_argument(
            "--public",
            action="store_true",
            help=_("Image is accessible to the public"),
        )
        public_group.add_argument(
            "--private",
            action="store_true",
            help=_("Image is inaccessible to the public (default)"),
        )
        parser.add_argument(
            "--property",
            dest="properties",
            metavar="<key=value>",
            action=parseractions.KeyValueAction,
            help=_("Set a property on this image "
                   "(repeat option to set multiple properties)"),
        )
        parser.add_argument(
            "--store",
            metavar="<store>",
            help=_("Upload image to this store"),
        )
        parser.add_argument(
            "--location",
            metavar="<image-url>",
            help=_("Download image from an existing URL"),
        )
        parser.add_argument(
            "--copy-from",
            metavar="<image-url>",
            help=_("Copy image from the data store (similar to --location)"),
        )
        parser.add_argument(
            "--file",
            metavar="<file>",
            help=_("Upload image from local file"),
        )
        parser.add_argument(
            "--volume",
            metavar="<volume>",
            help=_("Create image from a volume"),
        )
        parser.add_argument(
            "--force",
            dest='force',
            action='store_true',
            default=False,
            help=_("Force image change if volume is in use "
                   "(only meaningful with --volume)"),
        )
        parser.add_argument(
            "--stdin",
            dest='stdin',
            action='store_true',
            default=False,
            help=_("Read image data from standard input"),
        )
        parser.add_argument(
            "--checksum",
            metavar="<checksum>",
            help=_("Image hash used for verification"),
        )
        parser.add_argument(
            "--project",
            metavar="<project>",
            help=_("Set an alternate project on this image (name or ID)"),
        )
        return parser

    def take_action(self, parsed_args):
        image_client = self.app.client_manager.image

        kwargs = {}
        copy_attrs = ('name', 'owner', 'min_disk', 'min_ram', 'properties',
                      'container_format', 'disk_format', 'size', 'store',
                      'location', 'copy_from', 'volume', 'checksum')
        for attr in copy_attrs:
            if attr in parsed_args:
                val = getattr(parsed_args, attr, None)
                if val is not None:
                    # Only include a value in kwargs for attributes that are
                    # actually present on the command line
                    kwargs[attr] = val

        # Special case project option back to API attribute name 'owner'
        val = getattr(parsed_args, 'project', None)
        if val:
            kwargs['owner'] = val

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
        if parsed_args.force:
            kwargs['force'] = True

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
                    volume_client.volumes.upload_to_image(
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
                            LOG.warning(_('Use --stdin to enable read image '
                                          'data from standard input'))

            if image.properties and parsed_args.properties:
                image.properties.update(kwargs['properties'])
                kwargs['properties'] = image.properties

            image = image_client.images.update(image.id, **kwargs)
        finally:
            # Clean up open files - make sure data isn't a string
            if ('data' in kwargs and hasattr(kwargs['data'], 'close') and
                    kwargs['data'] != sys.stdin):
                kwargs['data'].close()


class ShowImage(command.ShowOne):
    _description = _("Display image details")

    def get_parser(self, prog_name):
        parser = super(ShowImage, self).get_parser(prog_name)
        parser.add_argument(
            "--human-readable",
            default=False,
            action='store_true',
            help=_("Print image size in a human-friendly format."),
        )
        parser.add_argument(
            "image",
            metavar="<image>",
            help=_("Image to display (name or ID)"),
        )
        return parser

    def take_action(self, parsed_args):
        image_client = self.app.client_manager.image
        image = utils.find_resource(
            image_client.images,
            parsed_args.image,
        )

        info = {}
        info.update(image._info)
        if parsed_args.human_readable:
            if 'size' in info:
                info['size'] = utils.format_size(info['size'])
        info['properties'] = format_columns.DictColumn(
            info.get('properties', {}))
        return zip(*sorted(six.iteritems(info)))
