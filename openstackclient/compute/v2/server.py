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

import getpass
import logging
import os
import six
import sys
import time

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


def _wait_for_status(poll_fn, obj_id, final_ok_states, poll_period=5,
                     status_field="status"):
    """Block while an action is being performed

    :param poll_fn: a function to retrieve the state of the object
    :param obj_id: the id of the object
    :param final_ok_states: a tuple of the states of the object that end the
        wait as success, ex ['active']
    :param poll_period: the wait time between checks of object status
    :param status_field: field name containing the status to be checked
    """
    log = logging.getLogger(__name__ + '._wait_for_status')
    while True:
        obj = poll_fn(obj_id)

        status = getattr(obj, status_field)

        if status:
            status = status.lower()

        if status in final_ok_states:
            log.debug('Wait terminated with success')
            retval = True
            break
        elif status == "error":
            log.error('Wait terminated with an error')
            retval = False
            break

        time.sleep(poll_period)

    return retval


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
            dest='wait',
            action='store_true',
            help='Wait for servers to become active')
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
                if isinstance(hints[key], basestring):
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
            _wait_for_status(compute_client.servers.get, server._info['id'],
                             ['active'])

        details = _prep_server_detail(compute_client, server)
        return zip(*sorted(details.iteritems()))


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
            help='only return instances that match the reservation')
        parser.add_argument(
            '--ip',
            metavar='<ip-address-regex>',
            help='regular expression to match IP address')
        parser.add_argument(
            '--ip6',
            metavar='<ip-address-regex>',
            help='regular expression to match IPv6 address')
        parser.add_argument(
            '--name',
            metavar='<name>',
            help='regular expression to match name')
        parser.add_argument(
            '--status',
            metavar='<status>',
            # FIXME(dhellmann): Add choices?
            help='search by server status')
        parser.add_argument(
            '--flavor',
            metavar='<flavor>',
            help='search by flavor ID')
        parser.add_argument(
            '--image',
            metavar='<image>',
            help='search by image ID')
        parser.add_argument(
            '--host',
            metavar='<hostname>',
            help='search by hostname')
        parser.add_argument(
            '--instance-name',
            metavar='<server-name>',
            help='regular expression to match instance name (admin only)')
        parser.add_argument(
            '--all-tenants',
            action='store_true',
            default=bool(int(os.environ.get("ALL_TENANTS", 0))),
            help='display information from all tenants (admin only)')
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help='Additional fields are listed in output')
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
            'all_tenants': parsed_args.all_tenants,
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
    """Reboot server command"""

    log = logging.getLogger(__name__ + '.RebootServer')

    def get_parser(self, prog_name):
        parser = super(RebootServer, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help='Name or ID of server to reboot')
        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            '--hard',
            dest='reboot_type',
            action='store_const',
            const=servers.REBOOT_HARD,
            default=servers.REBOOT_SOFT,
            help='Perform a hard reboot')
        group.add_argument(
            '--soft',
            dest='reboot_type',
            action='store_const',
            const=servers.REBOOT_SOFT,
            default=servers.REBOOT_SOFT,
            help='Perform a soft reboot')
        parser.add_argument(
            '--wait',
            dest='wait',
            action='store_true',
            help='Wait for server to become active to return')
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        compute_client = self.app.client_manager.compute
        server = utils.find_resource(
            compute_client.servers, parsed_args.server)
        server.reboot(parsed_args.reboot_type)

        if parsed_args.wait:
            _wait_for_status(compute_client.servers.get, server.id,
                             ['active'])

        return


class RebuildServer(show.ShowOne):
    """Rebuild server command"""

    log = logging.getLogger(__name__ + '.RebuildServer')

    def get_parser(self, prog_name):
        parser = super(RebuildServer, self).get_parser(prog_name)
        parser.add_argument(
            'server',
            metavar='<server>',
            help='Server name or ID')
        parser.add_argument(
            '--image',
            metavar='<image>',
            required=True,
            help='Recreate server from this image')
        parser.add_argument(
            '--password',
            metavar='<password>',
            default=False,
            help="Set the provided password on the rebuild instance")
        parser.add_argument(
            '--wait',
            dest='wait',
            action='store_true',
            help='Wait for server to become active to return')
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)' % parsed_args)
        compute_client = self.app.client_manager.compute

        # Lookup parsed_args.image
        image = utils.find_resource(compute_client.images, parsed_args.image)

        server = utils.find_resource(
            compute_client.servers, parsed_args.server)

        _password = None
        if parsed_args.password is not False:
            _password = parsed_args.password

        kwargs = {}
        server = server.rebuild(image, _password, **kwargs)

        # TODO(dtroyer): force silent=True if output filter != table
        if parsed_args.wait:
            _wait_for_status(compute_client.servers.get, server._info['id'],
                             ['active'])

        details = _prep_server_detail(compute_client, server)
        return zip(*sorted(details.iteritems()))


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

        return zip(*sorted(data.iteritems()))


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
