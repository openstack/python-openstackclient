============
network rbac
============

A **network rbac** is a Role-Based Access Control (RBAC) policy for
network resources. It enables both operators and users to grant access
to network resources for specific projects.

Network v2

network rbac list
-----------------

List network RBAC policies

.. program:: network rbac list
.. code:: bash

    os network rbac list

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
