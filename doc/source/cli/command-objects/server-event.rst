============
server event
============

Server event are event record for server operations. They consist of: type
(create, delete, reboot and so on), result (success, error), start time, finish
time and so on. These are important for server maintenance.

Compute v2

.. autoprogram-cliff:: openstack.compute.v2
   :command: server event *
