================
network qos rule
================

A **Network QoS rule** specifies a rule defined in a Network QoS policy; its
type is defined by the parameter 'type'. Can be assigned, within a Network QoS
policy, to a port or a network. Each Network QoS policy can contain several
rules, each of them

Network v2

network qos rule create
-----------------------

Create new Network QoS rule

.. program:: network qos rule create
.. code:: bash

    os network qos rule create
        --type <type>
        [--max-kbps <max-kbps>]
        [--max-burst-kbits <max-burst-kbits>]
        [--dscp-marks <dscp-marks>]
        [--min-kbps <min-kbps>]
        [--ingress | --egress]
        <qos-policy>

.. option:: --type <type>

    QoS rule type (minimum-bandwidth, dscp-marking, bandwidth-limit)

.. option:: --max-kbps <min-kbps>

    Maximum bandwidth in kbps

.. option:: --max-burst-kbits <max-burst-kbits>

    Maximum burst in kilobits, 0 means automatic

.. option:: --dscp-mark <dscp-mark>

    DSCP mark: value can be 0, even numbers from 8-56, excluding 42, 44, 50,
    52, and 54

.. option:: --min-kbps <min-kbps>

    Minimum guaranteed bandwidth in kbps

.. option:: --ingress

    Ingress traffic direction from the project point of view

.. option:: --egress

    Egress traffic direction from the project point of view

.. describe:: <qos-policy>

    QoS policy that contains the rule (name or ID)

network qos rule delete
-----------------------

Delete Network QoS rule

.. program:: network qos rule delete
.. code:: bash

    os network qos rule delete
         <qos-policy>
         <rule-id>

.. describe:: <qos-policy>

    QoS policy that contains the rule (name or ID)

.. describe:: <rule-id>

    Network QoS rule to delete (ID)

network qos rule list
---------------------

List Network QoS rules

.. program:: network qos rule list
.. code:: bash

    os network qos rule list
         <qos-policy>

.. describe:: <qos-policy>

    QoS policy that contains the rule (name or ID)

network qos rule set
--------------------

Set Network QoS rule properties

.. program:: network qos rule set
.. code:: bash

    os network qos rule set
        [--max-kbps <max-kbps>]
        [--max-burst-kbits <max-burst-kbits>]
        [--dscp-marks <dscp-marks>]
        [--min-kbps <min-kbps>]
        [--ingress | --egress]
        <qos-policy>
        <rule-id>

.. option:: --max-kbps <min-kbps>

    Maximum bandwidth in kbps

.. option:: --max-burst-kbits <max-burst-kbits>

    Maximum burst in kilobits, 0 means automatic

.. option:: --dscp-mark <dscp-mark>

    DSCP mark: value can be 0, even numbers from 8-56, excluding 42, 44, 50,
    52, and 54

.. option:: --min-kbps <min-kbps>

    Minimum guaranteed bandwidth in kbps

.. option:: --ingress

    Ingress traffic direction from the project point of view

.. option:: --egress

    Egress traffic direction from the project point of view

.. describe:: <qos-policy>

    QoS policy that contains the rule (name or ID)

.. describe:: <rule-id>

    Network QoS rule to delete (ID)

network qos rule show
---------------------

Display Network QoS rule details

.. program:: network qos rule show
.. code:: bash

    os network qos rule show
        <qos-policy>
        <rule-id>

.. describe:: <qos-policy>

    QoS policy that contains the rule (name or ID)

.. describe:: <rule-id>

    Network QoS rule to delete (ID)
