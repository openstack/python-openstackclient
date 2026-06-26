=========================
Network v2 FWaaS Commands
=========================


firewall group
--------------

.. NOTE(efried): have to list these out one by one; 'firewall group *' pulls in
                 ... policy * and ... rule *.

.. autoprogram-cliff:: openstack.network.v2.fwaas
   :command: firewall group create

.. autoprogram-cliff:: openstack.network.v2.fwaas
   :command: firewall group delete

.. autoprogram-cliff:: openstack.network.v2.fwaas
   :command: firewall group list

.. autoprogram-cliff:: openstack.network.v2.fwaas
   :command: firewall group set

.. autoprogram-cliff:: openstack.network.v2.fwaas
   :command: firewall group show

.. autoprogram-cliff:: openstack.network.v2.fwaas
   :command: firewall group unset


firewall group policy
---------------------

.. autoprogram-cliff:: openstack.network.v2.fwaas
   :command: firewall group policy *


firewall group rule
-------------------

.. autoprogram-cliff:: openstack.network.v2.fwaas
   :command: firewall group rule *
