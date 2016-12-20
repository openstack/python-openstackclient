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

    openstack address scope create
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

address scope delete
--------------------

Delete address scope(s)

.. program:: address scope delete
.. code:: bash

    openstack address scope delete
        <address-scope> [<address-scope> ...]

.. _address_scope_delete-address-scope:
.. describe:: <address-scope>

    Address scope(s) to delete (name or ID)

address scope list
------------------

List address scopes

.. program:: address scope list
.. code:: bash

    openstack address scope list
        [--name <name>]
        [--ip-version <ip-version>]
        [--project <project> [--project-domain <project-domain>]]
        [--share | --no-share]

.. option:: --name <name>

    List only address scopes of given name in output

.. option:: --ip-version <ip-version>

    List address scopes of given IP version networks (4 or 6)

.. option:: --project <project>

    List address scopes according to their project (name or ID)

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name or ID).
    This can be used in case collisions between project names exist.

.. option:: --share

    List address scopes shared between projects

.. option:: --no-share

    List address scopes not shared between projects

address scope set
-----------------

Set address scope properties

.. program:: address scope set
.. code:: bash

    openstack address scope set
        [--name <name>]
        [--share | --no-share]
        <address-scope>

.. option:: --name <name>

    Set address scope name

.. option:: --share

    Share the address scope between projects

.. option:: --no-share

    Do not share the address scope between projects

.. _address_scope_set-address-scope:
.. describe:: <address-scope>

    Address scope to modify (name or ID)

address scope show
------------------

Display address scope details

.. program:: address scope show
.. code:: bash

    openstack address scope show
        <address-scope>

.. _address_scope_show-address-scope:
.. describe:: <address-scope>

    Address scope to display (name or ID)
