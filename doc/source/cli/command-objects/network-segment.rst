===============
network segment
===============

A **network segment** is an isolated Layer 2 segment within a network.
A network may contain multiple network segments. Depending on the
network configuration, Layer 2 connectivity between network segments
within a network may not be guaranteed.

Network v2

.. NOTE(efried): have to list these out one by one; 'network segment *' pulls
                 ... range *.

.. autoprogram-cliff:: openstack.network.v2
   :command: network segment create

.. autoprogram-cliff:: openstack.network.v2
   :command: network segment delete

.. autoprogram-cliff:: openstack.network.v2
   :command: network segment list

.. autoprogram-cliff:: openstack.network.v2
   :command: network segment set

.. autoprogram-cliff:: openstack.network.v2
   :command: network segment show
