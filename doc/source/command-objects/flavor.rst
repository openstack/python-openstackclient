======
flavor
======

Compute v2

flavor create
-------------

Create new flavor

.. program:: flavor create
.. code:: bash

    os flavor create
        [--id <id>]
        [--ram <size-mb>]
        [--disk <size-gb>]
        [--ephemeral-disk <size-gb>]
        [--swap <size-mb>]
        [--vcpus <num-cpu>]
        [--rxtx-factor <factor>]
        [--public | --private]
        <flavor-name>

.. option:: --id <id>

    Unique flavor ID; 'auto' creates a UUID (default: auto)

.. option:: --ram <size-mb>

    Memory size in MB (default 256M)

.. option:: --disk <size-gb>

    Disk size in GB (default 0G)

.. option:: --ephemeral-disk <size-gb>

    Ephemeral disk size in GB (default 0G)

.. option:: --swap <size-gb>

    Swap space size in GB (default 0G)

.. option:: --vcpus <num-cpu>

    Number of vcpus (default 1)

.. option:: --rxtx-factor <factor>

    RX/TX factor (default 1)

.. option:: --public

    Flavor is available to other projects (default)

.. option:: --private

    Flavor is not available to other projects

.. _flavor_create-flavor-name:
.. describe:: <flavor-name>

    New flavor name

flavor delete
-------------

Delete flavor

.. program:: flavor delete
.. code:: bash

    os flavor delete
        <flavor>

.. _flavor_delete-flavor:
.. describe:: <flavor>

    Flavor to delete (name or ID)

flavor list
-----------

List flavors

.. program:: flavor list
.. code:: bash

    os flavor list
        [--public | --private | --all]
        [--long]

.. option:: --public

    List only public flavors (default)

.. option:: --private

    List only private flavors

.. option:: --all

    List all flavors, whether public or private

.. option:: --long

    List additional fields in output

flavor show
-----------

Display flavor details

.. program:: flavor show
.. code:: bash

    os flavor show
        <flavor>

.. _flavor_show-flavor:
.. describe:: <flavor>

    Flavor to display (name or ID)
