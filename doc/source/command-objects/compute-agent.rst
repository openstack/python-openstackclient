=============
compute agent
=============

Compute v2

compute agent create
--------------------

Create compute agent

.. program:: compute agent create
.. code:: bash

    os compute agent create
        <os> <architecture> <version> <url> <md5hash>
        <hypervisor>

.. _compute_agent-create:
.. describe:: <os>

    Type of OS

.. describe:: <architecture>

    Type of architecture

.. describe:: <version>

    Version

.. describe:: <url>

    URL

.. describe:: <md5hash>

    MD5 hash

.. describe:: <hypervisor>

    Type of hypervisor

compute agent delete
--------------------

Delete compute agent(s)

.. program:: compute agent delete
.. code:: bash

    os compute agent delete <id> [<id> ...]

.. _compute_agent-delete:
.. describe:: <id>

    ID of agent(s) to delete

compute agent list
------------------

List compute agent command

.. program:: compute agent list
.. code:: bash

    os compute agent list [--hypervisor <hypervisor>]

.. _compute_agent-list:
.. describe:: --hypervisor <hypervisor>

    Optional type of hypervisor

compute agent set
-----------------

Set compute agent command

.. program:: agent set
.. code:: bash

    os compute agent set
        <id> <version> <url> <md5hash>

.. _compute_agent-set:
.. describe:: <id>

    ID of the agent

.. describe:: <version>

    Version of the agent

.. describe:: <url>

    URL

.. describe:: <md5hash>

    MD5 hash
