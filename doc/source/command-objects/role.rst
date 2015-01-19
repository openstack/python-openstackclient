====
role
====

Identity v2, v3

role add
--------

Add role to a user or group in a project or domain

.. program:: role add
.. code:: bash

    os role add
        --domain <domain> | --project <project>
        --user <user> | --group <group>
        <role>

.. option:: --domain <domain>

    Include `<domain>` (name or ID)

    .. versionadded:: 3

.. option:: --project <project>

    Include `<project>` (name or ID)

.. option:: --user <user>

    Include `<user>` (name or ID)

.. option:: --group <group>

    Include `<group>` (name or ID)

    .. versionadded:: 3

.. describe:: <role>

    Role to add to `<project>`:`<user>` (name or ID)

role create
-----------

Create new role

.. program:: role create
.. code:: bash

    os role create
        <name>

.. describe:: <name>

    New role name

role delete
-----------

Delete role(s)

.. program:: role delete
.. code:: bash

    os role delete
        <role> [<role> ...]

.. describe:: <role>

    Role to delete (name or ID)

role list
---------

List roles

.. program:: role list
.. code:: bash

    os role list
        [--domain <domain> | --project <project]
        [--user <user> | --group <group>]

.. option:: --domain <domain>

    Filter roles by <domain> (name or ID)

    .. versionadded:: 3

.. option:: --project <project>

    Filter roles by <project> (name or ID)

    .. versionadded:: 3

.. option:: --user <user>

    Filter roles by <user> (name or ID)

    .. versionadded:: 3

.. option:: --group <group>

    Filter roles by <group> (name or ID)

    .. versionadded:: 3

role remove
-----------

Remove role from domain/project : user/group

.. program:: role remove
.. code:: bash

    os role remove
        [--domain <domain> | --project <project]
        [--user <user> | --group <group>]
        <role>

.. option:: --domain <domain>

    Include `<domain>` (name or ID)

    .. versionadded:: 3

.. option:: --project <project>

    Include `<project>` (name or ID)

.. option:: --user <user>

    Include `<user>` (name or ID)

.. option:: --group <group>

    Include `<group>` (name or ID)

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
        <role>

.. option:: --name <name>

    Set role name

.. describe:: <role>

    Role to modify (name or ID)

role show
---------

Display role details

.. program:: role show
.. code:: bash

    os role show
        <role>

.. describe:: <role>

    Role to display (name or ID)
