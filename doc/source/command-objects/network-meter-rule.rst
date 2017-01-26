==================
network meter rule
==================

A **meter rule** sets the rule for
a meter to measure traffic for a specific IP range.
The following uses **meter** and requires the L3
metering extension.

Network v2

network meter rule create
-------------------------

Create meter rule

.. program:: network meter rule create
.. code:: bash

    openstack network meter rule create
        --remote-ip-prefix <remote-ip-prefix>
        [--ingress | --egress]
        [--exclude | --include]
        [--project <project> [--project-domain <project-domain>]]
        <meter>

.. option:: --project <project>

    Owner's project (name or ID)

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name of ID).
    This can be used in case collisions between project names exist.

.. option:: --ingress

    Rule is applied to incoming traffic (default)

.. option:: --egress

    Rule is applied to outgoing traffic

.. option:: --exclude

    Exclude remote_ip_prefix from count of the traffic of IP addresses

.. option:: --include

    Include remote_ip_prefix into count of the traffic of IP addresses
    (default)

.. option:: --remote-ip-prefix <remote-ip-prefix>

    The remote IP prefix to associate with this metering rule packet

.. _network_meter_rule_create:
.. describe:: <meter>

    Meter to associate with this meter rule (name or ID)


network meter rule delete
-------------------------

Delete meter rule(s)

.. program:: network meter rule delete
.. code:: bash

    openstack network meter rule delete <id> [<id> ...]

.. _network_meter_rule_delete:
.. describe:: <meter-rule-id>

    ID of meter rule(s) to delete

network meter rule list
-----------------------

List meter rules

.. program:: network meter rule list
.. code:: bash

    openstack network meter rule list

network meter rule show
-----------------------

Show meter rule

.. program:: network meter rule show
.. code:: bash

    openstack network meter rule show <meter-rule-id>

.. _network_meter_show:
.. describe:: <meter-rule-id>

    Meter rule to display (ID only)
