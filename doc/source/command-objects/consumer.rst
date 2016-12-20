========
consumer
========

Identity v3

`Requires: OS-OAUTH1 extension`

consumer create
---------------

Create new consumer

.. program:: consumer create
.. code:: bash

    openstack consumer create
        [--description <description>]

.. option:: --description <description>

    New consumer description

consumer delete
---------------

Delete consumer(s)

.. program:: consumer delete
.. code:: bash

    openstack consumer delete
        <consumer> [<consumer> ...]

.. describe:: <consumer>

    Consumer(s) to delete

consumer list
-------------

List consumers

.. program:: consumer list
.. code:: bash

    openstack consumer list

consumer set
------------

Set consumer properties

.. program:: consumer set
.. code:: bash

    openstack consumer set
        [--description <description>]
        <consumer>

.. option:: --description <description>

    New consumer description

.. describe:: <consumer>

    Consumer to modify

consumer show
-------------

Display consumer details

.. program:: consumer show
.. code:: bash

    openstack consumer show
        <consumer>

.. _consumer_show-consumer:
.. describe:: <consumer>

    Consumer to display
