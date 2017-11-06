=====================
network qos rule type
=====================

A **Network QoS rule type** is a specific Network QoS rule type available to be
used.

Network v2

network qos rule type list
--------------------------

List Network QoS rule types

.. program:: network qos rule type list
.. code:: bash

    openstack network qos rule type list

network qos rule type show
--------------------------

Display Network QoS rule type details

.. program:: network qos rule type show
.. code:: bash

    openstack network qos rule type show
        <rule-type-name>

.. describe:: <rule-type-name>

    Name of QoS rule type (minimum-bandwidth, dscp-marking, bandwidth-limit)
