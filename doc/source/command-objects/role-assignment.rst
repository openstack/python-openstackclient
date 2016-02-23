===============
role assignment
===============

Identity v2, v3

role assignment list
--------------------

List role assignments

.. program:: role assignment list
.. code:: bash

    os role assignment list
        [--role <role>]
        [--role-domain <role-domain>]
        [--user <user>]
        [--user-domain <user-domain>]
        [--group <group>]
        [--group-domain <group-domain>]
        [--domain <domain>]
        [--project <project>]
        [--project-domain <project-domain>]
        [--effective]
        [--inherited]
        [--names]

.. option:: --role <role>

    Role to filter (name or ID)

    .. versionadded:: 3

.. option:: --role-domain <role-domain>

    Domain the role belongs to (name or ID).
    This can be used in case collisions between role names exist.

    .. versionadded:: 3

.. option:: --user <user>

    User to filter (name or ID)

.. option:: --user-domain <user-domain>

    Domain the user belongs to (name or ID).
    This can be used in case collisions between user names exist.

    .. versionadded:: 3

.. option:: --group <group>

    Group to filter (name or ID)

    .. versionadded:: 3

.. option:: --group-domain <group-domain>

    Domain the group belongs to (name or ID).
    This can be used in case collisions between group names exist.

    .. versionadded:: 3

.. option:: --domain <domain>

    Domain to filter (name or ID)

    .. versionadded:: 3

.. option:: --project <project>

    Project to filter (name or ID)

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name or ID).
    This can be used in case collisions between project names exist.

    .. versionadded:: 3

.. option:: --effective

    Returns only effective role assignments (defaults to False)

    .. versionadded:: 3

.. option:: --inherited

    Specifies if the role grant is inheritable to the sub projects

    .. versionadded:: 3

.. option:: --names

    Returns role assignments with names instead of IDs

.. option:: --auth-user

    Returns role assignments for the authenticated user.

.. option:: --auth-project

    Returns role assignments for the project to which the authenticated user
    is scoped.
