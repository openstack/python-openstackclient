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

.. describe:: <group>

    Group to contain <user> (name or ID)

.. describe:: <user>

    User to add to <group> (name or ID)

group contains user
-------------------

Check user membership in group

.. program:: group contains user
.. code:: bash

    os group contains user
        <group>
        <user>

.. describe:: <group>

    Group to check (name or ID)

.. describe:: <user>

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

    Domain to contain new group (name or ID)

.. option:: --description <description>

    New group description

.. option:: --or-show

    Return existing group

    If the group already exists, return the existing group data and do not fail.

.. describe:: <group-name>

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

    Domain containing group(s) (name or ID)

.. describe:: <group>

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

    Filter group list by <user> (name or ID)

.. option:: --long

    List additional fields in output

group remove user
-----------------

Remove user from group

.. program:: group remove user
.. code:: bash

    os group remove user
        <group>
        <user>

.. describe:: <group>

    Group containing <user> (name or ID)

.. describe:: <user>

    User to remove from <group> (name or ID)

group set
---------

Set group properties

.. program:: group set
.. code:: bash

    os group set
        [--name <name>]
        [--description <description>]
        <group>

.. option:: --name <name>

    New group name

.. option:: --description <description>

    New group description

.. describe:: <group>

    Group to modify (name or ID)

group show
----------

Display group details

.. program:: group show
.. code:: bash

    os group show
        [--domain <domain>]
        <group>

.. option:: --domain <domain>

    Domain containing <group> (name or ID)

.. describe:: <group>

    Group to display (name or ID)
