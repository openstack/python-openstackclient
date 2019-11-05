=============
network meter
=============

A **network meter** allows operators to measure
traffic for a specific IP range. The following commands
are specific to the L3 metering extension.

Network v2

.. NOTE(efried): have to list these out one by one; 'network meter *' pulls in
                 ... rule *.

.. autoprogram-cliff:: openstack.network.v2
   :command: network meter create

.. autoprogram-cliff:: openstack.network.v2
   :command: network meter delete

.. autoprogram-cliff:: openstack.network.v2
   :command: network meter list

.. autoprogram-cliff:: openstack.network.v2
   :command: network meter show
