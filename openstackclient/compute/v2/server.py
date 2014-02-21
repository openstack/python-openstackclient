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

import argparse
import getpass
import logging
import os
import six
import sys

from cliff import command
from cliff import lister
from cliff import show

from novaclient.v1_1 import servers
from openstackclient.common import exceptions
from openstackclient.common import parseractions
from openstackclient.common import utils


def _format_servers_list_networks(networks):
    """Return a formatted string of a server's networks

    :param server: a Server.networks field
    :rtype: a string of formatted network addresses
    """
    output = []
    for (network, addresses) in networks.items():
        if not addresses:
            continue
        addresses_csv = ', '.join(addresses)
        group = "%s=%s" % (network, addresses_csv)
        output.append(group)
    return '; '.join(output)


def _prep_server_detail(compute_client, server):
    """Prepare the detailed server dict for printing

    :param compute_client: a compute client instance
    :param server: a Server resource
    :rtype: a dict of server details
    """
    info = server._info.copy()

    # Call .get() to retrieve all of the server information
    # as findall(name=blah) and REST /details are not the same
    # and do not return flavor and image information.
    server = compute_client.servers.get(info['id'])
    info.update(server._info)

    # Convert the image blob to a name
    image_info = info.get('image', {})
    image_id = image_info.get('id', '')
    image = utils.find_resource(compute_client.images, image_id)
    info['image'] = "%s (%s)" % (image.name, image_id)

    # Convert the flavor blob to a name
    flavor_info = info.get('flavor', {})
    flavor_id = flavor_info.get('id', '')
    flavor = utils.find_resource(compute_client.flavors, flavor_id)
    info['flavor'] = "%s (%s)" % (flavor.name, flavor_id)

    # NOTE(dtroyer): novaclient splits these into separate entries...
    # Format addresses in a useful way
    info['addresses'] = _format_servers_list_networks(server.networks)

    # Map 'metadata' field to 'properties'
    info.update(
        {'properties': utils.format_dict(info.pop('metadata'))}
    )

    # Remove values that are long and not too useful
    info.pop('links', None)

    return info


def _show_progress(progress):
    if progress:
        sys.stdout.write('\rProgress: %s' % progress)
        sys.stdout.flush()


class AddServerVolume(command.Command):
    """Add volume to server"""

    log = logging.getLogger(__name__ + '.AddServerVolume')

    def get_parser(self, prog_name):
        parser = super(AddServerVolume, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help='Server (name or ID)',
        )
        parser.add_argument(
            'volume',
            metavar='<volume>',
            help='Volume to add (name or ID)',
        )
        parser.add_argument(
            '--device',
            metavar='<device>',
            help='Server internal device name for volume',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)" % parsed_args)

        compute_client = self.app.client_manager.compute
        volume_client = self.app.client_manager.volume

        server = utils.find_resource(
            compute_client.servers,
            parsed_args.server,
        )
        volume = utils.find_resource(
            volume_client.volumes,
            parsed_args.volume,
        )

        compute_client.volumes.create_server_volume(
            server.id,
            volume.id,
            parsed_args.device,
        )


class AddServerSecurityGroup(command.Command):
    """Add security group to server"""

    log = logging.getLogger(__name__ + '.AddServerSecurityGroup')

    def get_parser(self, prog_name):
        parser = super(AddServerSecurityGroup, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help='Name or ID of server to use',
        )
        parser.add_argument(
            'group',
            metavar='<group>',
            help='Name or ID of security group to add to server',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)" % parsed_args)

        compute_client = self.app.client_manager.compute

        server = utils.find_resource(
            compute_client.servers,
            parsed_args.server,
        )
        security_group = utils.find_resource(
            compute_client.security_groups,
            parsed_args.group,
        )

        server.add_security_group(security_group)
        return


class CreateServer(show.ShowOne):
    """Create a new server"""

    log = logging.getLogger(__name__ + '.CreateServer')

    def get_parser(self, prog_name):
        parser = super(CreateServer, self).get_parser(prog_name)
        parser.add_argument(
            'server_name',
            metavar='<server-name>',
            help='New server name')
        parser.add_argument(
            '--image',
            metavar='<image>',
            required=True,
            help='Create server from this image')
        parser.add_argument(
            '--flavor',
            metavar='<flavor>',
            required=True,
            help='Create server with this flavor')
        parser.add_argument(
            '--security-group',
            metavar='<security-group-name>',
            action='append',
            default=[],
            help='Security group to assign to this server '
                 '(repeat for multiple groups)')
        parser.add_argument(
            '--key-name',
            metavar='<key-name>',
            help='Keypair to inject into this server (optional extension)')
        parser.add_argument(
            '--property',
            metavar='<key=value>',
            action=parseractions.KeyValueAction,
            help='Set a property on this server '
                 '(repeat for multiple values)')
        parser.add_argument(
            '--file',
            metavar='<dest-filename=source-filename>',
            action='append',
            default=[],
            help='File to inject into image before boot '
                 '(repeat for multiple files)')
        parser.add_argument(
            '--user-data',
            metavar='<user-data>',
            help='User data file to serve from the metadata server')
        parser.add_argument(
            '--availability-zone',
            metavar='<zone-name>',
            help='Select an availability zone for the server')
        parser.add_argument(
            '--block-device-mapping',
            metavar='<dev-name=mapping>',
            action='append',
            default=[],
            help='Map block devices; map is '
                 '<id>:<type>:<size(GB)>:<delete_on_terminate> '
                 '(optional extension)')
        parser.add_argument(
            '--nic',
            metavar='<nic-config-string>',
            action='append',
            default=[],
            help='Specify NIC configuration (optional extension)')
        parser.add_argument(
            '--hint',
            metavar='<key=value>',
            action='append',
            default=[],
            help='Hints for the scheduler (optional extension)')
        parser.add_argument(
            '--config-drive',
            metavar='<config-drive-volume>|True',
            default=False,
            help='Use specified volume as the config drive, '
                 'or \'True\' to use an ephemeral drive')
        parser.add_argument(
            '--min',
            metavar='<count>',
            type=int,
            default=1,
            help='Minimum number of servers to launch (default=1)')
        parser.add_argument(
            '--max',
            metavar='<count>',
            type=int,
            default=1,
            help='Maximum number of servers to launch (default=1)')
        parser.add_argument(
            '--wait',
            action='store_true',
            help='Wait for build to complete',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        compute_client = self.app.client_manager.compute

        # Lookup parsed_args.image
        image = utils.find_resource(compute_client.images,
                                    parsed_args.image)

        # Lookup parsed_args.flavor
        flavor = utils.find_resource(compute_client.flavors,
                                     parsed_args.flavor)

        boot_args = [parsed_args.server_name, image, flavor]

        files = {}
        for f in parsed_args.file:
            dst, src = f.split('=', 1)
            try:
                files[dst] = open(src)
            except IOError as e:
                raise exceptions.CommandError("Can't open '%s': %s" % (src, e))

        if parsed_args.min > parsed_args.max:
            raise exceptions.CommandError("min instances should be <= "
                                          "max instances")
        if parsed_args.min < 1:
            raise exceptions.CommandError("min instances should be > 0")
        if parsed_args.max < 1:
            raise exceptions.CommandError("max instances should be > 0")

        userdata = None
        if parsed_args.user_data:
            try:
                userdata = open(parsed_args.user_data)
            except IOError as e:
                raise exceptions.CommandError("Can't open '%s': %s" %
                                              (parsed_args.user_data, e))

        block_device_mapping = dict(v.split('=', 1)
                                    for v in parsed_args.block_device_mapping)

        nics = []
        for nic_str in parsed_args.nic:
            nic_info = {"net-id": "", "v4-fixed-ip": ""}
            nic_info.update(dict(kv_str.split("=", 1)
                            for kv_str in nic_str.split(",")))
            nics.append(nic_info)

        hints = {}
        for hint in parsed_args.hint:
            key, _sep, value = hint.partition('=')
            # NOTE(vish): multiple copies of the same hint will
            #             result in a list of values
            if key in hints:
                if isinstance(hints[key], six.string_types):
                    hints[key] = [hints[key]]
                hints[key] += [value]
            else:
                hints[key] = value

        # What does a non-boolean value for config-drive do?
        # --config-drive argument is either a volume id or
        # 'True' (or '1') to use an ephemeral volume
        if str(parsed_args.config_drive).lower() in ("true", "1"):
            config_drive = True
        elif str(parsed_args.config_drive).lower() in ("false", "0",
                                                       "", "none"):
            config_drive = None
        else:
            config_drive = parsed_args.config_drive

        boot_kwargs = dict(
            meta=parsed_args.property,
            files=files,
            reservation_id=None,
            min_count=parsed_args.min,
            max_count=parsed_args.max,
            security_groups=parsed_args.security_group,
            userdata=userdata,
            key_name=parsed_args.key_name,
            availability_zone=parsed_args.availability_zone,
            block_device_mapping=block_device_mapping,
            nics=nics,
            scheduler_hints=hints,
            config_drive=config_drive)

        self.log.debug('boot_args: %s' % boot_args)
        self.log.debug('boot_kwargs: %s' % boot_kwargs)
        server = compute_client.servers.create(*boot_args, **boot_kwargs)

        if parsed_args.wait:
            if utils.wait_for_status(
                compute_client.servers.get,
                server.id,
                callback=_show_progress,
            ):
                sys.stdout.write('\n')
            else:
                self.log.error('Error creating server: %s' %
                               parsed_args.server_name)
                sys.stdout.write('\nError creating server')
                raise SystemExit

        details = _prep_server_detail(compute_client, server)
        return zip(*sorted(six.iteritems(details)))


class CreateServerImage(show.ShowOne):
    """Create a new disk image from a running server"""

    log = logging.getLogger(__name__ + '.CreateServerImage')

    def get_parser(self, prog_name):
        parser = super(CreateServerImage, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server',
            help='Server (name or ID)',
        )
        parser.add_argument(
            '--name',
            metavar='<image-name>',
            help='Name of new image (default is server name)',
        )
        parser.add_argument(
            '--wait',
            action='store_true',
            help='Wait for image create to complete',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        compute_client = self.app.client_manager.compute
        image_client = self.app.client_manager.image
        server = utils.find_resource(
            compute_client.servers,
            parsed_args.server,
        )
        if parsed_args.name:
            name = parsed_args.name
        else:
            name = server.name

        image = compute_client.servers.create_image(
            server,
            name,
        )

        if parsed_args.wait:
            if utils.wait_for_status(
                image_client.images.get,
                image,
                callback=_show_progress,
            ):
                sys.stdout.write('\n')
            else:
                self.log.error(
                    'Error creating server snapshot: %s' %
                    parsed_args.image_name,
                )
                sys.stdout.write('\nError creating server snapshot')
                raise SystemExit

        image = utils.find_resource(
            image_client.images,
            image.id,
        )

        info = {}
        info.update(image._info)
        return zip(*sorted(six.iteritems(info)))


class DeleteServer(command.Command):
    """Delete server command"""

    log = logging.getLogger(__name__ + '.DeleteServer')

    def get_parser(self, prog_name):
        parser = super(DeleteServer, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help='Name or ID of server to delete')
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        compute_client = self.app.client_manager.compute
        server = utils.find_resource(
            compute_client.servers, parsed_args.server)
        compute_client.servers.delete(server.id)
        return


class ListServer(lister.Lister):
    """List servers"""

    log = logging.getLogger(__name__ + '.ListServer')

    def get_parser(self, prog_name):
        parser = super(ListServer, self).get_parser(prog_name)
        parser.add_argument(
            '--reservation-id',
            metavar='<reservation-id>',
            help='Only return instances that match the reservation')
        parser.add_argument(
            '--ip',
            metavar='<ip-address-regex>',
            help='Regular expression to match IP addresses')
        parser.add_argument(
            '--ip6',
            metavar='<ip-address-regex>',
            help='Regular expression to match IPv6 addresses')
        parser.add_argument(
            '--name',
            metavar='<name>',
            help='Regular expression to match names')
        parser.add_argument(
            '--status',
            metavar='<status>',
            # FIXME(dhellmann): Add choices?
            help='Search by server status')
        parser.add_argument(
            '--flavor',
            metavar='<flavor>',
            help='Search by flavor ID')
        parser.add_argument(
            '--image',
            metavar='<image>',
            help='Search by image ID')
        parser.add_argument(
            '--host',
            metavar='<hostname>',
            help='Search by hostname')
        parser.add_argument(
            '--instance-name',
            metavar='<server-name>',
            help='Regular expression to match instance name (admin only)')
        parser.add_argument(
            '--all-projects',
            action='store_true',
            default=bool(int(os.environ.get("ALL_PROJECTS", 0))),
            help='Include all projects (admin only)')
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help='List additional fields in output')
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        compute_client = self.app.client_manager.compute
        search_opts = {
            'reservation_id': parsed_args.reservation_id,
            'ip': parsed_args.ip,
            'ip6': parsed_args.ip6,
            'name': parsed_args.name,
            'instance_name': parsed_args.instance_name,
            'status': parsed_args.status,
            'flavor': parsed_args.flavor,
            'image': parsed_args.image,
            'host': parsed_args.host,
            'all_tenants': parsed_args.all_projects,
        }
        self.log.debug('search options: %s', search_opts)

        if parsed_args.long:
            columns = (
                'ID',
                'Name',
                'Status',
                'Networks',
                'OS-EXT-AZ:availability_zone',
                'OS-EXT-SRV-ATTR:host',
                'Metadata',
            )
            column_headers = (
                'ID',
                'Name',
                'Status',
                'Networks',
                'Availability Zone',
                'Host',
                'Properties',
            )
            mixed_case_fields = [
                'OS-EXT-AZ:availability_zone',
                'OS-EXT-SRV-ATTR:host',
            ]
        else:
            columns = ('ID', 'Name', 'Status', 'Networks')
            column_headers = columns
            mixed_case_fields = []
        data = compute_client.servers.list(search_opts=search_opts)
        return (column_headers,
                (utils.get_item_properties(
                    s, columns,
                    mixed_case_fields=mixed_case_fields,
                    formatters={
                        'Networks': _format_servers_list_networks,
                        'Metadata': utils.format_dict,
                    },
                ) for s in data))


class LockServer(command.Command):
    """Lock server"""

    log = logging.getLogger(__name__ + '.LockServer')

    def get_parser(self, prog_name):
        parser = super(LockServer, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help='Server (name or ID)',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)

        compute_client = self.app.client_manager.compute
        utils.find_resource(
            compute_client.servers,
            parsed_args.server,
        ).lock()


# FIXME(dtroyer): Here is what I want, how with argparse/cliff?
# server migrate [--wait] \
#   [--live <hostname>
#     [--shared-migration | --block-migration]
#     [--disk-overcommit | --no-disk-overcommit]]
#   <server>
#
# live_parser = parser.add_argument_group(title='Live migration options')
# then adding the groups doesn't seem to work

class MigrateServer(command.Command):
    """Migrate server to different host"""

    log = logging.getLogger(__name__ + '.MigrateServer')

    def get_parser(self, prog_name):
        parser = super(MigrateServer, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help='Server to migrate (name or ID)',
        )
        parser.add_argument(
            '--wait',
            action='store_true',
            help='Wait for resize to complete',
        )
        parser.add_argument(
            '--live',
            metavar='<hostname>',
            help='Target hostname',
        )
        migration_group = parser.add_mutually_exclusive_group()
        migration_group.add_argument(
            '--shared-migration',
            dest='shared_migration',
            action='store_true',
            default=True,
            help='Perform a shared live migration (default)',
        )
        migration_group.add_argument(
            '--block-migration',
            dest='shared_migration',
            action='store_false',
            help='Perform a block live migration',
        )
        disk_group = parser.add_mutually_exclusive_group()
        disk_group.add_argument(
            '--no-disk-overcommit',
            dest='disk_overcommit',
            action='store_false',
            default=False,
            help='Do not over-commit disk on the destination host (default)',
        )
        disk_group.add_argument(
            '--disk-overcommit',
            action='store_true',
            default=False,
            help='Allow disk over-commit on the destination host',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)

        compute_client = self.app.client_manager.compute

        server = utils.find_resource(
            compute_client.servers,
            parsed_args.server,
        )
        if parsed_args.live:
            server.live_migrate(
                parsed_args.live,
                parsed_args.shared_migration,
                parsed_args.disk_overcommit,
            )
        else:
            server.migrate()

        if parsed_args.wait:
            if utils.wait_for_status(
                compute_client.servers.get,
                server.id,
                #callback=_show_progress,
            ):
                sys.stdout.write('Complete\n')
            else:
                sys.stdout.write('\nError migrating server')
                raise SystemExit


class PauseServer(command.Command):
    """Pause server"""

    log = logging.getLogger(__name__ + '.PauseServer')

    def get_parser(self, prog_name):
        parser = super(PauseServer, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help='Server (name or ID)',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)

        compute_client = self.app.client_manager.compute
        utils.find_resource(
            compute_client.servers,
            parsed_args.server,
        ).pause()


class RebootServer(command.Command):
    """Perform a hard or soft server reboot"""

    log = logging.getLogger(__name__ + '.RebootServer')

    def get_parser(self, prog_name):
        parser = super(RebootServer, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help='Server (name or ID)',
        )
        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            '--hard',
            dest='reboot_type',
            action='store_const',
            const=servers.REBOOT_HARD,
            default=servers.REBOOT_SOFT,
            help='Perform a hard reboot',
        )
        group.add_argument(
            '--soft',
            dest='reboot_type',
            action='store_const',
            const=servers.REBOOT_SOFT,
            default=servers.REBOOT_SOFT,
            help='Perform a soft reboot',
        )
        parser.add_argument(
            '--wait',
            action='store_true',
            help='Wait for reboot to complete',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        compute_client = self.app.client_manager.compute
        server = utils.find_resource(
            compute_client.servers, parsed_args.server)
        server.reboot(parsed_args.reboot_type)

        if parsed_args.wait:
            if utils.wait_for_status(
                compute_client.servers.get,
                server.id,
                callback=_show_progress,
            ):
                sys.stdout.write('\nReboot complete\n')
            else:
                sys.stdout.write('\nError rebooting server\n')
                raise SystemExit


class RebuildServer(show.ShowOne):
    """Rebuild server"""

    log = logging.getLogger(__name__ + '.RebuildServer')

    def get_parser(self, prog_name):
        parser = super(RebuildServer, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help='Server (name or ID)',
        )
        parser.add_argument(
            '--image',
            metavar='<image>',
            required=True,
            help='Recreate server from this image',
        )
        parser.add_argument(
            '--password',
            metavar='<password>',
            help="Set the password on the rebuilt instance",
        )
        parser.add_argument(
            '--wait',
            action='store_true',
            help='Wait for rebuild to complete',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        compute_client = self.app.client_manager.compute

        # Lookup parsed_args.image
        image = utils.find_resource(compute_client.images, parsed_args.image)

        server = utils.find_resource(
            compute_client.servers, parsed_args.server)

        server = server.rebuild(image, parsed_args.password)
        if parsed_args.wait:
            if utils.wait_for_status(
                compute_client.servers.get,
                server.id,
                callback=_show_progress,
            ):
                sys.stdout.write('\nComplete\n')
            else:
                sys.stdout.write('\nError rebuilding server')
                raise SystemExit

        details = _prep_server_detail(compute_client, server)
        return zip(*sorted(six.iteritems(details)))


class RemoveServerSecurityGroup(command.Command):
    """Remove security group from server"""

    log = logging.getLogger(__name__ + '.RemoveServerSecurityGroup')

    def get_parser(self, prog_name):
        parser = super(RemoveServerSecurityGroup, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help='Name or ID of server to use',
        )
        parser.add_argument(
            'group',
            metavar='<group>',
            help='Name or ID of security group to remove from server',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)" % parsed_args)

        compute_client = self.app.client_manager.compute

        server = utils.find_resource(
            compute_client.servers,
            parsed_args.server,
        )
        security_group = utils.find_resource(
            compute_client.security_groups,
            parsed_args.group,
        )

        server.remove_security_group(security_group)


class RemoveServerVolume(command.Command):
    """Remove volume from server"""

    log = logging.getLogger(__name__ + '.RemoveServerVolume')

    def get_parser(self, prog_name):
        parser = super(RemoveServerVolume, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help='Server (name or ID)',
        )
        parser.add_argument(
            'volume',
            metavar='<volume>',
            help='Volume to remove (name or ID)',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action(%s)" % parsed_args)

        compute_client = self.app.client_manager.compute
        volume_client = self.app.client_manager.volume

        server = utils.find_resource(
            compute_client.servers,
            parsed_args.server,
        )
        volume = utils.find_resource(
            volume_client.volumes,
            parsed_args.volume,
        )

        compute_client.volumes.delete_server_volume(
            server.id,
            volume.id,
        )


class RescueServer(show.ShowOne):
    """Put server in rescue mode"""

    log = logging.getLogger(__name__ + '.RescueServer')

    def get_parser(self, prog_name):
        parser = super(RescueServer, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help='Server (name or ID)',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)

        compute_client = self.app.client_manager.compute
        server = utils.find_resource(
            compute_client.servers,
            parsed_args.server,
        ).rescue()
        return zip(*sorted(six.iteritems(server._info)))


class ResizeServer(command.Command):
    """Convert server to a new flavor"""

    log = logging.getLogger(__name__ + '.ResizeServer')

    def get_parser(self, prog_name):
        parser = super(ResizeServer, self).get_parser(prog_name)
        phase_group = parser.add_mutually_exclusive_group()
        phase_group.add_argument(
            '--flavor',
            metavar='<flavor>',
            help='Resize server to this flavor',
        )
        phase_group.add_argument(
            '--verify',
            action="store_true",
            help='Verify previous server resize',
        )
        phase_group.add_argument(
            '--revert',
            action="store_true",
            help='Restore server before resize',
        )
        parser.add_argument(
            '--wait',
            action='store_true',
            help='Wait for resize to complete',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)

        compute_client = self.app.client_manager.compute
        server = utils.find_resource(
            compute_client.servers,
            parsed_args.server,
        )
        if parsed_args.flavor:
            flavor = utils.find_resource(
                compute_client.flavors,
                parsed_args.flavor,
            )
            server.resize(flavor)
            if parsed_args.wait:
                if utils.wait_for_status(
                    compute_client.servers.get,
                    server.id,
                    success_status=['active', 'verify_resize'],
                    callback=_show_progress,
                ):
                    sys.stdout.write('Complete\n')
                else:
                    sys.stdout.write('\nError resizing server')
                    raise SystemExit
        elif parsed_args.verify:
            server.confirm_resize()
        elif parsed_args.revert:
            server.revert_resize()


class ResumeServer(command.Command):
    """Resume server"""

    log = logging.getLogger(__name__ + '.ResumeServer')

    def get_parser(self, prog_name):
        parser = super(ResumeServer, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help='Server (name or ID)',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)

        compute_client = self.app.client_manager.compute
        utils.find_resource(
            compute_client.servers,
            parsed_args.server,
        ) .resume()


class SetServer(command.Command):
    """Set server properties"""

    log = logging.getLogger(__name__ + '.SetServer')

    def get_parser(self, prog_name):
        parser = super(SetServer, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help='Server (name or ID)',
        )
        parser.add_argument(
            '--name',
            metavar='<new-name>',
            help='New server name',
        )
        parser.add_argument(
            '--root-password',
            action="store_true",
            help='Set new root password (interactive only)',
        )
        parser.add_argument(
            "--property",
            metavar="<key=value>",
            action=parseractions.KeyValueAction,
            help='Property to add/change for this server '
                 '(repeat option to set multiple properties)',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)

        compute_client = self.app.client_manager.compute
        server = utils.find_resource(
            compute_client.servers,
            parsed_args.server,
        )

        if parsed_args.name:
            server.update(name=parsed_args.name)

        if parsed_args.property:
            compute_client.servers.set_meta(
                server,
                parsed_args.property,
            )

        if parsed_args.root_password:
            p1 = getpass.getpass('New password: ')
            p2 = getpass.getpass('Retype new password: ')
            if p1 == p2:
                server.change_password(p1)
            else:
                raise exceptions.CommandError(
                    "Passwords do not match, password unchanged")


class ShowServer(show.ShowOne):
    """Show server details"""

    log = logging.getLogger(__name__ + '.ShowServer')

    def get_parser(self, prog_name):
        parser = super(ShowServer, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help='Server to show (name or ID)',
        )
        parser.add_argument(
            '--diagnostics',
            action='store_true',
            default=False,
            help='Display diagnostics information for a given server',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        compute_client = self.app.client_manager.compute
        server = utils.find_resource(compute_client.servers,
                                     parsed_args.server)

        if parsed_args.diagnostics:
            (resp, data) = server.diagnostics()
            if not resp.status_code == 200:
                sys.stderr.write("Error retrieving diagnostics data")
                return ({}, {})
        else:
            data = _prep_server_detail(compute_client, server)

        return zip(*sorted(six.iteritems(data)))


class SshServer(command.Command):
    """Ssh to server"""

    log = logging.getLogger(__name__ + '.SshServer')

    def get_parser(self, prog_name):
        parser = super(SshServer, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help='Server (name or ID)',
        )
        parser.add_argument(
            '--login',
            metavar='<login-name>',
            help='Login name (ssh -l option)',
        )
        parser.add_argument(
            '-l',
            metavar='<login-name>',
            help=argparse.SUPPRESS,
        )
        parser.add_argument(
            '--port',
            metavar='<port>',
            type=int,
            help='Destination port (ssh -p option)',
        )
        parser.add_argument(
            '-p',
            metavar='<port>',
            dest='port',
            type=int,
            help=argparse.SUPPRESS,
        )
        parser.add_argument(
            '--identity',
            metavar='<keyfile>',
            help='Private key file (ssh -i option)',
        )
        parser.add_argument(
            '-i',
            metavar='<filename>',
            dest='identity',
            help=argparse.SUPPRESS,
        )
        parser.add_argument(
            '--option',
            metavar='<config-options>',
            help='Options in ssh_config(5) format (ssh -o option)',
        )
        parser.add_argument(
            '-o',
            metavar='<option>',
            dest='option',
            help=argparse.SUPPRESS,
        )
        ip_group = parser.add_mutually_exclusive_group()
        ip_group.add_argument(
            '-4',
            dest='ipv4',
            action='store_true',
            default=False,
            help='Use only IPv4 addresses',
        )
        ip_group.add_argument(
            '-6',
            dest='ipv6',
            action='store_true',
            default=False,
            help='Use only IPv6 addresses',
        )
        type_group = parser.add_mutually_exclusive_group()
        type_group.add_argument(
            '--public',
            dest='address_type',
            action='store_const',
            const='public',
            default='public',
            help='Use public IP address',
        )
        type_group.add_argument(
            '--private',
            dest='address_type',
            action='store_const',
            const='private',
            default='public',
            help='Use private IP address',
        )
        type_group.add_argument(
            '--address-type',
            metavar='<address-type>',
            dest='address_type',
            default='public',
            help='Use other IP address (public, private, etc)',
        )
        parser.add_argument(
            '-v',
            dest='verbose',
            action='store_true',
            default=False,
            help=argparse.SUPPRESS,
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)

        compute_client = self.app.client_manager.compute
        server = utils.find_resource(
            compute_client.servers,
            parsed_args.server,
        )

        # Build the command
        cmd = "ssh"

        # Look for address type
        if parsed_args.address_type:
            address_type = parsed_args.address_type
        if address_type not in server.addresses:
            raise SystemExit("ERROR: No %s IP address found" % address_type)

        # Set up desired address family
        ip_address_family = [4, 6]
        if parsed_args.ipv4:
            ip_address_family = [4]
            cmd += " -4"
        if parsed_args.ipv6:
            ip_address_family = [6]
            cmd += " -6"

        # Grab the first matching IP address
        ip_address = None
        for addr in server.addresses[address_type]:
            if int(addr['version']) in ip_address_family:
                ip_address = addr['addr']
        if not ip_address:
            raise SystemExit("ERROR: No IP address found")

        if parsed_args.port:
            cmd += " -p %d" % parsed_args.port
        if parsed_args.identity:
            cmd += " -i %s" % parsed_args.identity
        if parsed_args.option:
            cmd += " -o %s" % parsed_args.option
        if parsed_args.login:
            login = parsed_args.login
        else:
            login = self.app.client_manager._username
        if parsed_args.verbose:
            cmd += " -v"

        cmd += " %s@%s"
        self.log.debug("ssh command: %s" % (cmd % (login, ip_address)))
        os.system(cmd % (login, ip_address))


class SuspendServer(command.Command):
    """Suspend server"""

    log = logging.getLogger(__name__ + '.SuspendServer')

    def get_parser(self, prog_name):
        parser = super(SuspendServer, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help='Server (name or ID)',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)

        compute_client = self.app.client_manager.compute
        utils.find_resource(
            compute_client.servers,
            parsed_args.server,
        ).suspend()


class UnlockServer(command.Command):
    """Unlock server"""

    log = logging.getLogger(__name__ + '.UnlockServer')

    def get_parser(self, prog_name):
        parser = super(UnlockServer, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help='Server (name or ID)',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)

        compute_client = self.app.client_manager.compute
        utils.find_resource(
            compute_client.servers,
            parsed_args.server,
        ).unlock()


class UnpauseServer(command.Command):
    """Unpause server"""

    log = logging.getLogger(__name__ + '.UnpauseServer')

    def get_parser(self, prog_name):
        parser = super(UnpauseServer, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help='Server (name or ID)',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)

        compute_client = self.app.client_manager.compute
        utils.find_resource(
            compute_client.servers,
            parsed_args.server,
        ).unpause()


class UnrescueServer(command.Command):
    """Restore server from rescue mode"""

    log = logging.getLogger(__name__ + '.UnrescueServer')

    def get_parser(self, prog_name):
        parser = super(UnrescueServer, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help='Server (name or ID)',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)

        compute_client = self.app.client_manager.compute
        utils.find_resource(
            compute_client.servers,
            parsed_args.server,
        ).unrescue()


class UnsetServer(command.Command):
    """Unset server properties"""

    log = logging.getLogger(__name__ + '.UnsetServer')

    def get_parser(self, prog_name):
        parser = super(UnsetServer, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help='Server (name or ID)',
        )
        parser.add_argument(
            '--property',
            metavar='<key>',
            action='append',
            default=[],
            help='Property key to remove from server '
                 '(repeat to set multiple values)',
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        compute_client = self.app.client_manager.compute
        server = utils.find_resource(
            compute_client.servers,
            parsed_args.server,
        )

        if parsed_args.property:
            compute_client.servers.delete_meta(
                server,
                parsed_args.property,
            )
