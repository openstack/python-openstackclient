====
host
====

Compute v2

The physical computer running a hypervisor.

host list
---------

List hosts

.. program:: host list
.. code:: bash

    os host list
        [--zone <availability-zone>]

.. option:: --zone <availability-zone>

    Only return hosts in the availability zone

host set
--------

Set host properties

.. program:: host set
.. code:: bash

    os host set
        [--enable | --disable]
        [--enable-maintenance | --disable-maintenance]
        <host>

.. _host-set:
.. option:: --enable

    Enable the host

.. option:: --disable

    Disable the host

.. _maintenance-set:
.. option:: --enable-maintenance

    Enable maintenance mode for the host

.. option:: --disable-maintenance

    Disable maintenance mode for the host

.. describe:: <host>

    Host to modify (name only)

host show
---------

Display host details

.. program:: host show
.. code:: bash

    os host show
        <host>

.. describe:: <host>

    Name of host
