=============
network trunk
=============

A **network trunk** is a container to group logical ports from different
networks and provide a single trunked vNIC for servers. It consists of
one parent port which is a regular VIF and multiple subports which allow
the server to connect to more networks.

Network v2

.. autoprogram-cliff:: openstack.network.v2
   :command: network subport list

.. autoprogram-cliff:: openstack.network.v2
   :command: network trunk *
