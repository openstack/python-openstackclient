======
subnet
======

A **subnet** is a block of IP addresses and associated configuration state.
Subnets are used to allocate IP addresses when new ports are created on a
network.

Network v2

subnet create
-------------

Create new subnet

.. program:: subnet create
.. code:: bash

    os subnet create
        [--project <project> [--project-domain <project-domain>]]
        [--subnet-pool <subnet-pool> | --use-default-subnet-pool [--prefix-length <prefix-length>]]
        [--subnet-range <subnet-range>]
        [--allocation-pool start=<ip-address>,end=<ip-address>]
        [--dhcp | --no-dhcp]
        [--dns-nameserver <dns-nameserver>]
        [--gateway <gateway>]
        [--host-route destination=<subnet>,gateway=<ip-address>]
        [--ip-version {4,6}]
        [--description <description>]
        [--ipv6-ra-mode {dhcpv6-stateful,dhcpv6-stateless,slaac}]
        [--ipv6-address-mode {dhcpv6-stateful,dhcpv6-stateless,slaac}]
        [--network-segment <network-segment>]
        [--service-type <service-type>]
        --network <network>
        <name>

.. option:: --project <project>

    Owner's project (name or ID)

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name or ID).
    This can be used in case collisions between project names exist.

.. option:: --subnet-pool <subnet-pool>

    Subnet pool from which this subnet will obtain a CIDR (name or ID)

.. option:: --use-default-subnet-pool

    Use default subnet pool for ``--ip-version``

.. option:: --prefix-length <prefix-length>

    Prefix length for subnet allocation from subnet pool

.. option:: --subnet-range <subnet-range>

    Subnet range in CIDR notation
    (required if ``--subnet-pool`` is not specified, optional otherwise)

.. option:: --allocation-pool start=<ip-address>,end=<ip-address>

    Allocation pool IP addresses for this subnet e.g.:
    ``start=192.168.199.2,end=192.168.199.254``
    (repeat option to add multiple IP addresses)

.. option:: --dhcp

     Enable DHCP (default)

.. option:: --no-dhcp

     Disable DHCP

.. option:: --dns-nameserver <dns-nameserver>

     DNS server for this subnet (repeat option to set multiple DNS servers)

.. option:: --gateway <gateway>

     Specify a gateway for the subnet.  The three options are:
     <ip-address>: Specific IP address to use as the gateway,
     'auto': Gateway address should automatically be chosen from
     within the subnet itself, 'none': This subnet will not use
     a gateway, e.g.: ``--gateway 192.168.9.1``, ``--gateway auto``,
     ``--gateway none`` (default is 'auto').

.. option:: --host-route destination=<subnet>,gateway=<ip-address>

     Additional route for this subnet e.g.:
     ``destination=10.10.0.0/16,gateway=192.168.71.254``
     destination: destination subnet (in CIDR notation)
     gateway: nexthop IP address
     (repeat option to add multiple routes)

.. option:: --ip-version {4,6}

     IP version (default is 4).  Note that when subnet pool is specified,
     IP version is determined from the subnet pool and this option
     is ignored.

.. option:: --description <description>

     Set subnet description

.. option:: --ipv6-ra-mode {dhcpv6-stateful,dhcpv6-stateless,slaac}

     IPv6 RA (Router Advertisement) mode,
     valid modes: [dhcpv6-stateful, dhcpv6-stateless, slaac]

.. option:: --ipv6-address-mode {dhcpv6-stateful,dhcpv6-stateless,slaac}

     IPv6 address mode, valid modes: [dhcpv6-stateful, dhcpv6-stateless, slaac]

.. option:: --network-segment <network-segment>

     Network segment to associate with this subnet (name or ID)

.. option:: --service-type <service-type>

     Service type for this subnet e.g.:
     ``network:floatingip_agent_gateway``.
     Must be a valid device owner value for a network port
     (repeat option to set multiple service types)

.. option:: --network <network>

     Network this subnet belongs to (name or ID)

.. _subnet_create-name:
.. describe:: <name>

     Name of subnet to create

subnet delete
-------------

Delete subnet(s)

.. program:: subnet delete
.. code:: bash

    os subnet delete
        <subnet> [<subnet> ...]

.. _subnet_delete-subnet:
.. describe:: <subnet>

    Subnet(s) to delete (name or ID)

subnet list
-----------

List subnets

.. program:: subnet list
.. code:: bash

    os subnet list
        [--long]
        [--ip-version {4,6}]
        [--dhcp | --no-dhcp]
        [--project <project> [--project-domain <project-domain>]]
        [--network <network>]
        [--gateway <gateway>]
        [--name <name>]
        [--subnet-range <subnet-range>]

.. option:: --long

    List additional fields in output

.. option:: --ip-version {4, 6}

    List only subnets of given IP version in output.
    Allowed values for IP version are 4 and 6.

.. option:: --dhcp

    List subnets which have DHCP enabled

.. option:: --no-dhcp

    List subnets which have DHCP disabled

.. option:: --service-type <service-type>

    List only subnets of a given service type in output
    e.g.: ``network:floatingip_agent_gateway``.
    Must be a valid device owner value for a network port
    (repeat option to list multiple service types)

.. option:: --project <project>

    List only subnets which belong to a given project (name or ID) in output

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name or ID).
    This can be used in case collisions between project names exist.

.. option:: --network <network>

    List only subnets which belong to a given network (name or ID) in output

.. option:: --gateway <gateway>

    List only subnets of given gateway IP in output

.. option:: --name <name>

    List only subnets of given name in output

.. option:: --subnet-range <subnet-range>

    List only subnets of given subnet range (in CIDR notation) in output
    e.g.: ``--subnet-range 10.10.0.0/16``

subnet set
----------

Set subnet properties

.. program:: subnet set
.. code:: bash

    os subnet set
        [--allocation-pool start=<ip-address>,end=<ip-address>]
        [--no-allocation-pool]
        [--dhcp | --no-dhcp]
        [--dns-nameserver <dns-nameserver>]
        [--gateway <gateway-ip>]
        [--host-route destination=<subnet>,gateway=<ip-address>]
        [--no-host-route]
        [--service-type <service-type>]
        [--name <new-name>]
        [--description <description>]
        <subnet>

.. option:: --allocation-pool start=<ip-address>,end=<ip-address>

    Allocation pool IP addresses for this subnet e.g.:
    ``start=192.168.199.2,end=192.168.199.254``
    (repeat option to add multiple IP addresses)

.. option:: --no-allocation-pool

     Clear associated allocation pools from this subnet.
     Specify both --allocation-pool and --no-allocation-pool
     to overwrite the current allocation pool information.

.. option:: --dhcp

     Enable DHCP

.. option:: --no-dhcp

     Disable DHCP

.. option:: --dns-nameserver <dns-nameserver>

     DNS server for this subnet (repeat option to set multiple DNS servers)

.. option:: --gateway <gateway>

     Specify a gateway for the subnet. The options are:
     <ip-address>: Specific IP address to use as the gateway,
     'none': This subnet will not use a gateway,
     e.g.: ``--gateway 192.168.9.1``, ``--gateway none``.

.. option:: --host-route destination=<subnet>,gateway=<ip-address>

     Additional route for this subnet e.g.:
     ``destination=10.10.0.0/16,gateway=192.168.71.254``
     destination: destination subnet (in CIDR notation)
     gateway: nexthop IP address

.. option:: --no-host-route

     Clear associated host routes from this subnet.
     Specify both --host-route and --no-host-route
     to overwrite the current host route information.

.. option:: --service-type <service-type>

     Service type for this subnet e.g.:
     ``network:floatingip_agent_gateway``.
     Must be a valid device owner value for a network port
     (repeat option to set multiple service types)
.. option:: --description <description>

     Set subnet description

.. option:: --name

     Updated name of the subnet

.. _subnet_set-subnet:
.. describe:: <subnet>

    Subnet to modify (name or ID)


subnet show
-----------

Display subnet details

.. program:: subnet show
.. code:: bash

    os subnet show
        <subnet>

.. _subnet_show-subnet:
.. describe:: <subnet>

    Subnet to display (name or ID)

subnet unset
------------

Unset subnet properties

.. program:: subnet unset
.. code:: bash

    os subnet unset
        [--allocation-pool start=<ip-address>,end=<ip-address> [...]]
        [--dns-nameserver <dns-nameserver> [...]]
        [--host-route destination=<subnet>,gateway=<ip-address> [...]]
        [--service-type <service-type>]
        <subnet>

.. option:: --dns-nameserver <dns-nameserver>

     DNS server to be removed from this subnet
     (repeat option to unset multiple DNS servers)

.. option:: --allocation-pool start=<ip-address>,end=<ip-address>

    Allocation pool IP addresses to be removed from this
    subnet e.g.: ``start=192.168.199.2,end=192.168.199.254``
    (repeat option to unset multiple allocation pools)

.. option:: --host-route destination=<subnet>,gateway=<ip-address>

     Route to be removed from this subnet e.g.:
     ``destination=10.10.0.0/16,gateway=192.168.71.254``
     destination: destination subnet (in CIDR notation)
     gateway: nexthop IP address
     (repeat option to unset multiple host routes)

.. option:: --service-type <service-type>

     Service type to be removed from this subnet e.g.:
     ``network:floatingip_agent_gateway``.
     Must be a valid device owner value for a network port
     (repeat option to unset multiple service types)

.. _subnet_unset-subnet:
.. describe:: <subnet>

    Subnet to modify (name or ID)
