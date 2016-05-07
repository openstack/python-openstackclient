=============
address scope
=============

An **address scope** is a scope of IPv4 or IPv6 addresses that belongs
to a given project and may be shared between projects.

Network v2

address scope create
--------------------

Create new address scope

.. program:: address scope create
.. code:: bash

    os address scope create
        [--project <project> [--project-domain <project-domain>]]
        [--ip-version <ip-version>]
        [--share | --no-share]
        <name>

.. option:: --project <project>

    Owner's project (name or ID)

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name or ID).
    This can be used in case collisions between project names exist.

.. option:: --ip-version <ip-version>

    IP version (4 or 6, default is 4)

.. option:: --share

    Share the address scope between projects

.. option:: --no-share

    Do not share the address scope between projects (default)

.. _address_scope_create-name:
.. describe:: <name>

     New address scope name
