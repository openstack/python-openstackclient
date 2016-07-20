===========
ip floating
===========

Compute v2, Network v2

ip floating add
---------------

Add floating IP address to server
(Deprecated, please use ``server add floating ip`` instead)

.. program:: ip floating add
.. code:: bash

    os ip floating add
        <ip-address>
        <server>

.. describe:: <ip-address>

    IP address to add to server (name only)

.. describe:: <server>

    Server to receive the IP address (name or ID)

ip floating create
------------------

Create new floating IP address
(Deprecated, please use ``floating ip create`` instead)

.. program:: ip floating create
.. code:: bash

    os ip floating create
        [--subnet <subnet>]
        [--port <port>]
        [--floating-ip-address <floating-ip-address>]
        [--fixed-ip-address <fixed-ip-address>]
        <network>

.. option:: --subnet <subnet>

    Subnet on which you want to create the floating IP (name or ID)
    (Network v2 only)

.. option:: --port <port>

    Port to be associated with the floating IP (name or ID)
    (Network v2 only)

.. option:: --floating-ip-address <floating-ip-address>

    Floating IP address
    (Network v2 only)

.. option:: --fixed-ip-address <fixed-ip-address>

    Fixed IP address mapped to the floating IP
    (Network v2 only)

.. describe:: <network>

    Network to allocate floating IP from (name or ID)

ip floating delete
------------------

Delete floating IP(s)
(Deprecated, please use ``floating ip delete`` instead)

.. program:: ip floating delete
.. code:: bash

    os ip floating delete
        <floating-ip> [<floating-ip> ...]

.. describe:: <floating-ip>

    Floating IP(s) to delete (IP address or ID)

ip floating list
----------------

List floating IP addresses
(Deprecated, please use ``floating ip list`` instead)

.. program:: ip floating list
.. code:: bash

    os ip floating list

ip floating remove
------------------

Remove floating IP address from server
(Deprecated, please use ``server remove floating ip`` instead)

.. program:: ip floating remove
.. code:: bash

    os ip floating remove
        <ip-address>
        <server>

.. describe:: <ip-address>

    IP address to remove from server (name only)

.. describe:: <server>

    Server to remove the IP address from (name or ID)

ip floating show
----------------

Display floating IP details
(Deprecated, please use ``floating ip show`` instead)

.. program:: ip floating show
.. code:: bash

    os ip floating show <floating-ip>

.. describe:: <floating-ip>

    Floating IP to display (IP address or ID)
