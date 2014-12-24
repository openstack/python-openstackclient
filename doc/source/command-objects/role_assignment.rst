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
        [--group <group>]
        [--domain <domain>]
        [--project <project>]
        [--effective]

.. option:: --role <role>

    Role to filter (name or ID)

.. option:: --user <user>

    User to filter (name or ID)

.. option:: --group <group>

    Group to filter (name or ID)

.. option:: --domain <domain>

    Domain to filter (name or ID)

.. option:: --project <project>

    Project to filter (name or ID)

.. option:: --effective

    Returns only effective role assignments (defaults to False)
