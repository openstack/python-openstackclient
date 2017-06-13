==================
network qos policy
==================

A **Network QoS policy** groups a number of Network QoS rules, applied to a
network or a port.

Network v2

network qos policy create
-------------------------

Create new Network QoS policy

.. program:: network qos policy create
.. code:: bash

    openstack network qos policy create
        [--description <description>]
        [--share | --no-share]
        [--project <project>]
        [--project-domain <project-domain>]
        <name>

.. option:: --description <description>

    Description of the QoS policy

.. option:: --share

    Make the QoS policy accessible by other projects

.. option:: --no-share

    Make the QoS policy not accessible by other projects (default)

.. option:: --project <project>

    Owner's project (name or ID)

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name or ID).
    This can be used in case collisions between project names exist.

.. _network_qos_policy_create-name:
.. describe:: <name>

    New QoS policy specification name

network qos policy delete
-------------------------

Delete Network QoS policy

.. program:: network qos policy delete
.. code:: bash

    openstack network qos policy delete
         <qos-policy> [<qos-policy> ...]

.. _network_qos_policy_delete-qos-policy:
.. describe:: <qos-policy>

    Network QoS policy(s) to delete (name or ID)

network qos policy list
-----------------------

List Network QoS policies

.. program:: network qos policy list
.. code:: bash

    openstack network qos policy list
        [--project <project> [--project-domain <project-domain>]]
        [--share | --no-share]

.. option:: --project <project>

    List qos policies according to their project (name or ID)

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name or ID).
    This can be used in case collisions between project names exist.

.. option:: --share

    List qos policies shared between projects

.. option:: --no-share

    List qos policies not shared between projects

network qos policy set
----------------------

Set Network QoS policy properties

.. program:: network qos policy set
.. code:: bash

    openstack network qos policy set
        [--name <name>]
        [--description <description>]
        [--share | --no-share]
        <qos-policy>

.. option:: --name <name>

    Name of the QoS policy

.. option:: --description <description>

    Description of the QoS policy

.. option:: --share

    Make the QoS policy accessible by other projects

.. option:: --no-share

    Make the QoS policy not accessible by other projects

.. _network_qos_policy_set-qos-policy:
.. describe:: <qos-policy>

    Network QoS policy to modify (name or ID)

network qos policy show
-----------------------

Display Network QoS policy details

.. program:: network qos policy show
.. code:: bash

    openstack network qos policy show
        <qos-policy>

.. _network_qos_policy_show-qos-policy:
.. describe:: <qos-policy>

    Network QoS policy to display (name or ID)
