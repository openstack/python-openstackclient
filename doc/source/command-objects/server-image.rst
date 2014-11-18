============
server image
============

A server image is a disk image created from a running server instance.  The
image is created in the Image store.

server image create
-------------------

Create a new disk image from a running server

.. code:: bash

    os server image create
        [--name <image-name>]
        [--wait]
        <server>

:option:`--name` <image-name>
    Name of new image (default is server name)

:option:`--wait`
    Wait for image create to complete

:option:`<server>`
    Server (name or ID)
