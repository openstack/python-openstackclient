============
server group
============

Server group provides a mechanism to group servers according to certain policy.

Compute v2

server group create
-------------------

Create a new server group

.. program:: server group create
.. code-block:: bash

    os server group create
        --policy <policy> [--policy <policy>] ...
        <name>

.. option:: --policy <policy>

    Add a policy to :ref:`\<name\> <server_group_create-name>`
    (repeat option to add multiple policies)

.. _server_group_create-name:
.. describe:: <name>

    New server group name

server group delete
-------------------

Delete existing server group(s)

.. program:: server group delete
.. code-block:: bash

    os server group delete
        <server-group> [<server-group> ...]

.. describe:: <server-group>

    Server group(s) to delete (name or ID)
    (repeat to delete multiple server groups)

server group list
-----------------

List all server groups

.. program:: server group list
.. code-block:: bash

    os server group list
        [--all-projects]
        [--long]

.. option:: --all-projects

    Display information from all projects (admin only)

.. option:: --long

    List additional fields in output

server group show
-----------------

Display server group details

.. program:: server group show
.. code-block:: bash

    os server group show
        <server-group>

.. describe:: <server-group>

    Server group to display (name or ID)
