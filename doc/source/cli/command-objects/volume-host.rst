===========
volume host
===========

Block Storage v2

volume host failover
--------------------

Failover volume host to different backend

.. program:: volume host failover
.. code:: bash

    openstack volume host failover
        --volume-backend <backend-id>
        <host-name>

.. option:: --volume-backend <backend-id>

    The ID of the volume backend replication
    target where the host will failover to (required)

.. _volume_host_failover-host-name:
.. describe:: <host-name>

    Name of volume host

volume host set
---------------

Set volume host properties

.. program:: volume host set
.. code:: bash

    openstack volume host set
        [--enable | --disable]
        <host-name>

.. option:: --enable

    Thaw and enable the specified volume host.

.. option:: --disable

    Freeze and disable the specified volume host

.. _volume_host_set-host-name:
.. describe:: <host-name>

    Name of volume host
