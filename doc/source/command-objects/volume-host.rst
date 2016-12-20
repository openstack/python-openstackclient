===========
volume host
===========

Volume v2

volume host set
---------------

Set volume host properties

.. program:: volume host set
.. code:: bash

    openstack volume host set
        [--enable | --disable]
        <host-name>

.. option:: --enable

    Thaw and enable the specified volume host

.. option:: --disable

    Freeze and disable the specified volume host

.. _volume-host-set:
.. describe:: <host-name>

    Name of volume host
