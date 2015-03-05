======
server
======

Compute v2

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
        [--security-group <security-group-list> [...] ]
        [--key-name <key-name>]
        [--property <key=value> [...] ]
        [--file <dest-filename=source-filename>] [...] ]
        [--user-data <user-data>]
        [--availability-zone <zone-name>]
        [--block-device-mapping <dev-name=mapping> [...] ]
        [--nic <net-id=net-uuid,v4-fixed-ip=ip-addr> [...] ]
        [--hint <key=value> [...] ]
        [--config-drive <value>|True ]
        [--min <count>]
        [--max <count>]
        [--wait]
        <server-name>

.. option:: --image <image>

    Create server from this image

.. option:: --volume <volume>

    Create server from this volume

.. option:: --flavor <flavor>

    Create server with this flavor

.. option:: --security-group <security-group-name>

    Security group to assign to this server (repeat for multiple groups)

.. option:: --key-name <key-name>

    Keypair to inject into this server (optional extension)

.. option:: --property <key=value>

    Set a property on this server (repeat for multiple values)

.. option:: --file <dest-filename=source-filename>

    File to inject into image before boot (repeat for multiple files)

.. option:: --user-data <user-data>

    User data file to serve from the metadata server

.. option:: --availability-zone <zone-name>

    Select an availability zone for the server

.. option:: --block-device-mapping <dev-name=mapping>

    Map block devices; map is <id>:<type>:<size(GB)>:<delete_on_terminate> (optional extension)

.. option:: --nic <nic-config-string>

    Specify NIC configuration (optional extension)

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
        <server> [<server> ...]

.. describe:: <server>

    Server to delete (name or ID)

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
        [--long]

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

    Search by flavor ID

.. option:: --image <image>

    Search by image ID

.. option:: --host <hostname>

    Search by hostname

.. option:: --all-projects

    Include all projects (admin only)

.. option:: --long

    List additional fields in output

server lock
-----------

Lock a server. A non-admin user will not be able to execute actions

.. program:: server lock
.. code:: bash

    os server lock
        <server>

.. describe:: <server>

    Server (name or ID)

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

Pause server

.. program:: server pause
.. code:: bash

    os server pause
        <server>

.. describe:: <server>

    Server (name or ID)

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
        --image <image>
        [--password <password>]
        [--wait]
        <server>

.. option:: --image <image>

    Recreate server from this image

.. option:: --password <password>

    Set the password on the rebuilt instance

.. option:: --wait

    Wait for rebuild to complete

.. describe:: <server>

    Server (name or ID)

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

.. program:: server rescure
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

server resume
-------------

Resume server

.. program:: server resume
.. code:: bash

    os server resume
        <server>

.. describe:: <server>

    Server (name or ID)

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
        <server>

.. option:: --name <new-name>

    New server name

.. option:: --root-password

    Set new root password (interactive only)

.. option:: --property <key=value>

    Property to add/change for this server (repeat option to set
    multiple properties)

.. describe:: <server>

    Server (name or ID)

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

Ssh to server

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

server suspend
--------------

Suspend server

.. program:: server suspend
.. code:: bash

    os server suspend
        <server>

.. describe:: <server>

    Server (name or ID)

server unlock
-------------

Unlock server

.. program:: server unlock
.. code:: bash

    os server unlock
        <server>

.. describe:: <server>

    Server (name or ID)

server unpause
--------------

Unpause server

.. program:: server unpause
.. code:: bash

    os server unpause
        <server>

.. describe:: <server>

    Server (name or ID)

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

    Property key to remove from server (repeat to set multiple values)

.. describe:: <server>

    Server (name or ID)
