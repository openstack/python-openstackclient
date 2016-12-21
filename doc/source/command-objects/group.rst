=====
group
=====

Identity v3

group add user
--------------

Add user to group

.. program:: group add user
.. code:: bash

    openstack group add user
        [--group-domain <group-domain>]
        [--user-domain <user-domain>]
        <group>
        <user>

.. option:: --group-domain <group-domain>

    Domain the group belongs to (name or ID). This can be
    used in case collisions between group names exist.

    .. versionadded:: 3

.. option:: --user-domain <user-domain>

    Domain the user belongs to (name or ID). This can be
    used in case collisions between user names exist.

    .. versionadded:: 3

.. describe:: <group>

    Group to contain <user> (name or ID)

.. describe:: <user>

    User to add to <group> (name or ID)

group contains user
-------------------

Check user membership in group

.. program:: group contains user
.. code:: bash

    openstack group contains user
        [--group-domain <group-domain>]
        [--user-domain <user-domain>]
        <group>
        <user>

.. option:: --group-domain <group-domain>

    Domain the group belongs to (name or ID). This can be
    used in case collisions between group names exist.

    .. versionadded:: 3

.. option:: --user-domain <user-domain>

    Domain the user belongs to (name or ID). This can be
    used in case collisions between user names exist.

    .. versionadded:: 3

.. describe:: <group>

    Group to check (name or ID)

.. describe:: <user>

   User to check (name or ID)

group create
------------

Create new group

.. program:: group create
.. code:: bash

    openstack group create
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

    openstack group delete
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

    openstack group list
        [--domain <domain>]
        [--user <user> [--user-domain <user-domain>]]
        [--long]

.. option:: --domain <domain>

    Filter group list by <domain> (name or ID)

.. option:: --user <user>

    Filter group list by <user> (name or ID)

.. option:: --user-domain <user-domain>

    Domain the user belongs to (name or ID). This can be
    used in case collisions between user names exist.

    .. versionadded:: 3

.. option:: --long

    List additional fields in output

group remove user
-----------------

Remove user from group

.. program:: group remove user
.. code:: bash

    openstack group remove user
        [--group-domain <group-domain>]
        [--user-domain <user-domain>]
        <group>
        <user>

.. option:: --group-domain <group-domain>

    Domain the group belongs to (name or ID). This can be
    used in case collisions between group names exist.

    .. versionadded:: 3

.. option:: --user-domain <user-domain>

    Domain the user belongs to (name or ID). This can be
    used in case collisions between user names exist.

    .. versionadded:: 3

.. describe:: <group>

    Group containing <user> (name or ID)

.. describe:: <user>

    User to remove from <group> (name or ID)

group set
---------

Set group properties

.. program:: group set
.. code:: bash

    openstack group set
        [--domain <domain>]
        [--name <name>]
        [--description <description>]
        <group>

.. option:: --domain <domain>

    Domain containing <group> (name or ID)

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

    openstack group show
        [--domain <domain>]
        <group>

.. option:: --domain <domain>

    Domain containing <group> (name or ID)

.. describe:: <group>

    Group to display (name or ID)
