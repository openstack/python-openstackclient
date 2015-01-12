============
server image
============

A server image is a disk image created from a running server instance.  The
image is created in the Image store.

Compute v2

server image create
-------------------

Create a new disk image from a running server

.. program:: server image create
.. code:: bash

    os server image create
        [--name <image-name>]
        [--wait]
        <server>

.. option:: --name <image-name>

    Name of new image (default is server name)

.. option:: --wait

    Wait for image create to complete

.. describe:: <server>

    Server (name or ID)
