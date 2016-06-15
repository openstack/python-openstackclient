===================
security group rule
===================

A **security group rule** specifies the network access rules for servers
and other resources on the network.

Compute v2, Network v2

security group rule create
--------------------------

Create a new security group rule

.. program:: security group rule create
.. code:: bash

    os security group rule create
        [--src-ip <ip-address> | --src-group <group>]
        [--dst-port <port-range> | [--icmp-type <icmp-type> [--icmp-code <icmp-code>]]]
        [--protocol <protocol>]
        [--ingress | --egress]
        [--ethertype <ethertype>]
        [--project <project> [--project-domain <project-domain>]]
        <group>

.. option:: --src-ip <ip-address>

    Source IP address block
    (may use CIDR notation; default for IPv4 rule: 0.0.0.0/0)

.. option:: --src-group <group>

    Source security group (name or ID)

.. option:: --dst-port <port-range>

    Destination port, may be a single port or a starting and
    ending port range: 137:139. Required for IP protocols TCP
    and UDP. Ignored for ICMP IP protocols.

.. option:: --icmp-type <icmp-type>

    ICMP type for ICMP IP protocols

    *Network version 2 only*

.. option:: --icmp-code <icmp-code>

    ICMP code for ICMP IP protocols

    *Network version 2 only*

.. option:: --protocol <protocol>

    IP protocol (icmp, tcp, udp; default: tcp)

    *Compute version 2*

    IP protocol (ah, dccp, egp, esp, gre, icmp, igmp,
    ipv6-encap, ipv6-frag, ipv6-icmp, ipv6-nonxt,
    ipv6-opts, ipv6-route, ospf, pgm, rsvp, sctp, tcp,
    udp, udplite, vrrp and integer representations [0-255];
    default: tcp)

    *Network version 2*

.. option:: --ingress

    Rule applies to incoming network traffic (default)

    *Network version 2 only*

.. option:: --egress

    Rule applies to outgoing network traffic

    *Network version 2 only*

.. option:: --ethertype <ethertype>

    Ethertype of network traffic
    (IPv4, IPv6; default: based on IP protocol)

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

Delete security group rule(s)

.. program:: security group rule delete
.. code:: bash

    os security group rule delete
        <rule> [<rule> ...]

.. describe:: <rule>

    Security group rule(s) to delete (ID only)

security group rule list
------------------------

List security group rules

.. program:: security group rule list
.. code:: bash

    os security group rule list
        [--all-projects]
        [--long]
        [<group>]

.. option:: --all-projects

    Display information from all projects (admin only)

    *Network version 2 ignores this option and will always display information*
    *for all projects (admin only).*

.. option:: --long

    List additional fields in output

    *Compute version 2 does not have additional fields to display.*

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
