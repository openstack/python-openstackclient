==========
volume qos
==========

Block Storage v1, v2

volume qos associate
--------------------

Associate a QoS specification to a volume type

.. program:: volume qos associate
.. code:: bash

    os volume qos associate
        <qos-spec>
        <volume-type>

.. describe:: <qos-spec>

    QoS specification to modify (name or ID)

.. describe:: <volume-type>

    Volume type to associate the QoS (name or ID)

volume qos create
-----------------

Create new QoS Specification

.. program:: volume qos create
.. code:: bash

    os volume qos create
        [--consumer <consumer>]
        [--property <key=value> [...] ]
        <name>

.. option:: --consumer <consumer>

    Consumer of the QoS. Valid consumers: 'front-end', 'back-end', 'both' (defaults to 'both')

.. option:: --property <key=value>

    Set a property on this QoS specification (repeat option to set multiple properties)

.. describe:: <name>

    New QoS specification name

volume qos delete
-----------------

Delete QoS specification

.. program:: volume qos delete
.. code:: bash

    os volume qos delete
         [--force]
         <qos-spec> [<qos-spec> ...]

.. option:: --force

    Allow to delete in-use QoS specification(s)

.. describe:: <qos-spec>

    QoS specification(s) to delete (name or ID)

volume qos disassociate
-----------------------

Disassociate a QoS specification from a volume type

.. program:: volume qos disassociate
.. code:: bash

    os volume qos disassociate
        --volume-type <volume-type> | --all
        <qos-spec>

.. option:: --volume-type <volume-type>

    Volume type to disassociate the QoS from (name or ID)

.. option:: --all

    Disassociate the QoS from every volume type

.. describe:: <qos-spec>

    QoS specification to modify (name or ID)

volume qos list
---------------

List QoS specifications

.. program:: volume qos list
.. code:: bash

    os volume qos list

volume qos set
--------------

Set QoS specification properties

.. program:: volume qos set
.. code:: bash

    os volume qos set
        [--property <key=value> [...] ]
        <qos-spec>

.. option:: --property <key=value>

    Property to add or modify for this QoS specification (repeat option to set multiple properties)

.. describe:: <qos-spec>

    QoS specification to modify (name or ID)

volume qos show
---------------

Display QoS specification details

.. program:: volume qos show
.. code:: bash

    os volume qos show
        <qos-spec>

.. describe:: <qos-spec>

   QoS specification to display (name or ID)

volume qos unset
----------------

Unset QoS specification properties

.. program:: volume qos unset
.. code:: bash

    os volume qos unset
        [--property <key>]
        <qos-spec>

.. option:: --property <key>

    Property to remove from QoS specification (repeat option to remove multiple properties)

.. describe:: <qos-spec>

    QoS specification to modify (name or ID)
