=========
container
=========

Object Storage v1

container create
----------------

Create new container

.. program:: container create
.. code:: bash

    os container create
        <container-name> [<container-name> ...]

.. describe:: <container-name>

    New container name(s)

container delete
----------------

Delete container

.. program:: container delete
.. code:: bash

    os container delete
        [-r] | [--recursive]
        <container> [<container> ...]

.. option:: --recursive, -r

    Recursively delete objects in container before container delete

.. describe:: <container>

    Container(s) to delete

container list
--------------

List containers

.. program:: container list
.. code:: bash

    os container list
        [--prefix <prefix>]
        [--marker <marker>]
        [--end-marker <end-marker>]
        [--limit <limit>]
        [--long]
        [--all]

.. option:: --prefix <prefix>

    Filter list using <prefix>

.. option:: --marker <marker>

    Anchor for paging

.. option:: --end-marker <end-marker>

    End anchor for paging

.. option:: --limit <limit>

    Limit the number of containers returned

.. option:: --long

    List additional fields in output

.. option:: --all

    List all containers (default is 10000)

container save
--------------

Save container contents locally

.. program:: container save
.. code:: bash

    os container save
        <container>

.. describe:: <container>

    Container to save

container set
-------------

Set container properties

.. program:: container set
.. code:: bash

    os container set
        [--property <key=value> [...] ]
        <container>

.. option:: --property <key=value>

    Set a property on this container (repeat option to set multiple properties)

.. describe:: <container>

    Container to modify

container show
--------------

Display container details

.. program:: container show
.. code:: bash

    os container show
        <container>

.. describe:: <container>

    Container to display

container unset
---------------

Unset container properties

.. program:: container unset
.. code:: bash

    os container unset
        [--property <key>]
        <container>

.. option:: --property <key>

    Property to remove from container (repeat option to remove multiple properties)

.. describe:: <container>

    Container to modify
