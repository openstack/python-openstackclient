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

import argparse
from base64 import b64encode
import logging

from glanceclient.common import utils as gc_utils
from openstack.image import image_signer
from osc_lib.api import utils as api_utils
from osc_lib.cli import format_columns
from osc_lib.cli import parseractions
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils
import six

from openstackclient.i18n import _
from openstackclient.identity import common


CONTAINER_CHOICES = ["ami", "ari", "aki", "bare", "docker", "ova", "ovf"]
DEFAULT_CONTAINER_FORMAT = 'bare'
DEFAULT_DISK_FORMAT = 'raw'
DISK_CHOICES = ["ami", "ari", "aki", "vhd", "vmdk", "raw", "qcow2", "vhdx",
                "vdi", "iso", "ploop"]
MEMBER_STATUS_CHOICES = ["accepted", "pending", "rejected", "all"]


LOG = logging.getLogger(__name__)


def _format_image(image):
    """Format an image to make it more consistent with OSC operations."""

    info = {}
    properties = {}

    # the only fields we're not including is "links", "tags" and the properties
    fields_to_show = ['status', 'name', 'container_format', 'created_at',
                      'size', 'disk_format', 'updated_at', 'visibility',
                      'min_disk', 'protected', 'id', 'file', 'checksum',
                      'owner', 'virtual_size', 'min_ram', 'schema']

    # split out the usual key and the properties which are top-level
    for key in six.iterkeys(image):
        if key in fields_to_show:
            info[key] = image.get(key)
        elif key == 'tags':
            continue  # handle this later
        else:
            properties[key] = image.get(key)

    # format the tags if they are there
    info['tags'] = format_columns.ListColumn(image.get('tags'))

    # add properties back into the dictionary as a top-level key
    if properties:
        info['properties'] = format_columns.DictColumn(properties)

    return info


class AddProjectToImage(command.ShowOne):
    _description = _("Associate project with image")

    def get_parser(self, prog_name):
        parser = super(AddProjectToImage, self).get_parser(prog_name)
        parser.add_argument(
            "image",
            metavar="<image>",
            help=_("Image to share (name or ID)"),
        )
        parser.add_argument(
            "project",
            metavar="<project>",
            help=_("Project to associate with image (ID)"),
        )
        common.add_project_domain_option_to_parser(parser)
        return parser

    def take_action(self, parsed_args):
        image_client = self.app.client_manager.image
        identity_client = self.app.client_manager.identity

        project_id = common.find_project(identity_client,
                                         parsed_args.project,
                                         parsed_args.project_domain).id

        image_id = utils.find_resource(
            image_client.images,
            parsed_args.image).id

        image_member = image_client.image_members.create(
            image_id,
            project_id,
        )

        return zip(*sorted(six.iteritems(image_member)))


class CreateImage(command.ShowOne):
    _description = _("Create/upload an image")

    deadopts = ('size', 'location', 'copy-from', 'checksum', 'store')

    def get_parser(self, prog_name):
        parser = super(CreateImage, self).get_parser(prog_name)
        # TODO(bunting): There are additional arguments that v1 supported
        # that v2 either doesn't support or supports weirdly.
        # --checksum - could be faked clientside perhaps?
        # --location - maybe location add?
        # --size - passing image size is actually broken in python-glanceclient
        # --copy-from - does not exist in v2
        # --store - does not exits in v2
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
            "--container-format",
            default=DEFAULT_CONTAINER_FORMAT,
            choices=CONTAINER_CHOICES,
            metavar="<container-format>",
            help=(_("Image container format. "
                    "The supported options are: %(option_list)s. "
                    "The default format is: %(default_opt)s") %
                  {'option_list': ', '.join(CONTAINER_CHOICES),
                   'default_opt': DEFAULT_CONTAINER_FORMAT})
        )
        parser.add_argument(
            "--disk-format",
            default=DEFAULT_DISK_FORMAT,
            choices=DISK_CHOICES,
            metavar="<disk-format>",
            help=_("Image disk format. The supported options are: %s. "
                   "The default format is: raw") % ', '.join(DISK_CHOICES)
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
            '--sign-key-path',
            metavar="<sign-key-path>",
            default=[],
            help=_("Sign the image using the specified private key. "
                   "Only use in combination with --sign-cert-id")
        )
        parser.add_argument(
            '--sign-cert-id',
            metavar="<sign-cert-id>",
            default=[],
            help=_("The specified certificate UUID is a reference to "
                   "the certificate in the key manager that corresponds "
                   "to the public key and is used for signature validation. "
                   "Only use in combination with --sign-key-path")
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
        public_group.add_argument(
            "--community",
            action="store_true",
            help=_("Image is accessible to the community"),
        )
        public_group.add_argument(
            "--shared",
            action="store_true",
            help=_("Image can be shared"),
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
            "--tag",
            dest="tags",
            metavar="<tag>",
            action='append',
            help=_("Set a tag on this image "
                   "(repeat option to set multiple tags)"),
        )
        parser.add_argument(
            "--project",
            metavar="<project>",
            help=_("Set an alternate project on this image (name or ID)"),
        )
        common.add_project_domain_option_to_parser(parser)
        for deadopt in self.deadopts:
            parser.add_argument(
                "--%s" % deadopt,
                metavar="<%s>" % deadopt,
                dest=deadopt.replace('-', '_'),
                help=argparse.SUPPRESS,
            )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        image_client = self.app.client_manager.image

        for deadopt in self.deadopts:
            if getattr(parsed_args, deadopt.replace('-', '_'), None):
                raise exceptions.CommandError(
                    _("ERROR: --%s was given, which is an Image v1 option"
                      " that is no longer supported in Image v2") % deadopt)

        # Build an attribute dict from the parsed args, only include
        # attributes that were actually set on the command line
        kwargs = {}
        copy_attrs = ('name', 'id',
                      'container_format', 'disk_format',
                      'min_disk', 'min_ram', 'tags', 'visibility')
        for attr in copy_attrs:
            if attr in parsed_args:
                val = getattr(parsed_args, attr, None)
                if val:
                    # Only include a value in kwargs for attributes that
                    # are actually present on the command line
                    kwargs[attr] = val

        # properties should get flattened into the general kwargs
        if getattr(parsed_args, 'properties', None):
            for k, v in six.iteritems(parsed_args.properties):
                kwargs[k] = str(v)

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
            kwargs['visibility'] = 'public'
        if parsed_args.private:
            kwargs['visibility'] = 'private'
        if parsed_args.community:
            kwargs['visibility'] = 'community'
        if parsed_args.shared:
            kwargs['visibility'] = 'shared'
        if parsed_args.project:
            kwargs['owner'] = common.find_project(
                identity_client,
                parsed_args.project,
                parsed_args.project_domain,
            ).id

        # open the file first to ensure any failures are handled before the
        # image is created
        fp = gc_utils.get_data_file(parsed_args)
        info = {}
        if fp is not None and parsed_args.volume:
            raise exceptions.CommandError(_("Uploading data and using "
                                            "container are not allowed at "
                                            "the same time"))

        if fp is None and parsed_args.file:
            LOG.warning(_("Failed to get an image file."))
            return {}, {}

        # sign an image using a given local private key file
        if parsed_args.sign_key_path or parsed_args.sign_cert_id:
            if not parsed_args.file:
                msg = (_("signing an image requires the --file option, "
                         "passing files via stdin when signing is not "
                         "supported."))
                raise exceptions.CommandError(msg)
            if (len(parsed_args.sign_key_path) < 1 or
                    len(parsed_args.sign_cert_id) < 1):
                msg = (_("'sign-key-path' and 'sign-cert-id' must both be "
                         "specified when attempting to sign an image."))
                raise exceptions.CommandError(msg)
            else:
                sign_key_path = parsed_args.sign_key_path
                sign_cert_id = parsed_args.sign_cert_id
                signer = image_signer.ImageSigner()
                try:
                    pw = utils.get_password(
                        self.app.stdin,
                        prompt=("Please enter private key password, leave "
                                "empty if none: "),
                        confirm=False)
                    if not pw or len(pw) < 1:
                        pw = None
                    signer.load_private_key(
                        sign_key_path,
                        password=pw)
                except Exception:
                    msg = (_("Error during sign operation: private key could "
                             "not be loaded."))
                    raise exceptions.CommandError(msg)

                signature = signer.generate_signature(fp)
                signature_b64 = b64encode(signature)
                kwargs['img_signature'] = signature_b64
                kwargs['img_signature_certificate_uuid'] = sign_cert_id
                kwargs['img_signature_hash_method'] = signer.hash_method
                if signer.padding_method:
                    kwargs['img_signature_key_type'] = signer.padding_method

        # If a volume is specified.
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
            try:
                info['volume_type'] = info['volume_type']['name']
            except TypeError:
                info['volume_type'] = None
        else:
            image = image_client.images.create(**kwargs)

        if fp is not None:
            with fp:
                try:
                    image_client.images.upload(image.id, fp)
                except Exception:
                    # If the upload fails for some reason attempt to remove the
                    # dangling queued image made by the create() call above but
                    # only if the user did not specify an id which indicates
                    # the Image already exists and should be left alone.
                    try:
                        if 'id' not in kwargs:
                            image_client.images.delete(image.id)
                    except Exception:
                        pass  # we don't care about this one
                    raise  # now, throw the upload exception again

                # update the image after the data has been uploaded
                image = image_client.images.get(image.id)

        if not info:
            info = _format_image(image)

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

        del_result = 0
        image_client = self.app.client_manager.image
        for image in parsed_args.images:
            try:
                image_obj = utils.find_resource(
                    image_client.images,
                    image,
                )
                image_client.images.delete(image_obj.id)
            except Exception as e:
                del_result += 1
                LOG.error(_("Failed to delete image with name or "
                            "ID '%(image)s': %(e)s"),
                          {'image': image, 'e': e})

        total = len(parsed_args.images)
        if (del_result > 0):
            msg = (_("Failed to delete %(dresult)s of %(total)s images.")
                   % {'dresult': del_result, 'total': total})
            raise exceptions.CommandError(msg)


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
        public_group.add_argument(
            "--community",
            dest="community",
            action="store_true",
            default=False,
            help=_("List only community images"),
        )
        public_group.add_argument(
            "--shared",
            dest="shared",
            action="store_true",
            default=False,
            help=_("List only shared images"),
        )
        parser.add_argument(
            '--property',
            metavar='<key=value>',
            action=parseractions.KeyValueAction,
            help=_('Filter output based on property '
                   '(repeat option to filter on multiple properties)'),
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            default=None,
            help=_("Filter images based on name.")
        )
        parser.add_argument(
            '--status',
            metavar='<status>',
            default=None,
            help=_("Filter images based on status.")
        )
        parser.add_argument(
            '--member-status',
            metavar='<member-status>',
            default=None,
            type=lambda s: s.lower(),
            choices=MEMBER_STATUS_CHOICES,
            help=(_("Filter images based on member status. "
                    "The supported options are: %s. ") %
                  ', '.join(MEMBER_STATUS_CHOICES))
        )
        parser.add_argument(
            '--tag',
            metavar='<tag>',
            default=None,
            help=_('Filter images based on tag.'),
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
        parser.add_argument(
            "--limit",
            metavar="<num-images>",
            type=int,
            help=_("Maximum number of images to display."),
        )
        parser.add_argument(
            '--marker',
            metavar='<image>',
            default=None,
            help=_("The last image of the previous page. Display "
                   "list of images after marker. Display all images if not "
                   "specified. (name or ID)"),
        )
        return parser

    def take_action(self, parsed_args):
        image_client = self.app.client_manager.image

        kwargs = {}
        if parsed_args.public:
            kwargs['public'] = True
        if parsed_args.private:
            kwargs['private'] = True
        if parsed_args.community:
            kwargs['community'] = True
        if parsed_args.shared:
            kwargs['shared'] = True
        if parsed_args.limit:
            kwargs['limit'] = parsed_args.limit
        if parsed_args.marker:
            kwargs['marker'] = utils.find_resource(image_client.images,
                                                   parsed_args.marker).id
        if parsed_args.name:
            kwargs['name'] = parsed_args.name
        if parsed_args.status:
            kwargs['status'] = parsed_args.status
        if parsed_args.member_status:
            kwargs['member_status'] = parsed_args.member_status
        if parsed_args.tag:
            kwargs['tag'] = parsed_args.tag
        if parsed_args.long:
            columns = (
                'ID',
                'Name',
                'Disk Format',
                'Container Format',
                'Size',
                'Checksum',
                'Status',
                'visibility',
                'protected',
                'owner',
                'tags',
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
                'Tags',
            )
        else:
            columns = ("ID", "Name", "Status")
            column_headers = columns

        # List of image data received
        data = []
        limit = None
        if 'limit' in kwargs:
            limit = kwargs['limit']
        if 'marker' in kwargs:
            data = image_client.api.image_list(**kwargs)
        else:
            # No pages received yet, so start the page marker at None.
            marker = None
            while True:
                page = image_client.api.image_list(marker=marker, **kwargs)
                if not page:
                    break
                data.extend(page)
                # Set the marker to the id of the last item we received
                marker = page[-1]['id']
                if limit:
                    break

        if parsed_args.property:
            for attr, value in parsed_args.property.items():
                api_utils.simple_filter(
                    data,
                    attr=attr,
                    value=value,
                    property_field='properties',
                )

        data = utils.sort_items(data, parsed_args.sort, str)

        return (
            column_headers,
            (utils.get_dict_properties(
                s,
                columns,
                formatters={
                    'tags': format_columns.ListColumn,
                },
            ) for s in data)
        )


class ListImageProjects(command.Lister):
    _description = _("List projects associated with image")

    def get_parser(self, prog_name):
        parser = super(ListImageProjects, self).get_parser(prog_name)
        parser.add_argument(
            "image",
            metavar="<image>",
            help=_("Image (name or ID)"),
        )
        common.add_project_domain_option_to_parser(parser)
        return parser

    def take_action(self, parsed_args):
        image_client = self.app.client_manager.image
        columns = (
            "Image ID",
            "Member ID",
            "Status"
        )

        image_id = utils.find_resource(
            image_client.images,
            parsed_args.image).id

        data = image_client.image_members.list(image_id)

        return (columns,
                (utils.get_item_properties(
                    s, columns,
                ) for s in data))


class RemoveProjectImage(command.Command):
    _description = _("Disassociate project with image")

    def get_parser(self, prog_name):
        parser = super(RemoveProjectImage, self).get_parser(prog_name)
        parser.add_argument(
            "image",
            metavar="<image>",
            help=_("Image to unshare (name or ID)"),
        )
        parser.add_argument(
            "project",
            metavar="<project>",
            help=_("Project to disassociate with image (name or ID)"),
        )
        common.add_project_domain_option_to_parser(parser)
        return parser

    def take_action(self, parsed_args):
        image_client = self.app.client_manager.image
        identity_client = self.app.client_manager.identity

        project_id = common.find_project(identity_client,
                                         parsed_args.project,
                                         parsed_args.project_domain).id

        image_id = utils.find_resource(
            image_client.images,
            parsed_args.image).id

        image_client.image_members.delete(image_id, project_id)


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
        data = image_client.images.data(image.id)

        if data.wrapped is None:
            msg = _('Image %s has no data.') % image.id
            LOG.error(msg)
            self.app.stdout.write(msg + '\n')
            raise SystemExit

        gc_utils.save_image(data, parsed_args.file)


class SetImage(command.Command):
    _description = _("Set image properties")

    deadopts = ('visibility',)

    def get_parser(self, prog_name):
        parser = super(SetImage, self).get_parser(prog_name)
        # TODO(bunting): There are additional arguments that v1 supported
        # --size - does not exist in v2
        # --store - does not exist in v2
        # --location - maybe location add?
        # --copy-from - does not exist in v2
        # --file - should be able to upload file
        # --volume - not possible with v2 as can't change id
        # --force - see `--volume`
        # --checksum - maybe could be done client side
        # --stdin - could be implemented
        parser.add_argument(
            "image",
            metavar="<image>",
            help=_("Image to modify (name or ID)")
        )
        parser.add_argument(
            "--name",
            metavar="<name>",
            help=_("New image name")
        )
        parser.add_argument(
            "--min-disk",
            type=int,
            metavar="<disk-gb>",
            help=_("Minimum disk size needed to boot image, in gigabytes")
        )
        parser.add_argument(
            "--min-ram",
            type=int,
            metavar="<ram-mb>",
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
            help=_("Image disk format. The supported options are: %s") %
            ', '.join(DISK_CHOICES)
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
        public_group.add_argument(
            "--community",
            action="store_true",
            help=_("Image is accessible to the community"),
        )
        public_group.add_argument(
            "--shared",
            action="store_true",
            help=_("Image can be shared"),
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
            "--tag",
            dest="tags",
            metavar="<tag>",
            default=None,
            action='append',
            help=_("Set a tag on this image "
                   "(repeat option to set multiple tags)"),
        )
        parser.add_argument(
            "--architecture",
            metavar="<architecture>",
            help=_("Operating system architecture"),
        )
        parser.add_argument(
            "--instance-id",
            metavar="<instance-id>",
            help=_("ID of server instance used to create this image"),
        )
        parser.add_argument(
            "--instance-uuid",
            metavar="<instance-id>",
            dest="instance_id",
            help=argparse.SUPPRESS,
        )
        parser.add_argument(
            "--kernel-id",
            metavar="<kernel-id>",
            help=_("ID of kernel image used to boot this disk image"),
        )
        parser.add_argument(
            "--os-distro",
            metavar="<os-distro>",
            help=_("Operating system distribution name"),
        )
        parser.add_argument(
            "--os-version",
            metavar="<os-version>",
            help=_("Operating system distribution version"),
        )
        parser.add_argument(
            "--ramdisk-id",
            metavar="<ramdisk-id>",
            help=_("ID of ramdisk image used to boot this disk image"),
        )
        deactivate_group = parser.add_mutually_exclusive_group()
        deactivate_group.add_argument(
            "--deactivate",
            action="store_true",
            help=_("Deactivate the image"),
        )
        deactivate_group.add_argument(
            "--activate",
            action="store_true",
            help=_("Activate the image"),
        )
        parser.add_argument(
            "--project",
            metavar="<project>",
            help=_("Set an alternate project on this image (name or ID)"),
        )
        common.add_project_domain_option_to_parser(parser)
        for deadopt in self.deadopts:
            parser.add_argument(
                "--%s" % deadopt,
                metavar="<%s>" % deadopt,
                dest=deadopt.replace('-', '_'),
                help=argparse.SUPPRESS,
            )

        membership_group = parser.add_mutually_exclusive_group()
        membership_group.add_argument(
            "--accept",
            action="store_true",
            help=_("Accept the image membership"),
        )
        membership_group.add_argument(
            "--reject",
            action="store_true",
            help=_("Reject the image membership"),
        )
        membership_group.add_argument(
            "--pending",
            action="store_true",
            help=_("Reset the image membership to 'pending'"),
        )
        return parser

    def take_action(self, parsed_args):
        identity_client = self.app.client_manager.identity
        image_client = self.app.client_manager.image

        for deadopt in self.deadopts:
            if getattr(parsed_args, deadopt.replace('-', '_'), None):
                raise exceptions.CommandError(
                    _("ERROR: --%s was given, which is an Image v1 option"
                      " that is no longer supported in Image v2") % deadopt)

        kwargs = {}
        copy_attrs = ('architecture', 'container_format', 'disk_format',
                      'file', 'instance_id', 'kernel_id', 'locations',
                      'min_disk', 'min_ram', 'name', 'os_distro', 'os_version',
                      'prefix', 'progress', 'ramdisk_id', 'tags', 'visibility')
        for attr in copy_attrs:
            if attr in parsed_args:
                val = getattr(parsed_args, attr, None)
                if val is not None:
                    # Only include a value in kwargs for attributes that are
                    # actually present on the command line
                    kwargs[attr] = val

        # Properties should get flattened into the general kwargs
        if getattr(parsed_args, 'properties', None):
            for k, v in six.iteritems(parsed_args.properties):
                kwargs[k] = str(v)

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
            kwargs['visibility'] = 'public'
        if parsed_args.private:
            kwargs['visibility'] = 'private'
        if parsed_args.community:
            kwargs['visibility'] = 'community'
        if parsed_args.shared:
            kwargs['visibility'] = 'shared'
        project_id = None
        if parsed_args.project:
            project_id = common.find_project(
                identity_client,
                parsed_args.project,
                parsed_args.project_domain,
            ).id
            kwargs['owner'] = project_id

        image = utils.find_resource(
            image_client.images, parsed_args.image)

        activation_status = None
        if parsed_args.deactivate:
            image_client.images.deactivate(image.id)
            activation_status = "deactivated"
        if parsed_args.activate:
            image_client.images.reactivate(image.id)
            activation_status = "activated"

        membership_group_args = ('accept', 'reject', 'pending')
        membership_status = [status for status in membership_group_args
                             if getattr(parsed_args, status)]
        if membership_status:
            # If a specific project is not passed, assume we want to update
            # our own membership
            if not project_id:
                project_id = self.app.client_manager.auth_ref.project_id
            # The mutually exclusive group of the arg parser ensure we have at
            # most one item in the membership_status list.
            if membership_status[0] != 'pending':
                membership_status[0] += 'ed'  # Glance expects the past form
            image_client.image_members.update(
                image.id, project_id, membership_status[0])

        if parsed_args.tags:
            # Tags should be extended, but duplicates removed
            kwargs['tags'] = list(set(image.tags).union(set(parsed_args.tags)))

        try:
            image = image_client.images.update(image.id, **kwargs)
        except Exception:
            if activation_status is not None:
                LOG.info(_("Image %(id)s was %(status)s."),
                         {'id': image.id, 'status': activation_status})
            raise


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
        if parsed_args.human_readable:
            image['size'] = utils.format_size(image['size'])

        info = _format_image(image)
        return zip(*sorted(six.iteritems(info)))


class UnsetImage(command.Command):
    _description = _("Unset image tags and properties")

    def get_parser(self, prog_name):
        parser = super(UnsetImage, self).get_parser(prog_name)
        parser.add_argument(
            "image",
            metavar="<image>",
            help=_("Image to modify (name or ID)"),
        )
        parser.add_argument(
            "--tag",
            dest="tags",
            metavar="<tag>",
            default=[],
            action='append',
            help=_("Unset a tag on this image "
                   "(repeat option to unset multiple tags)"),
        )
        parser.add_argument(
            "--property",
            dest="properties",
            metavar="<property-key>",
            default=[],
            action='append',
            help=_("Unset a property on this image "
                   "(repeat option to unset multiple properties)"),
        )
        return parser

    def take_action(self, parsed_args):
        image_client = self.app.client_manager.image
        image = utils.find_resource(
            image_client.images,
            parsed_args.image,
        )

        kwargs = {}
        tagret = 0
        propret = 0
        if parsed_args.tags:
            for k in parsed_args.tags:
                try:
                    image_client.image_tags.delete(image.id, k)
                except Exception:
                    LOG.error(_("tag unset failed, '%s' is a "
                                "nonexistent tag "), k)
                    tagret += 1

        if parsed_args.properties:
            for k in parsed_args.properties:
                if k not in image:
                    LOG.error(_("property unset failed, '%s' is a "
                                "nonexistent property "), k)
                    propret += 1
            image_client.images.update(
                image.id,
                parsed_args.properties,
                **kwargs)

        tagtotal = len(parsed_args.tags)
        proptotal = len(parsed_args.properties)
        if (tagret > 0 and propret > 0):
            msg = (_("Failed to unset %(tagret)s of %(tagtotal)s tags,"
                   "Failed to unset %(propret)s of %(proptotal)s properties.")
                   % {'tagret': tagret, 'tagtotal': tagtotal,
                      'propret': propret, 'proptotal': proptotal})
            raise exceptions.CommandError(msg)
        elif tagret > 0:
            msg = (_("Failed to unset %(tagret)s of %(tagtotal)s tags.")
                   % {'tagret': tagret, 'tagtotal': tagtotal})
            raise exceptions.CommandError(msg)
        elif propret > 0:
            msg = (_("Failed to unset %(propret)s of %(proptotal)s"
                   " properties.")
                   % {'propret': propret, 'proptotal': proptotal})
            raise exceptions.CommandError(msg)
