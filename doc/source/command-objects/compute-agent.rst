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

List compute agents

.. program:: compute agent list
.. code:: bash

    os compute agent list [--hypervisor <hypervisor>]

.. option:: --hypervisor <hypervisor>

    Type of hypervisor

compute agent set
-----------------

Set compute agent properties

.. program:: agent set
.. code:: bash

    os compute agent set
        [--agent-version <version>]
        [--url <url]
        [--md5hash <md5hash>]
        <id>

.. _compute_agent-set:
.. option:: --agent-version <version>

    Version of the agent

.. option:: --url <url>

    URL of the agent

.. option:: --md5hash <md5hash>

    MD5 hash of the agent

.. describe:: <id>

    Agent to modify (ID only)
