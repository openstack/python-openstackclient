======
image
======

Image v1, v2

image create
------------

*Only supported for Image v1*

Create/upload an image

.. program:: image create
.. code:: bash

    os image create
        [--id <id>]
        [--store <store>]
        [--container-format <container-format>]
        [--disk-format <disk-format>]
        [--owner <project>]
        [--size <size>]
        [--min-disk <disk-gb>]
        [--min-ram <ram-mb>]
        [--location <image-url>]
        [--copy-from <image-url>]
        [--file <file>]
        [--volume <volume>]
        [--force]
        [--checksum <checksum>]
        [--protected | --unprotected]
        [--public | --private]
        [--property <key=value> [...] ]
        <image-name>

.. option:: --id <id>

    Image ID to reserve

.. option:: --store <store>

    Upload image to this store

.. option:: --container-format <container-format>

    Image container format (default: bare)

.. option:: --disk-format <disk-format>

    Image disk format (default: raw)

.. option:: --owner <project>

    Image owner project name or ID

.. option:: --size <size>

    Image size, in bytes (only used with --location and --copy-from)

.. option:: --min-disk <disk-gb>

    Minimum disk size needed to boot image, in gigabytes

.. option:: --min-ram <disk-ram>

    Minimum RAM size needed to boot image, in megabytes

.. option:: --location <image-url>

    Download image from an existing URL

.. option:: --copy-from <image-url>

    Copy image from the data store (similar to --location)

.. option:: --file <file>

    Upload image from local file

.. option:: --volume <volume>

    Create image from a volume

.. option:: --force

    Force image creation if volume is in use (only meaningful with --volume)

.. option:: --checksum <checksum>

    Image hash used for verification

.. option:: --protected

    Prevent image from being deleted

.. option:: --unprotected

    Allow image to be deleted (default)

.. option:: --public

    Image is accessible to the public

.. option:: --private

    Image is inaccessible to the public (default)

.. option:: --property <key=value>

    Set a property on this image (repeat for multiple values)

.. describe:: <image-name>

    New image name

image delete
------------

Delete image(s)

.. program:: image delete
.. code:: bash

    os image delete
        <image>

.. describe:: <image>

    Image(s) to delete (name or ID)

image list
----------

List available images

.. program:: image list
.. code:: bash

    os image list
        [--public | --private | --shared]
        [--property <key=value>]
        [--long]
        [--sort <key>[:<direction>]]

.. option:: --public

    List only public images

.. option:: --private

    List only private images

.. option:: --shared

    List only shared images

    *Image version 2 only.*

.. option:: --property <key=value>

    Filter output based on property

.. option:: --long

    List additional fields in output

.. option:: --sort <key>[:<direction>]

    Sort output by selected keys and directions(asc or desc) (default: asc),
    multiple keys and directions can be specified separated by comma

image save
----------

Save an image locally

.. program:: image save
.. code:: bash

    os image save
        --file <filename>
        <image>

.. option:: --file <filename>

    Downloaded image save filename (default: stdout)

.. describe:: <image>

    Image to save (name or ID)

image set
---------

*Only supported for Image v1*

Set image properties

.. program:: image set
.. code:: bash

    os image set
        [--name <name>]
        [--owner <project>]
        [--min-disk <disk-gb>]
        [--min-ram <disk-ram>]
        [--protected | --unprotected]
        [--public | --private]
        [--property <key=value> [...] ]
        <image>

.. option:: --name <name>

    New image name

.. option:: --owner <project>

    New image owner project (name or ID)

.. option:: --min-disk <disk-gb>

    Minimum disk size needed to boot image, in gigabytes

.. option:: --min-ram <disk-ram>

    Minimum RAM size needed to boot image, in megabytes

.. option:: --protected

    Prevent image from being deleted

.. option:: --unprotected

    Allow image to be deleted (default)

.. option:: --public

    Image is accessible to the public

.. option:: --private

    Image is inaccessible to the public (default)

.. option:: --property <key=value>

    Set a property on this image (repeat for multiple values)

.. describe:: <image>

    Image to modify (name or ID)

image show
----------

Display image details

.. program:: image show
.. code:: bash

    os image show
        <image>

.. describe:: <image>

    Image to display (name or ID)
