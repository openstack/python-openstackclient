==========
volume qos
==========

Block Storage v1, v2

volume qos associate
--------------------

Associate a QoS specification to a volume type

.. program:: volume qos associate
.. code:: bash

    openstack volume qos associate
        <qos-spec>
        <volume-type>

.. _volume_qos_associate:
.. describe:: <qos-spec>

    QoS specification to modify (name or ID)

.. describe:: <volume-type>

    Volume type to associate the QoS (name or ID)

volume qos create
-----------------

Create new QoS Specification

.. program:: volume qos create
.. code:: bash

    openstack volume qos create
        [--consumer <consumer>]
        [--property <key=value> [...] ]
        <name>

.. option:: --consumer <consumer>

    Consumer of the QoS. Valid consumers: 'front-end', 'back-end', 'both' (defaults to 'both')

.. option:: --property <key=value>

    Set a property on this QoS specification (repeat option to set multiple properties)

.. _volume_qos_create-name:
.. describe:: <name>

    New QoS specification name

volume qos delete
-----------------

Delete QoS specification

.. program:: volume qos delete
.. code:: bash

    openstack volume qos delete
         [--force]
         <qos-spec> [<qos-spec> ...]

.. option:: --force

    Allow to delete in-use QoS specification(s)

.. _volume_qos_delete-qos-spec:
.. describe:: <qos-spec>

    QoS specification(s) to delete (name or ID)

volume qos disassociate
-----------------------

Disassociate a QoS specification from a volume type

.. program:: volume qos disassociate
.. code:: bash

    openstack volume qos disassociate
        --volume-type <volume-type> | --all
        <qos-spec>

.. option:: --volume-type <volume-type>

    Volume type to disassociate the QoS from (name or ID)

.. option:: --all

    Disassociate the QoS from every volume type

.. _volume_qos_disassociate-qos-spec:
.. describe:: <qos-spec>

    QoS specification to modify (name or ID)

volume qos list
---------------

List QoS specifications

.. program:: volume qos list
.. code:: bash

    openstack volume qos list

volume qos set
--------------

Set QoS specification properties

.. program:: volume qos set
.. code:: bash

    openstack volume qos set
        [--property <key=value> [...] ]
        <qos-spec>

.. option:: --property <key=value>

    Property to add or modify for this QoS specification (repeat option to set multiple properties)

.. _volume_qos_set-qos-spec:
.. describe:: <qos-spec>

    QoS specification to modify (name or ID)

volume qos show
---------------

Display QoS specification details

.. program:: volume qos show
.. code:: bash

    openstack volume qos show
        <qos-spec>

.. _volume_qos_show-qos-spec:
.. describe:: <qos-spec>

   QoS specification to display (name or ID)

volume qos unset
----------------

Unset QoS specification properties

.. program:: volume qos unset
.. code:: bash

    openstack volume qos unset
        [--property <key> [...] ]
        <qos-spec>

.. option:: --property <key>

    Property to remove from QoS specification (repeat option to remove multiple properties)

.. _volume_qos_unset-qos-spec:
.. describe:: <qos-spec>

    QoS specification to modify (name or ID)
