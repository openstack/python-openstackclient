======
router
======

Network v2

router create
--------------

Create new router

.. program:: router create
.. code:: bash

    os router create
        [--project <project> [--project-domain <project-domain>]]
        [--enable | --disable]
        [--distributed]
        <name>

.. option:: --project <project>

    Owner's project (name or ID)

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name or ID).
    This can be used in case collisions between project names exist.

.. option:: --enable

    Enable router (default)

.. option:: --disable

    Disable router

.. option:: --distributed

    Create a distributed router

.. _router_create-name:
.. describe:: <name>

    New router name

router list
-----------

List routers

.. program:: router list
.. code:: bash

    os router list
        [--long]

.. option:: --long

    List additional fields in output
