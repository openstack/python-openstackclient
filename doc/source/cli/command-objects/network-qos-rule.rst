================
network qos rule
================

A **Network QoS rule** specifies a rule defined in a Network QoS policy; its
type is defined by the parameter 'type'. Can be assigned, within a Network QoS
policy, to a port or a network. Each Network QoS policy can contain several
rules, each of them

Network v2

.. NOTE(efried): have to list these out one by one; 'network qos rule *' pulls
                 network qos rule type *.

.. autoprogram-cliff:: openstack.network.v2
   :command: network qos rule create

.. autoprogram-cliff:: openstack.network.v2
   :command: network qos rule delete

.. autoprogram-cliff:: openstack.network.v2
   :command: network qos rule list

.. autoprogram-cliff:: openstack.network.v2
   :command: network qos rule set

.. autoprogram-cliff:: openstack.network.v2
   :command: network qos rule show
