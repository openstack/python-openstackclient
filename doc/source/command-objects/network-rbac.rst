============
network rbac
============

A **network rbac** is a Role-Based Access Control (RBAC) policy for
network resources. It enables both operators and users to grant access
to network resources for specific projects.

Network v2

network rbac create
-------------------

Create network RBAC policy

.. program:: network rbac create
.. code:: bash

    os network rbac create
        --type <type>
        --action <action>
        --target-project <target-project> [--target-project-domain <target-project-domain>]
        [--project <project> [--project-domain <project-domain>]]
        <rbac-policy>

.. option:: --type <type>

    Type of the object that RBAC policy affects ("qos_policy" or "network") (required)

.. option:: --action <action>

    Action for the RBAC policy ("access_as_external" or "access_as_shared") (required)

.. option:: --target-project <target-project>

    The project to which the RBAC policy will be enforced (name or ID) (required)

.. option:: --target-project-domain <target-project-domain>

    Domain the target project belongs to (name or ID).
    This can be used in case collisions between project names exist.

.. option:: --project <project>

    The owner project (name or ID)

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name or ID).
    This can be used in case collisions between project names exist.

.. _network_rbac_create-rbac-policy:
.. describe:: <rbac-object>

    The object to which this RBAC policy affects (name or ID for network objects, ID only for QoS policy objects)

network rbac delete
-------------------

Delete network RBAC policy(s)

.. program:: network rbac delete
.. code:: bash

    os network rbac delete
        <rbac-policy> [<rbac-policy> ...]

.. _network_rbac_delete-rbac-policy:
.. describe:: <rbac-policy>

    RBAC policy(s) to delete (ID only)

network rbac list
-----------------

List network RBAC policies

.. program:: network rbac list
.. code:: bash

    os network rbac list

network rbac set
----------------

Set network RBAC policy properties

.. program:: network rbac set
.. code:: bash

    os network rbac set
        [--target-project <target-project> [--target-project-domain <target-project-domain>]]
        <rbac-policy>

.. option:: --target-project <target-project>

    The project to which the RBAC policy will be enforced (name or ID)

.. option:: --target-project-domain <target-project-domain>

    Domain the target project belongs to (name or ID).
    This can be used in case collisions between project names exist.

.. _network_rbac_set-rbac-policy:
.. describe:: <rbac-policy>

    RBAC policy to be modified (ID only)

network rbac show
-----------------

Display network RBAC policy details

.. program:: network rbac show
.. code:: bash

    os network rbac show
        <rbac-policy>

.. _network_rbac_show-rbac-policy:
.. describe:: <rbac-policy>

    RBAC policy (ID only)
