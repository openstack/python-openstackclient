====
port
====

Network v2

port create
-----------

Create new port

.. program:: port create
.. code:: bash

    os port create
        --network <network>
        [--fixed-ip subnet=<subnet>,ip-address=<ip-address>]
        [--device-id <device-id>]
        [--device-owner <device-owner>]
        [--vnic-type <vnic-type>]
        [--binding-profile <binding-profile>]
        [--host-id <host-id>]
        [--enable | --disable]
        [--mac-address <mac-address>]
        [--project <project> [--project-domain <project-domain>]]
        <name>

.. option:: --network <network>

    Network this port belongs to (name or ID)

.. option:: --fixed-ip subnet=<subnet>,ip-address=<ip-address>

    Desired IP and/or subnet (name or ID) for this port:
    subnet=<subnet>,ip-address=<ip-address>
    (this option can be repeated)

.. option:: --device-id <device-id>

    Device ID of this port

.. option:: --device-owner <device-owner>

    Device owner of this port

.. option:: --vnic-type <vnic-type>

    VNIC type for this port (direct | direct-physical | macvtap | normal | baremetal).
    If unspecified during port creation, default value will be 'normal'.

.. option:: --binding-profile <binding-profile>

    Custom data to be passed as binding:profile: <key>=<value>
    (this option can be repeated)

.. option:: --host-id <host-id>

    The ID of the host where the port is allocated

.. option:: --enable

    Enable port (default)

.. option:: --disable

    Disable port

.. option:: --mac-address <mac-address>

    MAC address of this port

.. option:: --project <project>

    Owner's project (name or ID)

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name or ID).
    This can be used in case collisions between project names exist.

.. _port_create-name:
.. describe:: <name>

    Name of this port

port delete
-----------

Delete port(s)

.. program:: port delete
.. code:: bash

    os port delete
        <port> [<port> ...]

.. _port_delete-port:
.. describe:: <port>

    Port(s) to delete (name or ID)

port list
---------

List ports

.. program:: port list
.. code:: bash

    os port list

port set
--------

Set port properties

.. program:: port set
.. code:: bash

    os port set
        [--fixed-ip subnet=<subnet>,ip-address=<ip-address>]
        [--device-id <device-id>]
        [--device-owner <device-owner>]
        [--vnic-type <vnic-type>]
        [--binding-profile <binding-profile>]
        [--host-id <host-id>]
        [--enable | --disable]
        <port>

.. option:: --fixed-ip subnet=<subnet>,ip-address=<ip-address>

    Desired IP and/or subnet for this port:
    subnet=<subnet>,ip-address=<ip-address>
    (you can repeat this option)

.. option:: --device-id <device-id>

    Device ID of this port

.. option:: --device-owner <device-owner>

    Device owner of this port

.. option:: --vnic-type <vnic-type>

    VNIC type for this port (direct | direct-physical | macvtap | normal | baremetal).
    If unspecified during port creation, default value will be 'normal'.

.. option:: --binding-profile <binding-profile>

    Custom data to be passed as binding:profile: <key>=<value>
    (this option can be repeated)

.. option:: --host-id <host-id>

    The ID of the host where the port is allocated

.. option:: --enable

    Enable port

.. option:: --disable

    Disable port

.. _port_set-port:
.. describe:: <port>

    Port to modify (name or ID)

port show
---------

Display port details

.. program:: port show
.. code:: bash

    os port show
        <port>

.. _port_show-port:
.. describe:: <port>

    Port to display (name or ID)
