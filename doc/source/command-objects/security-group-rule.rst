===================
security group rule
===================

Compute v2

security group rule create
--------------------------

Create a new security group rule

.. program:: security group rule create
.. code:: bash

    os security group rule create
        [--proto <proto>]
        [--src-ip <ip-address>]
        [--dst-port <port-range>]
        <group>

.. option:: --proto <proto>

    IP protocol (icmp, tcp, udp; default: tcp)

.. option:: --src-ip <ip-address>

    Source IP (may use CIDR notation; default: 0.0.0.0/0)

.. option:: --dst-port <port-range>

    Destination port, may be a range: 137:139 (default: 0; only required for proto tcp and udp)

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
        <group>

.. describe:: <group>

    List all rules in this security group (name or ID)
