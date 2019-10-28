=====================
network segment range
=====================

A **network segment range** is a resource for tenant network segment
allocation.
A network segment range exposes the segment range management to be administered
via the Neutron API. In addition, it introduces the ability for the
administrator to control the segment ranges globally or on a per-tenant basis.

Network v2

.. autoprogram-cliff:: openstack.network.v2
   :command: network segment range *
