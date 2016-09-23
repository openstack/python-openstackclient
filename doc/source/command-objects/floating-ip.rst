===========
floating ip
===========

Compute v2, Network v2

floating ip create
------------------

Create floating IP

.. program:: floating ip create
.. code:: bash

    os floating ip create
        [--subnet <subnet>]
        [--port <port>]
        [--floating-ip-address <floating-ip-address>]
        [--fixed-ip-address <fixed-ip-address>]
        [--description <description>]
        <network>

.. option:: --subnet <subnet>

    Subnet on which you want to create the floating IP (name or ID)
    *Network version 2 only*

.. option:: --port <port>

    Port to be associated with the floating IP (name or ID)
    *Network version 2 only*

.. option:: --floating-ip-address <floating-ip-address>

    Floating IP address
    *Network version 2 only*

.. option:: --fixed-ip-address <fixed-ip-address>

    Fixed IP address mapped to the floating IP
    *Network version 2 only*

.. option:: --description <description>

    Set floating IP description
    *Network version 2 only*

.. describe:: <network>

    Network to allocate floating IP from (name or ID)

floating ip delete
------------------

Delete floating IP(s)

.. program:: floating ip delete
.. code:: bash

    os floating ip delete <floating-ip> [<floating-ip> ...]

.. describe:: <floating-ip>

    Floating IP(s) to delete (IP address or ID)

floating ip list
----------------

List floating IP(s)

.. program:: floating ip list
.. code:: bash

    os floating ip list

floating ip show
----------------

Display floating IP details

.. program:: floating ip show
.. code:: bash

    os floating ip show <floating-ip>

.. describe:: <floating-ip>

    Floating IP to display (IP address or ID)
