===================
security group rule
===================

Compute v2, Network v2

security group rule create
--------------------------

Create a new security group rule

.. program:: security group rule create
.. code:: bash

    os security group rule create
        [--proto <proto>]
        [--src-ip <ip-address> | --src-group <group>]
        [--dst-port <port-range>]
        [--ingress | --egress]
        [--ethertype <ethertype>]
        [--project <project> [--project-domain <project-domain>]]
        <group>

.. option:: --proto <proto>

    IP protocol (icmp, tcp, udp; default: tcp)

.. option:: --src-ip <ip-address>

    Source IP address block
    (may use CIDR notation; default for IPv4 rule: 0.0.0.0/0)

.. option:: --src-group <group>

    Source security group (name or ID)

.. option:: --dst-port <port-range>

    Destination port, may be a single port or port range: 137:139
    (only required for IP protocols tcp and udp)

.. option:: --ingress

    Rule applies to incoming network traffic (default)

    *Network version 2 only*

.. option:: --egress

    Rule applies to outgoing network traffic

    *Network version 2 only*

.. option:: --ethertype <ethertype>

    Ethertype of network traffic (IPv4, IPv6; default: IPv4)

    *Network version 2 only*

.. option:: --project <project>

    Owner's project (name or ID)

    *Network version 2 only*

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name or ID).
    This can be used in case collisions between project names exist.

    *Network version 2 only*

.. describe:: <group>

    Create rule in this security group (name or ID)

security group rule delete
--------------------------

Delete a security group rule

.. program:: security group rule delete
.. code:: bash

    os security group rule delete
        <rule>

.. describe:: <rule>

    Security group rule to delete (ID only)

security group rule list
------------------------

List security group rules

.. program:: security group rule list
.. code:: bash

    os security group rule list
        [<group>]

.. describe:: <group>

    List all rules in this security group (name or ID)

security group rule show
------------------------

Display security group rule details

.. program:: security group rule show
.. code:: bash

    os security group rule show
        <rule>

.. describe:: <rule>

    Security group rule to display (ID only)
