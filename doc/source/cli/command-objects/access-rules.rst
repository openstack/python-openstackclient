===========
access rule
===========

Identity v3

Access rules are fine-grained permissions for application credentials. An access
rule comprises of a service type, a request path, and a request method. Access
rules may only be created as attributes of application credentials, but they may
be viewed and deleted independently.

.. autoprogram-cliff:: openstack.identity.v3
   :command: access rule delete

.. autoprogram-cliff:: openstack.identity.v3
   :command: access rule list

.. autoprogram-cliff:: openstack.identity.v3
   :command: access rule show
