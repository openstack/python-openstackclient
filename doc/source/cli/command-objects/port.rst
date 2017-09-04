====
port
====

A **port** is a connection point for attaching a single device, such as the
NIC of a server, to a network. The port also describes the associated network
configuration, such as the MAC and IP addresses to be used on that port.

Network v2

port create
-----------

Create new port

.. program:: port create
.. code:: bash

    openstack port create
        --network <network>
        [--description <description>]
        [--fixed-ip subnet=<subnet>,ip-address=<ip-address>]
        [--device <device-id>]
        [--device-owner <device-owner>]
        [--vnic-type <vnic-type>]
        [--binding-profile <binding-profile>]
        [--host <host-id>]
        [--enable | --disable]
        [--mac-address <mac-address>]
        [--security-group <security-group> | --no-security-group]
        [--dns-domain <dns-domain>]
        [--dns-name <dns-name>]
        [--allowed-address ip-address=<ip-address>[,mac-address=<mac-address>]]
        [--qos-policy <qos-policy>]
        [--project <project> [--project-domain <project-domain>]]
        [--enable-port-security | --disable-port-security]
        [--tag <tag> | --no-tag]
        <name>

.. option:: --network <network>

    Network this port belongs to (name or ID)

.. option:: --description <description>

    Description of this port

.. option:: --fixed-ip subnet=<subnet>,ip-address=<ip-address>

    Desired IP and/or subnet for this port (name or ID):
    subnet=<subnet>,ip-address=<ip-address>
    (repeat option to set multiple fixed IP addresses)

.. option:: --device <device-id>

    Port device ID

.. option:: --device-owner <device-owner>

    Device owner of this port. This is the entity that uses
    the port (for example, network:dhcp).

.. option:: --vnic-type <vnic-type>

    VNIC type for this port (direct | direct-physical | macvtap | normal | baremetal |
    virtio-forwarder, default: normal)

.. option:: --binding-profile <binding-profile>

    Custom data to be passed as binding:profile. Data may
    be passed as <key>=<value> or JSON.
    (repeat option to set multiple binding:profile data)

.. option:: --host <host-id>

    Allocate port on host ``<host-id>`` (ID only)

.. option:: --enable

    Enable port (default)

.. option:: --disable

    Disable port

.. option:: --mac-address <mac-address>

    MAC address of this port

.. option:: --security-group <security-group>

    Security group to associate with this port (name or ID)
    (repeat option to set multiple security groups)

.. option::  --no-security-group

    Associate no security groups with this port

.. option:: --dns-domain <dns-name>

    Set DNS domain for this port
    (requires dns_domain for ports extension)

.. option:: --dns-name <dns-name>

    Set DNS name for this port
    (requires DNS integration extension)

.. option:: --allowed-address ip-address=<ip-address>[,mac-address=<mac-address>]

    Add allowed-address pair associated with this port:
    ip-address=<ip-address>[,mac-address=<mac-address>]
    (repeat option to set multiple allowed-address pairs)

.. option:: --qos-policy <qos-policy>

    Attach QoS policy to this port (name or ID)

.. option:: --project <project>

    Owner's project (name or ID)

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name or ID).
    This can be used in case collisions between project names exist.

.. option::  --enable-port-security

    Enable port security for this port (Default)

.. option::  --disable-port-security

    Disable port security for this port

.. option:: --tag <tag>

    Tag to be added to the port (repeat option to set multiple tags)

.. option:: --no-tag

    No tags associated with the port

.. _port_create-name:
.. describe:: <name>

    Name of this port

port delete
-----------

Delete port(s)

.. program:: port delete
.. code:: bash

    openstack port delete
        <port> [<port> ...]

.. _port_delete-port:
.. describe:: <port>

    Port(s) to delete (name or ID)

port list
---------

List ports

.. program:: port list
.. code:: bash

    openstack port list
        [--device-owner <device-owner>]
        [--router <router> | --server <server>]
        [--network <network>]
        [--mac-address <mac-address>]
        [--fixed-ip subnet=<subnet>,ip-address=<ip-address>]
        [--long]
        [--project <project> [--project-domain <project-domain>]]
        [--tags <tag>[,<tag>,...]] [--any-tags <tag>[,<tag>,...]]
        [--not-tags <tag>[,<tag>,...]] [--not-any-tags <tag>[,<tag>,...]]

.. option:: --device-owner <device-owner>

    List only ports with the specified device owner. This is
    the entity that uses the port (for example, network:dhcp).

.. option:: --router <router>

    List only ports attached to this router (name or ID)

.. option:: --server <server>

    List only ports attached to this server (name or ID)

.. option:: --network <network>

    List only ports attached to this network (name or ID)

.. option:: --mac-address <mac-address>

    List only ports with this MAC address

.. option:: --fixed-ip subnet=<subnet>,ip-address=<ip-address>

    Desired IP and/or subnet for filtering ports (name or ID):
    subnet=<subnet>,ip-address=<ip-address>
    (repeat option to set multiple fixed IP addresses)

.. option:: --long

    List additional fields in output

.. option:: --project <project>

    List ports according to their project (name or ID)

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name or ID).
    This can be used in case collisions between project names exist.

.. option:: --tags <tag>[,<tag>,...]

    List ports which have all given tag(s)

.. option:: --any-tags <tag>[,<tag>,...]

    List ports which have any given tag(s)

.. option:: --not-tags <tag>[,<tag>,...]

    Exclude ports which have all given tag(s)

.. option:: --not-any-tags <tag>[,<tag>,...]

    Exclude ports which have any given tag(s)

port set
--------

Set port properties

.. program:: port set
.. code:: bash

    openstack port set
        [--description <description>]
        [--fixed-ip subnet=<subnet>,ip-address=<ip-address>]
        [--no-fixed-ip]
        [--device <device-id>]
        [--device-owner <device-owner>]
        [--vnic-type <vnic-type>]
        [--binding-profile <binding-profile>]
        [--no-binding-profile]
        [--host <host-id>]
        [--qos-policy <qos-policy>]
        [--enable | --disable]
        [--name <name>]
        [--mac-address <mac-address>]
        [--security-group <security-group>]
        [--no-security-group]
        [--enable-port-security | --disable-port-security]
        [--dns-domain <dns-domain>]
        [--dns-name <dns-name>]
        [--allowed-address ip-address=<ip-address>[,mac-address=<mac-address>]]
        [--no-allowed-address]
        [--data-plane-status <status>]
        [--tag <tag>] [--no-tag]
        <port>

.. option:: --description <description>

    Description of this port

.. option:: --fixed-ip subnet=<subnet>,ip-address=<ip-address>

    Desired IP and/or subnet for this port (name or ID):
    subnet=<subnet>,ip-address=<ip-address>
    (repeat option to set multiple fixed IP addresses)

.. option:: --no-fixed-ip

    Clear existing information of fixed IP addresses.
    Specify both :option:`--fixed-ip` and :option:`--no-fixed-ip`
    to overwrite the current fixed IP addresses.

.. option:: --device <device-id>

    Port device ID

.. option:: --device-owner <device-owner>

    Device owner of this port. This is the entity that uses
    the port (for example, network:dhcp).

.. option:: --vnic-type <vnic-type>

    VNIC type for this port (direct | direct-physical | macvtap | normal | baremetal |
    virtio-forwarder, default: normal)

.. option:: --binding-profile <binding-profile>

    Custom data to be passed as binding:profile. Data may
    be passed as <key>=<value> or JSON.
    (repeat option to set multiple binding:profile data)

.. option:: --no-binding-profile

    Clear existing information of binding:profile.
    Specify both :option:`--binding-profile` and :option:`--no-binding-profile`
    to overwrite the current binding:profile information.

.. option:: --host <host-id>

    Allocate port on host ``<host-id>`` (ID only)

.. option:: --qos-policy <qos-policy>

    Attach QoS policy to this port (name or ID)

.. option:: --enable

    Enable port

.. option:: --disable

    Disable port

.. option:: --name

    Set port name

.. option:: --mac-address

    Set port's MAC address (admin only)

.. option:: --security-group <security-group>

    Security group to associate with this port (name or ID)
    (repeat option to set multiple security groups)

.. option::  --no-security-group

    Clear existing security groups associated with this port

.. option::  --enable-port-security

    Enable port security for this port

.. option::  --disable-port-security

    Disable port security for this port

.. option:: --dns-domain <dns-domain>

    Set DNS domain for this port
    (requires dns_domain for ports extension)

.. option:: --dns-name <dns-name>

    Set DNS name for this port
    (requires DNS integration extension)

.. option:: --allowed-address ip-address=<ip-address>[,mac-address=<mac-address>]

    Add allowed-address pair associated with this port:
    ip-address=<ip-address>[,mac-address=<mac-address>]
    (repeat option to set multiple allowed-address pairs)

.. option:: --no-allowed-address

    Clear existing allowed-address pairs associated
    with this port.
    (Specify both --allowed-address and --no-allowed-address
    to overwrite the current allowed-address pairs)

.. option:: --data-plane-status

    Set data plane status of this port (ACTIVE | DOWN).
    Unset it to None with the 'port unset' command
    (requires data plane status extension)

.. option:: --tag <tag>

    Tag to be added to the port (repeat option to set multiple tags)

.. option:: --no-tag

    Clear tags associated with the port. Specify both --tag
    and --no-tag to overwrite current tags

.. _port_set-port:
.. describe:: <port>

    Port to modify (name or ID)

port show
---------

Display port details

.. program:: port show
.. code:: bash

    openstack port show
        <port>

.. _port_show-port:
.. describe:: <port>

    Port to display (name or ID)

port unset
----------

Unset port properties

.. program:: port unset
.. code:: bash

    openstack port unset
        [--fixed-ip subnet=<subnet>,ip-address=<ip-address> [...]]
        [--binding-profile <binding-profile-key> [...]]
        [--security-group <security-group> [...]]
        [--allowed-address ip-address=<ip-address>[,mac-address=<mac-address>] [...]]
        [--qos-policy]
        [--data-plane-status]
        [--tag <tag> | --all-tag]
        <port>

.. option:: --fixed-ip subnet=<subnet>,ip-address=<ip-address>

    Desired IP and/or subnet which should be removed
    from this port (name or ID): subnet=<subnet>,ip-address=<ip-address>
    (repeat option to unset multiple fixed IP addresses)

.. option:: --binding-profile <binding-profile-key>

    Desired key which should be removed from binding-profile
    (repeat option to unset multiple binding:profile data)

.. option:: --security-group <security-group>

    Security group which should be removed from this port (name or ID)
    (repeat option to unset multiple security groups)

.. option:: --allowed-address ip-address=<ip-address>[,mac-address=<mac-address>]

    Desired allowed-address pair which should be removed from this port:
    ip-address=<ip-address>[,mac-address=<mac-address>]
    (repeat option to unset multiple allowed-address pairs)

.. option:: --qos-policy

    Remove the QoS policy attached to the port

.. option:: --data-plane-status

    Clear existing information of data plane status

.. option:: --tag <tag>

    Tag to be removed from the port
    (repeat option to remove multiple tags)

.. option:: --all-tag

    Clear all tags associated with the port

.. _port_unset-port:
.. describe:: <port>

    Port to modify (name or ID)
