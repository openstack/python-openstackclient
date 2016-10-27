==========
hypervisor
==========

Compute v2

hypervisor list
---------------

List hypervisors

.. program:: hypervisor list
.. code:: bash

    os hypervisor list
        [--matching <hostname>]
        [--long]

.. option:: --matching <hostname>

    Filter hypervisors using <hostname> substring

.. option:: --long

    List additional fields in output

hypervisor show
---------------

Display hypervisor details

.. program:: hypervisor show
.. code:: bash

    os hypervisor show
        <hypervisor>

.. _hypervisor_show-flavor:
.. describe:: <hypervisor>

    Hypervisor to display (name or ID)
