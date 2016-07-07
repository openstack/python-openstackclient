======
server
======

Compute v2

server add fixed ip
-------------------

Add fixed IP address to server

.. program:: server add fixed ip
.. code:: bash

    os server add fixed ip
        <server>
        <network>

.. describe:: <server>

    Server (name or ID) to receive the fixed IP address

.. describe:: <network>

    Network (name or ID) to allocate the fixed IP address from

server add floating ip
----------------------

Add floating IP address to server

.. program:: server add floating ip
.. code:: bash

    os server add floating ip
        <server>
        <ip-address>

.. describe:: <server>

    Server (name or ID) to receive the floating IP address

.. describe:: <ip-address>

    Floating IP address (IP address only) to assign to server

server add security group
-------------------------

Add security group to server

.. program:: server add security group
.. code:: bash

    os server add security group
        <server>
        <group>

.. describe:: <server>

    Server (name or ID)

.. describe:: <group>

    Security group to add (name or ID)

server add volume
-----------------

Add volume to server

.. program:: server add volume
.. code:: bash

    os server add volume
        [--device <device>]
        <server>
        <volume>

.. option:: --device <device>

    Server internal device name for volume

.. describe:: <server>

    Server (name or ID)

.. describe:: <volume>

    Volume to add (name or ID)

server create
-------------

Create a new server

.. program:: server create
.. code:: bash

    os server create
        --image <image> | --volume <volume>
        --flavor <flavor>
        [--security-group <security-group-name> [...] ]
        [--key-name <key-name>]
        [--property <key=value> [...] ]
        [--file <dest-filename=source-filename>] [...] ]
        [--user-data <user-data>]
        [--availability-zone <zone-name>]
        [--block-device-mapping <dev-name=mapping> [...] ]
        [--nic <net-id=net-uuid,v4-fixed-ip=ip-addr,v6-fixed-ip=ip-addr,port-id=port-uuid> [...] ]
        [--hint <key=value> [...] ]
        [--config-drive <value>|True ]
        [--min <count>]
        [--max <count>]
        [--wait]
        <server-name>

.. option:: --image <image>

    Create server from this image (name or ID)

.. option:: --volume <volume>

    Create server from this volume (name or ID)

.. option:: --flavor <flavor>

    Create server with this flavor (name or ID)

.. option:: --security-group <security-group-name>

    Security group to assign to this server (name or ID)
    (repeat option to set multiple groups)

.. option:: --key-name <key-name>

    Keypair to inject into this server (optional extension)

.. option:: --property <key=value>

    Set a property on this server
    (repeat option to set multiple values)

.. option:: --file <dest-filename=source-filename>

    File to inject into image before boot
    (repeat option to set multiple files)

.. option:: --user-data <user-data>

    User data file to serve from the metadata server

.. option:: --availability-zone <zone-name>

    Select an availability zone for the server

.. option:: --block-device-mapping <dev-name=mapping>

    Map block devices; map is <id>:<type>:<size(GB)>:<delete_on_terminate> (optional extension)

.. option:: --nic <net-id=net-uuid,v4-fixed-ip=ip-addr,v6-fixed-ip=ip-addr,port-id=port-uuid>

    Create a NIC on the server. Specify option multiple times to create
    multiple NICs. Either net-id or port-id must be provided, but not both.
    net-id: attach NIC to network with this UUID,
    port-id: attach NIC to port with this UUID,
    v4-fixed-ip: IPv4 fixed address for NIC (optional),
    v6-fixed-ip: IPv6 fixed address for NIC (optional).

.. option:: --hint <key=value>

    Hints for the scheduler (optional extension)

.. option:: --config-drive <config-drive-volume>|True

    Use specified volume as the config drive, or 'True' to use an ephemeral drive

.. option:: --min <count>

    Minimum number of servers to launch (default=1)

.. option:: --max <count>

    Maximum number of servers to launch (default=1)

.. option:: --wait

    Wait for build to complete

.. describe:: <server-name>

    New server name

server delete
-------------

Delete server(s)

.. program:: server delete
.. code:: bash

    os server delete
        <server> [<server> ...] [--wait]

.. option:: --wait

    Wait for delete to complete

.. describe:: <server>

    Server(s) to delete (name or ID)

server dump create
------------------
Create a dump file in server(s)

Trigger crash dump in server(s) with features like kdump in Linux. It will
create a dump file in the server(s) dumping the server(s)' memory, and also
crash the server(s). OSC sees the dump file (server dump) as a kind of
resource.

.. program:: server dump create
.. code:: bash

    os server dump create
        <server> [<server> ...]

.. describe:: <server>

    Server(s) to create dump file (name or ID)

server list
-----------

List servers

.. code:: bash

    os server list
        [--reservation-id <reservation-id>]
        [--ip <ip-address-regex>]
        [--ip6 <ip6-address-regex>]
        [--name <name-regex>]
        [--instance-name <instance-name-regex>]
        [--status <status>]
        [--flavor <flavor>]
        [--image <image>]
        [--host <hostname>]
        [--all-projects]
        [--project <project> [--project-domain <project-domain>]]
        [--long]
        [--marker <server>]
        [--limit <limit>]

.. option:: --reservation-id <reservation-id>

    Only return instances that match the reservation

.. option:: --ip <ip-address-regex>

    Regular expression to match IP addresses

.. option:: --ip6 <ip-address-regex>

    Regular expression to match IPv6 addresses

.. option:: --name <name-regex>

    Regular expression to match names

.. option:: --instance-name <server-name-regex>

    Regular expression to match instance name (admin only)

.. option:: --status <status>

    Search by server status

.. option:: --flavor <flavor>

    Search by flavor (name or ID)

.. option:: --image <image>

    Search by image (name or ID)

.. option:: --host <hostname>

    Search by hostname

.. option:: --all-projects

    Include all projects (admin only)

.. option:: --project <project>

    Search by project (admin only) (name or ID)

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name or ID).
    This can be used in case collisions between project names exist.

.. option:: --user <user>

    Search by user (admin only) (name or ID)

.. option:: --user-domain <user-domain>

    Domain the user belongs to (name or ID).
    This can be used in case collisions between user names exist.

.. option:: --long

    List additional fields in output

.. option:: --marker <server>

    The last server (name or ID) of the previous page. Display list of servers
    after marker. Display all servers if not specified.

.. option:: --limit <limit>

    Maximum number of servers to display. If limit equals -1, all servers will
    be displayed. If limit is greater than 'osapi_max_limit' option of Nova
    API, 'osapi_max_limit' will be used instead.

server lock
-----------

Lock server(s). A non-admin user will not be able to execute actions

.. program:: server lock
.. code:: bash

    os server lock
        <server> [<server> ...]

.. describe:: <server>

    Server(s) to lock (name or ID)

server migrate
--------------

Migrate server to different host

.. program:: server migrate
.. code:: bash

    os server migrate
        --live <host>
        [--shared-migration | --block-migration]
        [--disk-overcommit | --no-disk-overcommit]
        [--wait]
        <server>

.. option:: --live <hostname>

    Target hostname

.. option:: --shared-migration

    Perform a shared live migration (default)

.. option:: --block-migration

    Perform a block live migration

.. option:: --disk-overcommit

    Allow disk over-commit on the destination host

.. option:: --no-disk-overcommit

    Do not over-commit disk on the destination host (default)

.. option:: --wait

    Wait for resize to complete

.. describe:: <server>

    Server to migrate (name or ID)

server pause
------------

Pause server(s)

.. program:: server pause
.. code:: bash

    os server pause
        <server> [<server> ...]

.. describe:: <server>

    Server(s) to pause (name or ID)

server reboot
-------------

Perform a hard or soft server reboot

.. program:: server reboot
.. code:: bash

    os server reboot
        [--hard | --soft]
        [--wait]
        <server>

.. option:: --hard

    Perform a hard reboot

.. option:: --soft

    Perform a soft reboot

.. option:: --wait

    Wait for reboot to complete

.. describe:: <server>

    Server (name or ID)

server rebuild
--------------

Rebuild server

.. program:: server rebuild
.. code:: bash

    os server rebuild
        [--image <image>]
        [--password <password>]
        [--wait]
        <server>

.. option:: --image <image>

    Recreate server from the specified image (name or ID). Defaults to the
    currently used one.

.. option:: --password <password>

    Set the password on the rebuilt instance

.. option:: --wait

    Wait for rebuild to complete

.. describe:: <server>

    Server (name or ID)

server remove fixed ip
----------------------

Remove fixed IP address from server

.. program:: server remove fixed ip
.. code:: bash

    os server remove fixed ip
        <server>
        <ip-address>

.. describe:: <server>

    Server (name or ID) to remove the fixed IP address from

.. describe:: <ip-address>

    Fixed IP address (IP address only) to remove from the server

server remove floating ip
-------------------------

Remove floating IP address from server

.. program:: server remove floating ip
.. code:: bash

    os server remove floating ip
        <server>
        <ip-address>

.. describe:: <server>

    Server (name or ID) to remove the floating IP address from

.. describe:: <ip-address>

    Floating IP address (IP address only) to remove from server

server remove security group
----------------------------

Remove security group from server

.. program:: server remove security group
.. code:: bash

    os server remove security group
        <server>
        <group>

.. describe:: <server>

    Name or ID of server to use

.. describe:: <group>

    Name or ID of security group to remove from server

server remove volume
--------------------

Remove volume from server

.. program:: server remove volume
.. code:: bash

    os server remove volume
        <server>
        <volume>

.. describe:: <server>

    Server (name or ID)

.. describe:: <volume>

    Volume to remove (name or ID)

server rescue
-------------

Put server in rescue mode

.. program:: server rescue
.. code:: bash

    os server rescue
        <server>

.. describe:: <server>

    Server (name or ID)

server resize
-------------

Scale server to a new flavor

.. program:: server resize
.. code:: bash

    os server resize
        --flavor <flavor>
        [--wait]
        <server>

    os server resize
        --confirm | --revert
        <server>

.. option:: --flavor <flavor>

    Resize server to specified flavor

.. option:: --confirm

    Confirm server resize is complete

.. option:: --revert

    Restore server state before resize

.. option:: --wait

    Wait for resize to complete

.. describe:: <server>

    Server (name or ID)

A resize operation is implemented by creating a new server and copying
the contents of the original disk into a new one.  It is also a two-step
process for the user: the first is to perform the resize, the second is
to either confirm (verify) success and release the old server, or to declare
a revert to release the new server and restart the old one.

server restore
--------------

Restore server(s) from soft-deleted state

.. program:: server restore
.. code:: bash

    os server restore
        <server> [<server> ...]

.. describe:: <server>

    Server(s) to restore (name or ID)

server resume
-------------

Resume server(s)

.. program:: server resume
.. code:: bash

    os server resume
        <server> [<server> ...]

.. describe:: <server>

    Server(s) to resume (name or ID)

server set
----------

Set server properties

.. program:: server set
.. code:: bash

    os server set
        --name <new-name>
        --property <key=value>
        [--property <key=value>] ...
        --root-password
        --state <state>
        <server>

.. option:: --name <new-name>

    New server name

.. option:: --root-password

    Set new root password (interactive only)

.. option:: --property <key=value>

    Property to add/change for this server
    (repeat option to set multiple properties)

.. option:: --state <state>

    New server state (valid value: active, error)

.. describe:: <server>

    Server (name or ID)

server shelve
-------------

Shelve server(s)

.. program:: server shelve
.. code:: bash

    os server shelve
        <server> [<server> ...]

.. describe:: <server>

    Server(s) to shelve (name or ID)

server show
-----------

Show server details

.. program:: server show
.. code:: bash

    os server show
        [--diagnostics]
        <server>

.. option:: --diagnostics

    Display server diagnostics information

.. describe:: <server>

    Server (name or ID)

server ssh
----------

SSH to server

.. program:: server ssh
.. code:: bash

    os server ssh
        [--login <login-name>]
        [--port <port>]
        [--identity <keyfile>]
        [--option <config-options>]
        [--public | --private | --address-type <address-type>]
        <server>

.. option:: --login <login-name>

    Login name (ssh -l option)

.. option:: --port <port>

    Destination port (ssh -p option)

.. option:: --identity <keyfile>

    Private key file (ssh -i option)

.. option:: --option <config-options>

    Options in ssh_config(5) format (ssh -o option)

.. option:: --public

    Use public IP address

.. option:: --private

    Use private IP address

.. option:: --address-type <address-type>

    Use other IP address (public, private, etc)

.. describe:: <server>

    Server (name or ID)

server start
------------

Start server(s)

.. program:: server start
.. code:: bash

    os server start
        <server> [<server> ...]

.. describe:: <server>

    Server(s) to start (name or ID)

server stop
-----------

Stop server(s)

.. program:: server stop
.. code:: bash

    os server stop
        <server> [<server> ...]

.. describe:: <server>

    Server(s) to stop (name or ID)

server suspend
--------------

Suspend server(s)

.. program:: server suspend
.. code:: bash

    os server suspend
        <server> [<server> ...]

.. describe:: <server>

    Server(s) to suspend (name or ID)

server unlock
-------------

Unlock server(s)

.. program:: server unlock
.. code:: bash

    os server unlock
        <server> [<server> ...]

.. describe:: <server>

    Server(s) to unlock (name or ID)

server unpause
--------------

Unpause server(s)

.. program:: server unpause
.. code:: bash

    os server unpause
        <server> [<server> ...]

.. describe:: <server>

   Server(s) to unpause (name or ID)

server unrescue
---------------

Restore server from rescue mode

.. program:: server unrescue
.. code:: bash

    os server unrescue
        <server>

.. describe:: <server>

    Server (name or ID)

server unset
------------

Unset server properties

.. program:: server unset
.. code:: bash

    os server unset
        --property <key>
        [--property <key>] ...
        <server>

.. option:: --property <key>

    Property key to remove from server
    (repeat option to remove multiple values)

.. describe:: <server>

    Server (name or ID)

server unshelve
---------------

Unshelve server(s)

.. program:: server unshelve
.. code:: bash

    os server unshelve
        <server> [<server> ...]

.. describe:: <server>

    Server(s) to unshelve (name or ID)
