=====
group
=====

Identity v3

group add user
--------------

Add user to group

.. program:: group add user
.. code:: bash

    os group add user
        <group>
        <user>

.. option:: <group>

    Group that user will be added to (name or ID)

.. option:: <user>

    User to add to group (name or ID)

group contains user
-------------------

Check user in group

.. program:: group contains user
.. code:: bash

    os group contains user
        <group>
        <user>

.. option:: <group>

    Group to check if user belongs to (name or ID)

.. option:: <user>

   User to check (name or ID)

group create
------------

Create new group

.. program:: group create
.. code:: bash

    os group create
        [--domain <domain>]
        [--description <description>]
        [--or-show]
        <group-name>

.. option:: --domain <domain>

    References the domain ID or name which owns the group

.. option:: --description <description>

    New group description

.. option:: --or-show

    Return existing group

    If the group already exists, return the existing group data and do not fail.

.. option:: <group-name>

    New group name

group delete
------------

Delete group

.. program:: group delete
.. code:: bash

    os group delete
        [--domain <domain>]
        <group> [<group> ...]

.. option:: --domain <domain>

    Domain where group resides (name or ID)

.. option:: <group>

    Group(s) to delete (name or ID)

group list
----------

List groups

.. program:: group list
.. code:: bash

    os group list
        [--domain <domain>]
        [--user <user>]
        [--long]

.. option:: --domain <domain>

    Filter group list by <domain> (name or ID)

.. option:: --user <user>

    List group memberships for <user> (name or ID)

.. option:: --long

    List additional fields in output (defaults to false)

group remove user
-----------------

Remove user from group

.. program:: group remove user
.. code:: bash

    os group remove user
        <group>
        <user>

.. option:: <group>

    Group that user will be removed from (name or ID)

.. option:: <user>

    User to remove from group (name or ID)

group set
---------

Set group properties

.. program:: group set
.. code:: bash

    os group set
        [--name <name>]
        [--domain <domain>]
        [--description <description>]
        <group>

.. option:: --name <name>

    New group name

.. option:: --domain <domain>

    New domain that will now own the group (name or ID)

.. option:: --description <description>

    New group description

.. option:: <group>

    Group to modify (name or ID)

group show
----------

Show group details

.. program:: group show
.. code:: bash

    os group show
        [--domain <domain>]
        <group>

.. option:: --domain <domain>

    Domain where group resides (name or ID)

.. option:: <group>

    Group to display (name or ID)
