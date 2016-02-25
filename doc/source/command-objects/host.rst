====
host
====

Compute v2

The physical computer running a hypervisor.

host list
---------

List all hosts

.. program:: host list
.. code:: bash

    os host list
        [--zone <availability-zone>]

.. option:: --zone <availability-zone>

    Only return hosts in the availability zone

host show
---------

Display host details

.. program:: host show
.. code:: bash

    os host show
        <host>

.. describe:: <host>

    Name of host
