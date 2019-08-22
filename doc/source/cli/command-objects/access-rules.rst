===========
access rule
===========

Identity v3

Access rules are fine-grained permissions for application credentials. An access
rule comprises of a service type, a request path, and a request method. Access
rules may only be created as attributes of application credentials, but they may
be viewed and deleted independently.


access rule delete
------------------

Delete access rule(s)

.. program:: access rule delete
.. code:: bash

    openstack access rule delete <access-rule> [<access-rule> ...]

.. describe:: <access-rule>

    Access rule(s) to delete (ID)

access rule list
----------------

List access rules

.. program:: access rule list
.. code:: bash

    openstack access rule list
        [--user <user>]
        [--user-domain <user-domain>]

.. option:: --user

    User whose access rules to list (name or ID). If not provided, looks up the
    current user's access rules.

.. option:: --user-domain

    Domain the user belongs to (name or ID). This can be
    used in case collisions between user names exist.

access rule show
---------------------------

Display access rule details

.. program:: access rule show
.. code:: bash

    openstack access rule show <access-rule>

.. describe:: <access-rule>

    Access rule to display (ID)
