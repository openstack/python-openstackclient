=============
network agent
=============

A **network agent** is an agent that handles various tasks used to
implement virtual networks. These agents include neutron-dhcp-agent,
neutron-l3-agent, neutron-metering-agent, and neutron-lbaas-agent,
among others. The agent is available when the alive status of the
agent is "True".

Network v2

network agent delete
--------------------

Delete network agent(s)

.. program:: network agent delete
.. code:: bash

    os network agent delete
        <network-agent> [<network-agent> ...]

.. _network_agent_delete-network-agent:
.. describe:: <network-agent>

    Network agent(s) to delete (ID only)

network agent list
------------------

List network agents

.. program:: network agent list
.. code:: bash

    os network agent list

network agent set
-----------------

Set network agent properties

.. program:: network agent set
.. code:: bash

    os network agent set
        [--description <description>]
        [--enable | --disable]
        <network-agent>

.. option:: --description <description>

    Set network agent description

.. option:: --enable

    Enable network agent

.. option:: --disable

    Disable network agent

.. _network_agent_set-network-agent:
.. describe:: <network-agent>

    Network agent to modify (ID only)

network agent show
------------------

Display network agent details

.. program:: network agent show
.. code:: bash

    os network agent show
        <network-agent>

.. _network_agent_show-network-agent:
.. describe:: <network-agent>

    Network agent to display (ID only)
