===========================
floating ip port forwarding
===========================

Network v2

floating ip port forwarding create
----------------------------------

Create floating IP Port Forwarding

.. program:: floating ip port forwarding create
.. code:: bash

    openstack floating ip port forwarding create
        --internal-ip-address <internal-ip-address>
        --port <port>
        --internal-protocol-port <port-number>
        --external-protocol-port <port-number>
        --protocol <protocol>
        <floating-ip>


.. describe:: --internal-ip-address <internal-ip-address>

    The fixed IPv4 address of the network port associated
    to the floating IP port forwarding

.. describe:: --port <port>

    The name or ID of the network port associated to the
    floating IP port forwarding

.. describe:: --internal-protocol-port <port-number>

    The protocol port number of the network port fixed
    IPv4 address associated to the floating IP port
    forwarding

.. describe:: --external-protocol-port <port-number>

    The protocol port number of the port forwarding's
    floating IP address

.. describe:: --protocol <protocol>

    The protocol used in the floating IP port forwarding,
    for instance: TCP, UDP

.. describe:: <floating-ip>

    Floating IP that the port forwarding belongs to (IP
    address or ID)

floating ip port forwarding delete
----------------------------------

Delete floating IP Port Forwarding(s)

.. program:: floating ip port forwarding delete
.. code:: bash

    openstack floating ip port forwarding delete <floating-ip>
    <port-forwarding-id> [<port-forwarding-id> ...]

.. describe:: <floating-ip>

    Floating IP that the port forwarding belongs to (IP
    address or ID)

.. describe:: <port-forwarding-id>

    The ID of the floating IP port forwarding

floating ip port forwarding list
--------------------------------

List floating IP Port Forwarding(s)

.. program:: floating ip port forwarding list
.. code:: bash

    openstack floating ip port forwarding list
    [--port <port>]
    [--external-protocol-port <port-number>]
    [--protocol protocol]
    <floating-ip>

.. option:: --port <port>

    The ID of the network port associated to the floating
    IP port forwarding

.. option:: --protocol <protocol>

    The IP protocol used in the floating IP port
    forwarding

.. describe:: <floating-ip>

    Floating IP that the port forwarding belongs to (IP
    address or ID)

floating ip port forwarding set
-------------------------------

Set floating IP Port Forwarding properties

.. program:: floating ip port forwarding set
.. code:: bash

    openstack floating ip port forwarding set
    [--port <port>]
    [--internal-ip-address <internal-ip-address>]
    [--internal-protocol-port <port-number>]
    [--external-protocol-port <port-number>]
    [--protocol <protocol>]
    <floating-ip>
    <port-forwarding-id>

.. option:: --port <port>

    The ID of the network port associated to the floating
    IP port forwarding

.. option:: --internal-ip-address <internal-ip-address>

    The fixed IPv4 address of the network port associated
    to the floating IP port forwarding

.. option:: --internal-protocol-port <port-number>

    The TCP/UDP/other protocol port number of the network
    port fixed IPv4 address associated to the floating IP
    port forwarding

.. option:: --external-protocol-port <port-number>

    The TCP/UDP/other protocol port number of the port
    forwarding's floating IP address

.. option:: --protocol <protocol>

    The IP protocol used in the floating IP port
    forwarding

.. describe:: <floating-ip>

    Floating IP that the port forwarding belongs to (IP
    address or ID)

.. describe:: <port-forwarding-id>

    The ID of the floating IP port forwarding

floating ip port forwarding show
--------------------------------

Display floating IP Port Forwarding details

.. program:: floating ip port forwarding show
.. code:: bash

    openstack floating ip show <floating-ip> <port-forwarding-id>

.. describe:: <floating-ip>

    Floating IP that the port forwarding belongs to (IP
    address or ID)

.. describe:: <port-forwarding-id>

    The ID of the floating IP port forwarding
