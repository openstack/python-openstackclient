===================
Network v2 Commands
===================


address group
-------------

An **address group** is a group of IPv4 or IPv6 address blocks which could be
referenced as a remote source or destination when creating a security group
rule.

.. autoprogram-cliff:: openstack.network.v2
   :command: address group *


address scope
-------------

An **address scope** is a scope of IPv4 or IPv6 addresses that belongs
to a given project and may be shared between projects.

.. autoprogram-cliff:: openstack.network.v2
   :command: address scope *


default security group rule
---------------------------

A **default security group rule** specifies the template of the security group
rules which will be used by neutron to create rules in every new security group.

.. autoprogram-cliff:: openstack.network.v2
   :command: default security group rule *


floating ip port forwarding
---------------------------

.. autoprogram-cliff:: openstack.network.v2
   :command: floating ip port forwarding *


floating ip
-----------

.. NOTE(efried): have to list these out one by one; 'floating ip' pulls in
                 ... pool and ... port forwarding.

.. autoprogram-cliff:: openstack.network.v2
   :command: floating ip create

.. autoprogram-cliff:: openstack.network.v2
   :command: floating ip delete

.. autoprogram-cliff:: openstack.network.v2
   :command: floating ip list

.. autoprogram-cliff:: openstack.network.v2
   :command: floating ip set

.. autoprogram-cliff:: openstack.network.v2
   :command: floating ip show

.. autoprogram-cliff:: openstack.network.v2
   :command: floating ip unset


ip availability
---------------

.. autoprogram-cliff:: openstack.network.v2
   :command: ip availability *


Local IP Associations (local_ip_associations)
---------------------------------------------

The resource lets users assign Local IPs to user Ports.
This is a sub-resource of the Local IP resource.

.. autoprogram-cliff:: openstack.network.v2
   :command: local ip association *


Local IPs (local_ips)
---------------------

Extension that allows users to create a virtual IP that can later be assigned
to multiple ports/VMs (similar to anycast IP) and is guaranteed to only be
reachable within the same physical server/node boundaries

.. autoprogram-cliff:: openstack.network.v2
   :command: local ip *


network agent
-------------

A **network agent** is an agent that handles various tasks used to
implement virtual networks. These agents include neutron-dhcp-agent,
neutron-l3-agent, neutron-metering-agent, and neutron-lbaas-agent,
among others. The agent is available when the alive status of the
agent is "True".

.. autoprogram-cliff:: openstack.network.v2
   :command: network agent *


network auto allocated topology
-------------------------------

An **auto allocated topology** allows admins to quickly set up external
connectivity for end-users. Only one auto allocated topology is allowed per
project. For more information on how to set up the resources required
for auto allocated topology review :neutron-doc:`the documentation
<admin/config-auto-allocation>`.

.. autoprogram-cliff:: openstack.network.v2
   :command: network auto allocated topology *


network flavor profile
----------------------

A **network flavor profile** allows administrators to create, delete, list,
show and update network service profile, which details a framework to enable
operators to configure and users to select from different abstract
representations of a service implementation in the Networking service.
It decouples the logical configuration from its instantiation enabling
operators to create user options according to deployment needs.

.. autoprogram-cliff:: openstack.network.v2
   :command: network flavor profile *


network flavor
--------------

A **network flavor** extension allows the user selection of operator-curated
flavors during resource creations. It allows administrators to create network
service flavors.


.. NOTE(efried): have to list these out one by one; 'network flavor' pulls in
                 ... profile *.

.. autoprogram-cliff:: openstack.network.v2
   :command: network flavor add profile

.. autoprogram-cliff:: openstack.network.v2
   :command: network flavor create

.. autoprogram-cliff:: openstack.network.v2
   :command: network flavor delete

.. autoprogram-cliff:: openstack.network.v2
   :command: network flavor list

.. autoprogram-cliff:: openstack.network.v2
   :command: network flavor remove profile

.. autoprogram-cliff:: openstack.network.v2
   :command: network flavor set

.. autoprogram-cliff:: openstack.network.v2
   :command: network flavor show


network l3 conntrack helper
---------------------------

.. autoprogram-cliff:: openstack.network.v2
   :command: network l3 conntrack helper *


network meter rule
------------------

A **meter rule** sets the rule for
a meter to measure traffic for a specific IP range.
The following uses **meter** and requires the L3
metering extension.

.. autoprogram-cliff:: openstack.network.v2
   :command: network meter rule *


network meter
-------------

A **network meter** allows operators to measure
traffic for a specific IP range. The following commands
are specific to the L3 metering extension.


.. NOTE(efried): have to list these out one by one; 'network meter *' pulls in
                 ... rule *.

.. autoprogram-cliff:: openstack.network.v2
   :command: network meter create

.. autoprogram-cliff:: openstack.network.v2
   :command: network meter delete

.. autoprogram-cliff:: openstack.network.v2
   :command: network meter list

.. autoprogram-cliff:: openstack.network.v2
   :command: network meter show


network qos policy
------------------

A **Network QoS policy** groups a number of Network QoS rules, applied to a
network or a port.

.. autoprogram-cliff:: openstack.network.v2
   :command: network qos policy *


network qos rule type
---------------------

A **Network QoS rule type** is a specific Network QoS rule type available to be
used.

.. autoprogram-cliff:: openstack.network.v2
   :command: network qos rule type *


network qos rule
----------------

A **Network QoS rule** specifies a rule defined in a Network QoS policy; its
type is defined by the parameter 'type'. Can be assigned, within a Network QoS
policy, to a port or a network. Each Network QoS policy can contain several
rules, each of them


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


network rbac
------------

A **network rbac** is a Role-Based Access Control (RBAC) policy for
network resources. It enables both operators and users to grant access
to network resources for specific projects.

.. autoprogram-cliff:: openstack.network.v2
   :command: network rbac *


network segment range
---------------------

A **network segment range** is a resource for tenant network segment
allocation.
A network segment range exposes the segment range management to be administered
via the Neutron API. In addition, it introduces the ability for the
administrator to control the segment ranges globally or on a per-tenant basis.

.. autoprogram-cliff:: openstack.network.v2
   :command: network segment range *


network segment
---------------

A **network segment** is an isolated Layer 2 segment within a network.
A network may contain multiple network segments. Depending on the
network configuration, Layer 2 connectivity between network segments
within a network may not be guaranteed.


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


network service provider
------------------------

A **network service provider** is a particular driver that implements a
networking service


.. _network_service_provider_list:

.. autoprogram-cliff:: openstack.network.v2
   :command: network service provider list


network trunk
-------------

A **network trunk** is a container to group logical ports from different
networks and provide a single trunked vNIC for servers. It consists of
one parent port which is a regular VIF and multiple subports which allow
the server to connect to more networks.

.. autoprogram-cliff:: openstack.network.v2
   :command: network subport list

.. autoprogram-cliff:: openstack.network.v2
   :command: network trunk *


network
-------

A **network** is an isolated Layer 2 networking segment. There are two types
of networks, project and provider networks. Project networks are fully isolated
and are not shared with other projects. Provider networks map to existing
physical networks in the data center and provide external network access for
servers and other resources. Only an OpenStack administrator can create
provider networks. Networks can be connected via routers.


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


port
----

A **port** is a connection point for attaching a single device, such as the
NIC of a server, to a network. The port also describes the associated network
configuration, such as the MAC and IP addresses to be used on that port.

.. autoprogram-cliff:: openstack.network.v2
   :command: port *


router ndp proxy
----------------

An **NDP proxy** publishes a internal IPv6 address to public network. With the
**NDP proxy**, the IPv6 address can be accessed from external. It is similar
to **Floating IP** of IPv4 in functionality.

.. autoprogram-cliff:: openstack.network.v2
   :command: router ndp proxy *


router
------

A **router** is a logical component that forwards data packets between
networks. It also provides Layer 3 and NAT forwarding to provide external
network access for servers on project networks.

.. autoprogram-cliff:: openstack.network.v2
   :command: router *


security group rule
-------------------

A **security group rule** specifies the network access rules for servers
and other resources on the network.

.. autoprogram-cliff:: openstack.network.v2
   :command: security group rule *


security group
--------------

A **security group** acts as a virtual firewall for servers and other
resources on a network. It is a container for security group rules
which specify the network access rules.


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


subnet pool
-----------

A **subnet pool** contains a collection of prefixes in CIDR notation
that are available for IP address allocation.

.. autoprogram-cliff:: openstack.network.v2
   :command: subnet pool *


subnet
------

A **subnet** is a block of IP addresses and associated configuration state.
Subnets are used to allocate IP addresses when new ports are created on a
network.


.. NOTE(efried): have to list these out one by one; 'subnet *' pulls in
                 subnet pool *.

.. autoprogram-cliff:: openstack.network.v2
   :command: subnet create

.. autoprogram-cliff:: openstack.network.v2
   :command: subnet delete

.. autoprogram-cliff:: openstack.network.v2
   :command: subnet list

.. autoprogram-cliff:: openstack.network.v2
   :command: subnet set

.. autoprogram-cliff:: openstack.network.v2
   :command: subnet show

.. autoprogram-cliff:: openstack.network.v2
   :command: subnet unset
