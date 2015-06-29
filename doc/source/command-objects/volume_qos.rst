==========
volume qos
==========

volume v1, v2

volume qos associate
--------------------

Associate a QoS specification to a volume type

.. program:: volume qos associate
.. code:: bash

    os volume qos associate
        <qos-specs>
        <volume-type>

.. describe:: <qos-specs>

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
         <qos-specs>

.. describe:: <qos-specs>

    QoS specification to delete (name or ID)

volume qos disassociate
-----------------------

Disassociate a QoS specification from a volume type

.. program:: volume qos disassoiate
.. code:: bash

    os volume qos disassociate
        --volume-type <volume-type> | --all
        <qos-specs>

.. option:: --volume-type <volume-type>

    Volume type to disassociate the QoS from (name or ID)

.. option:: --all

    Disassociate the QoS from every volume type

.. describe:: <qos-specs>

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
        <qos-specs>

.. option:: --property <key=value>

    Property to add or modify for this QoS specification (repeat option to set multiple properties)

.. describe:: <qos-specs>

    QoS specification to modify (name or ID)

volume qos show
---------------

Display QoS specification details

.. program:: volume qos show
.. code:: bash

    os volume qos show
        <qos-specs>

.. describe:: <qos-specs>

   QoS specification to display (name or ID)

volume qos unset
----------------

Unset QoS specification properties

.. program:: volume qos unset
.. code:: bash

    os volume qos unset
        [--property <key>]
        <qos-specs>

.. option:: --property <key>

    Property to remove from QoS specification (repeat option to remove multiple properties)

.. describe:: <qos-specs>

    QoS specification to modify (name or ID)
