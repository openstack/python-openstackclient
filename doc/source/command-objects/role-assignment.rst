===============
role assignment
===============

Identity v3

role assignment list
--------------------

List role assignments

.. program:: role assignment list
.. code:: bash

    os role assignment list
        [--role <role>]
        [--user <user>]
        [--user-domain <user-domain>]
        [--group <group>]
        [--group-domain <group-domain>]
        [--domain <domain>]
        [--project <project>]
        [--project-domain <project-domain>]
        [--effective]
        [--inherited]

.. option:: --role <role>

    Role to filter (name or ID)

.. option:: --user <user>

    User to filter (name or ID)

.. option:: --user-domain <user-domain>

    Domain the user belongs to (name or ID).
    This can be used in case collisions between user names exist.

.. option:: --group <group>

    Group to filter (name or ID)

.. option:: --group-domain <group-domain>

    Domain the group belongs to (name or ID).
    This can be used in case collisions between group names exist.

.. option:: --domain <domain>

    Domain to filter (name or ID)

.. option:: --project <project>

    Project to filter (name or ID)

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name or ID).
    This can be used in case collisions between project names exist.

.. option:: --effective

    Returns only effective role assignments (defaults to False)

.. option:: --inherited

    Specifies if the role grant is inheritable to the sub projects

.. option:: --names

    Returns role assignments with names instead of IDs
