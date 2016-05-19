============
server image
============

A server image is a disk image created from a running server instance.  The
image is created in the Image store.

Compute v2

server image create
-------------------

Create a new server disk image from an existing server

.. program:: server image create
.. code:: bash

    os server image create
        [--name <image-name>]
        [--wait]
        <server>

.. option:: --name <image-name>

    Name of new disk image (default: server name)

.. option:: --wait

    Wait for operation to complete

.. describe:: <server>

    Server to create image (name or ID)
