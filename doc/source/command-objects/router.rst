======
router
======

Network v2

router create
-------------

Create new router

.. program:: router create
.. code:: bash

    os router create
        [--project <project> [--project-domain <project-domain>]]
        [--enable | --disable]
        [--distributed]
	[--availability-zone-hint <availability-zone>]
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

.. option:: --availability-zone-hint <availability-zone>

    Availability Zone in which to create this router (requires the Router
    Availability Zone extension, this option can be repeated).

.. _router_create-name:
.. describe:: <name>

    New router name

router delete
-------------

Delete router(s)

.. program:: router delete
.. code:: bash

    os router delete
        <router> [<router> ...]

.. _router_delete-router:
.. describe:: <router>

    Router(s) to delete (name or ID)

router list
-----------

List routers

.. program:: router list
.. code:: bash

    os router list
        [--long]

.. option:: --long

    List additional fields in output

router set
----------

Set router properties

.. program:: router set
.. code:: bash

    os router set
        [--name <name>]
        [--enable | --disable]
        [--distributed | --centralized]
        <router>

.. option:: --name <name>

    Set router name

.. option:: --enable

    Enable router

.. option:: --disable

    Disable router

.. option:: --distributed

    Set router to distributed mode (disabled router only)

.. option:: --centralized

    Set router to centralized mode (disabled router only)

.. _router_set-router:
.. describe:: <router>

    Router to modify (name or ID)

router show
-----------

Display router details

.. program:: router show
.. code:: bash

    os router show
        <router>

.. _router_show-router:
.. describe:: <router>

    Router to display (name or ID)
