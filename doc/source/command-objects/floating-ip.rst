===========
floating ip
===========

Compute v2, Network v2

floating ip create
------------------

Create floating IP

.. program:: floating ip create
.. code:: bash

    openstack floating ip create
        [--subnet <subnet>]
        [--port <port>]
        [--floating-ip-address <floating-ip-address>]
        [--fixed-ip-address <fixed-ip-address>]
        [--description <description>]
        [--project <project> [--project-domain <project-domain>]]
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

.. option:: --project <project>

    Owner's project (name or ID)

    *Network version 2 only*

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name or ID).
    This can be used in case collisions between project names exist.

    *Network version 2 only*

.. describe:: <network>

    Network to allocate floating IP from (name or ID)

floating ip delete
------------------

Delete floating IP(s)

.. program:: floating ip delete
.. code:: bash

    openstack floating ip delete <floating-ip> [<floating-ip> ...]

.. describe:: <floating-ip>

    Floating IP(s) to delete (IP address or ID)

floating ip list
----------------

List floating IP(s)

.. program:: floating ip list
.. code:: bash

    openstack floating ip list
        [--network <network>]
        [--port <port>]
        [--fixed-ip-address <fixed-ip-address>]
        [--long]
        [--status <status>]
        [--project <project> [--project-domain <project-domain>]]
        [--router <router>]

.. option:: --network <network>

    List floating IP(s) according to given network (name or ID)

    *Network version 2 only*

.. option:: --port <port>

    List floating IP(s) according to given port (name or ID)

    *Network version 2 only*

.. option:: --fixed-ip-address <fixed-ip-address>

    List floating IP(s) according to given fixed IP address

    *Network version 2 only*

.. option:: --long

    List additional fields in output

    *Network version 2 only*

.. option:: --status <status>

    List floating IP(s) according to given status ('ACTIVE', 'DOWN')

    *Network version 2 only*

.. option:: --project <project>

    List floating IP(s) according to given project (name or ID)

    *Network version 2 only*

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name or ID). This can
    be used in case collisions between project names exist.

    *Network version 2 only*

.. option:: --router <router>

    List floating IP(s) according to given router (name or ID)

    *Network version 2 only*

floating ip show
----------------

Display floating IP details

.. program:: floating ip show
.. code:: bash

    openstack floating ip show <floating-ip>

.. describe:: <floating-ip>

    Floating IP to display (IP address or ID)
