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

    os network qos policy create
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

.. option:: --project-domain <project-domain>]

    Domain the project belongs to (name or ID).
    This can be used in case collisions between project names exist.

.. describe:: <name>

    New QoS policy specification name

network qos policy delete
-------------------------

Delete Network QoS policy

.. program:: network qos policy delete
.. code:: bash

    os network qos policy delete
         <qos-policy> [<qos-policy> ...]

.. describe:: <qos-policy>

    Network QoS policy(s) to delete (name or ID)

network qos policy list
-----------------------

List Network QoS policies

.. program:: network qos policy list
.. code:: bash

    os network qos policy list

network qos policy set
----------------------

Set Network QoS policy properties

.. program:: network qos policy set
.. code:: bash

    os network qos policy set
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

.. describe:: <qos-policy>

    Network QoS policy(s) to delete (name or ID)

network qos policy show
-----------------------

Display Network QoS policy details

.. program:: network qos policy show
.. code:: bash

    os network qos policy show
        <qos-policy>

.. describe:: <qos-policy>

    Network QoS policy(s) to show (name or ID)
