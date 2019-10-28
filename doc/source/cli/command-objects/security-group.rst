==============
security group
==============

A **security group** acts as a virtual firewall for servers and other
resources on a network. It is a container for security group rules
which specify the network access rules.

Compute v2, Network v2

.. NOTE(efried): have to list these out one by one; 'security group *' pulls in
                 ... rule *.

.. autoprogram-cliff:: openstack.network.v2
   :command: security group create

.. autoprogram-cliff:: openstack.network.v2
   :command: security group delete

.. autoprogram-cliff:: openstack.network.v2
   :command: security group list

.. autoprogram-cliff:: openstack.network.v2
   :command: security group set

.. autoprogram-cliff:: openstack.network.v2
   :command: security group show

.. autoprogram-cliff:: openstack.network.v2
   :command: security group unset
