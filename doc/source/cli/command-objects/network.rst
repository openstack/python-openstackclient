=======
network
=======

A **network** is an isolated Layer 2 networking segment. There are two types
of networks, project and provider networks. Project networks are fully isolated
and are not shared with other projects. Provider networks map to existing
physical networks in the data center and provide external network access for
servers and other resources. Only an OpenStack administrator can create
provider networks. Networks can be connected via routers.

Compute v2, Network v2

.. NOTE(efried): have to list these out one by one; 'network *' pulls in
                 ... flavor *, ... qos policy *, etc.

.. autoprogram-cliff:: openstack.network.v2
   :command: network create

.. autoprogram-cliff:: openstack.network.v2
   :command: network delete

.. autoprogram-cliff:: openstack.network.v2
   :command: network list

.. autoprogram-cliff:: openstack.network.v2
   :command: network set

.. autoprogram-cliff:: openstack.network.v2
   :command: network show

.. autoprogram-cliff:: openstack.network.v2
   :command: network unset
