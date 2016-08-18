====
role
====

Identity v2, v3

role add
--------

Add role assignment to a user or group in a project or domain

.. program:: role add
.. code:: bash

    os role add
        --domain <domain> | --project <project> [--project-domain <project-domain>]
        --user <user> [--user-domain <user-domain>] | --group <group> [--group-domain <group-domain>]
        --role-domain <role-domain>
        --inherited
        <role>

.. option:: --domain <domain>

    Include <domain> (name or ID)

    .. versionadded:: 3

.. option:: --project <project>

    Include <project> (name or ID)

.. option:: --user <user>

    Include <user> (name or ID)

.. option:: --group <group>

    Include <group> (name or ID)

    .. versionadded:: 3

.. option:: --user-domain <user-domain>

    Domain the user belongs to (name or ID).
    This can be used in case collisions between user names exist.

    .. versionadded:: 3

.. option:: --group-domain <group-domain>

    Domain the group belongs to (name or ID).
    This can be used in case collisions between group names exist.

    .. versionadded:: 3

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name or ID).
    This can be used in case collisions between project names exist.

    .. versionadded:: 3

.. option:: --inherited

    Specifies if the role grant is inheritable to the sub projects.

    .. versionadded:: 3

.. option:: --role-domain <role-domain>

    Domain the role belongs to (name or ID).
    This must be specified when the name of a domain specific role is used.

    .. versionadded:: 3

.. describe:: <role>

    Role to add to <project>:<user> (name or ID)

role create
-----------

Create new role

.. program:: role create
.. code:: bash

    os role create
        [--or-show]
        [--domain <domain>]
        <name>

.. option:: --domain <domain>

    Domain the role belongs to (name or ID).

    .. versionadded:: 3

.. option:: --or-show

    Return existing role

    If the role already exists return the existing role data and do not fail.

.. describe:: <name>

    New role name

role delete
-----------

Delete role(s)

.. program:: role delete
.. code:: bash

    os role delete
        <role> [<role> ...]
        [--domain <domain>]

.. describe:: <role>

    Role to delete (name or ID)

.. option:: --domain <domain>

    Domain the role belongs to (name or ID).

    .. versionadded:: 3

role list
---------

List roles

.. program:: role list
.. code:: bash

    os role list
        --domain <domain> | --project <project> [--project-domain <project-domain>]
        --user <user> [--user-domain <user-domain>] | --group <group> [--group-domain <group-domain>]
        --inherited

.. option:: --domain <domain>

    Filter roles by <domain> (name or ID)

    (Deprecated if being used to list assignments in conjunction with the
    ``--user <user>``, option, please use ``role assignment list`` instead)

.. option:: --project <project>

    Filter roles by <project> (name or ID)

    (Deprecated, please use ``role assignment list`` instead)

.. option:: --user <user>

    Filter roles by <user> (name or ID)

    (Deprecated, please use ``role assignment list`` instead)

.. option:: --group <group>

    Filter roles by <group> (name or ID)

    (Deprecated, please use ``role assignment list`` instead)

.. option:: --user-domain <user-domain>

    Domain the user belongs to (name or ID).
    This can be used in case collisions between user names exist.

    (Deprecated, please use ``role assignment list`` instead)

    .. versionadded:: 3

.. option:: --group-domain <group-domain>

    Domain the group belongs to (name or ID).
    This can be used in case collisions between group names exist.

    (Deprecated, please use ``role assignment list`` instead)

    .. versionadded:: 3

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name or ID).
    This can be used in case collisions between project names exist.

    (Deprecated, please use ``role assignment list`` instead)

    .. versionadded:: 3

.. option:: --inherited

    Specifies if the role grant is inheritable to the sub projects.

    (Deprecated, please use ``role assignment list`` instead)

    .. versionadded:: 3

role remove
-----------

Remove role assignment from domain/project : user/group

.. program:: role remove
.. code:: bash

    os role remove
        --domain <domain> | --project <project> [--project-domain <project-domain>]
        --user <user> [--user-domain <user-domain>] | --group <group> [--group-domain <group-domain>]
        --role-domain <role-domain>
        --inherited
        <role>

.. option:: --domain <domain>

    Include <domain> (name or ID)

    .. versionadded:: 3

.. option:: --project <project>

    Include <project> (name or ID)

.. option:: --user <user>

    Include <user> (name or ID)

.. option:: --group <group>

    Include <group> (name or ID)

    .. versionadded:: 3

.. option:: --user-domain <user-domain>

    Domain the user belongs to (name or ID).
    This can be used in case collisions between user names exist.

    .. versionadded:: 3

.. option:: --group-domain <group-domain>

    Domain the group belongs to (name or ID).
    This can be used in case collisions between group names exist.

    .. versionadded:: 3

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name or ID).
    This can be used in case collisions between project names exist.

    .. versionadded:: 3

.. option:: --inherited

    Specifies if the role grant is inheritable to the sub projects.

    .. versionadded:: 3

.. option:: --role-domain <role-domain>

    Domain the role belongs to (name or ID).
    This must be specified when the name of a domain specific role is used.

    .. versionadded:: 3

.. describe:: <role>

    Role to remove (name or ID)

role set
--------

Set role properties

.. versionadded:: 3

.. program:: role set
.. code:: bash

    os role set
        [--name <name>]
        [--domain <domain>]
        <role>

.. option:: --name <name>

    Set role name

.. option:: --domain <domain>

    Domain the role belongs to (name or ID).

    .. versionadded:: 3

.. describe:: <role>

    Role to modify (name or ID)

role show
---------

Display role details

.. program:: role show
.. code:: bash

    os role show
        [--domain <domain>]
        <role>

.. option:: --domain <domain>

    Domain the role belongs to (name or ID).

    .. versionadded:: 3

.. describe:: <role>

    Role to display (name or ID)
