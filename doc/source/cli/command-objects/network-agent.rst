=============
network agent
=============

A **network agent** is an agent that handles various tasks used to
implement virtual networks. These agents include neutron-dhcp-agent,
neutron-l3-agent, neutron-metering-agent, and neutron-lbaas-agent,
among others. The agent is available when the alive status of the
agent is "True".

Network v2

.. autoprogram-cliff:: openstack.network.v2
   :command: network agent *
