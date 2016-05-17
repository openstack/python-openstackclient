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
        [--ipv6-ra-mode {dhcpv6-stateful,dhcpv6-stateless,slaac}]
        [--ipv6-address-mode {dhcpv6-stateful,dhcpv6-stateless,slaac}]
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
     ``--gateway none`` (default is 'auto')

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

.. option:: --ipv6-ra-mode {dhcpv6-stateful,dhcpv6-stateless,slaac}

     IPv6 RA (Router Advertisement) mode,
     valid modes: [dhcpv6-stateful, dhcpv6-stateless, slaac]

.. option:: --ipv6-address-mode {dhcpv6-stateful,dhcpv6-stateless,slaac}

     IPv6 address mode, valid modes: [dhcpv6-stateful, dhcpv6-stateless, slaac]

.. option:: --network <network>

     Network this subnet belongs to (name or ID)

.. _subnet_create-name:
.. describe:: <name>

     Name of subnet to create

subnet delete
-------------

Delete a subnet

.. program:: subnet delete
.. code:: bash

    os subnet delete
        <subnet>

.. _subnet_delete-subnet:
.. describe:: <subnet>

    Subnet to delete (name or ID)

subnet list
-----------

List subnets

.. program:: subnet list
.. code:: bash

    os subnet list
        [--long]

.. option:: --long

    List additional fields in output

.. option:: --ip-version {4, 6}

    List only subnets of given IP version in output

subnet set
----------

Set subnet properties

.. program:: subnet set
.. code:: bash

    os subnet set
        [--allocation-pool start=<ip-address>,end=<ip-address>]
        [--dhcp | --no-dhcp]
        [--dns-nameserver <dns-nameserver>]
        [--gateway <gateway-ip>]
        [--host-route destination=<subnet>,gateway=<ip-address>]
        [--name <new-name>]
        <subnet>

.. option:: --allocation-pool start=<ip-address>,end=<ip-address>

    Allocation pool IP addresses for this subnet e.g.:
    ``start=192.168.199.2,end=192.168.199.254``
    (repeat option to add multiple IP addresses)

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
     e.g.: ``--gateway 192.168.9.1``, ``--gateway none``

.. option:: --host-route destination=<subnet>,gateway=<ip-address>

     Additional route for this subnet e.g.:
     ``destination=10.10.0.0/16,gateway=192.168.71.254``
     destination: destination subnet (in CIDR notation)
     gateway: nexthop IP address
     (repeat option to add multiple routes)

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
