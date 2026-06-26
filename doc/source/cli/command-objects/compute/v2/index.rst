===================
Compute v2 Commands
===================


aggregate
---------

Host aggregates provide a mechanism to group hosts according to certain
criteria.

.. autoprogram-cliff:: openstack.compute.v2
   :command: aggregate *


compute agent
-------------

.. autoprogram-cliff:: openstack.compute.v2
   :command: compute agent *


compute service
---------------

.. autoprogram-cliff:: openstack.compute.v2
   :command: compute service *


console connection
------------------

Server console connection information

.. autoprogram-cliff:: openstack.compute.v2
   :command: console connection show


console log
-----------

Server console text dump

.. autoprogram-cliff:: openstack.compute.v2
   :command: console log *


console url
-----------

Server remote console URL

.. autoprogram-cliff:: openstack.compute.v2
   :command: console url *


flavor
------

.. autoprogram-cliff:: openstack.compute.v2
   :command: flavor *


host
----

The physical computer running a hypervisor.

.. autoprogram-cliff:: openstack.compute.v2
   :command: host *


hypervisor stats
----------------

.. autoprogram-cliff:: openstack.compute.v2
   :command: hypervisor stats *


hypervisor
----------

.. NOTE(efried): have to list these out one by one; 'hypervisor *' pulls in
                 ... stats.

.. autoprogram-cliff:: openstack.compute.v2
   :command: hypervisor list

.. autoprogram-cliff:: openstack.compute.v2
   :command: hypervisor show


keypair
-------

The badly named keypair is really the public key of an OpenSSH key pair to be
used for access to created servers. You can also create a private key for
access to a created server by not passing any argument to the keypair create
command.

.. autoprogram-cliff:: openstack.compute.v2
   :command: keypair *


server backup
-------------

A server backup is a disk image created in the Image store from a running server
instance. The backup command manages the number of archival copies to retain.

.. autoprogram-cliff:: openstack.compute.v2
   :command: server backup create


server event
------------

Server event are event record for server operations. They consist of: type
(create, delete, reboot and so on), result (success, error), start time, finish
time and so on. These are important for server maintenance.

.. autoprogram-cliff:: openstack.compute.v2
   :command: server event *


server group
------------

Server groups provide a mechanism to group servers according to certain policy.

.. autoprogram-cliff:: openstack.compute.v2
   :command: server group *


server image
------------

A server image is a disk image created from a running server instance.  The
image is created in the Image store.

.. autoprogram-cliff:: openstack.compute.v2
   :command: server image create


server migration
----------------

A server migration provides a way to move an instance from one
host to another. There are four types of migration operation
supported: live migration, cold migration, resize and evacuation.

.. autoprogram-cliff:: openstack.compute.v2
   :command: server migration *


server share
------------

.. autoprogram-cliff:: openstack.compute.v2
   :command: server share *


server volume
-------------

.. autoprogram-cliff:: openstack.compute.v2
   :command: server volume *


server
------

.. autoprogram-cliff:: openstack.compute.v2
   :command: server add *

.. autoprogram-cliff:: openstack.compute.v2
   :command: server create

.. autoprogram-cliff:: openstack.compute.v2
   :command: server evacuate

.. autoprogram-cliff:: openstack.compute.v2
   :command: server delete

.. autoprogram-cliff:: openstack.compute.v2
   :command: server dump create

.. autoprogram-cliff:: openstack.compute.v2
   :command: server list

.. autoprogram-cliff:: openstack.compute.v2
   :command: server lock

.. autoprogram-cliff:: openstack.compute.v2
   :command: server migrate*

.. autoprogram-cliff:: openstack.compute.v2
   :command: server pause

.. autoprogram-cliff:: openstack.compute.v2
   :command: server reboot

.. autoprogram-cliff:: openstack.compute.v2
   :command: server rebuild

.. autoprogram-cliff:: openstack.compute.v2
   :command: server remove *

.. autoprogram-cliff:: openstack.compute.v2
   :command: server rescue

.. autoprogram-cliff:: openstack.compute.v2
   :command: server resize*

.. autoprogram-cliff:: openstack.compute.v2
   :command: server restore

.. autoprogram-cliff:: openstack.compute.v2
   :command: server resume

.. autoprogram-cliff:: openstack.compute.v2
   :command: server set

.. autoprogram-cliff:: openstack.compute.v2
   :command: server shelve

.. autoprogram-cliff:: openstack.compute.v2
   :command: server show

.. autoprogram-cliff:: openstack.compute.v2
   :command: server ssh

.. autoprogram-cliff:: openstack.compute.v2
   :command: server start

.. autoprogram-cliff:: openstack.compute.v2
   :command: server stop

.. autoprogram-cliff:: openstack.compute.v2
   :command: server suspend

.. autoprogram-cliff:: openstack.compute.v2
   :command: server unlock

.. autoprogram-cliff:: openstack.compute.v2
   :command: server unpause

.. autoprogram-cliff:: openstack.compute.v2
   :command: server unrescue

.. autoprogram-cliff:: openstack.compute.v2
   :command: server unset

.. autoprogram-cliff:: openstack.compute.v2
   :command: server unshelve


usage
-----

.. autoprogram-cliff:: openstack.compute.v2
   :command: usage *
