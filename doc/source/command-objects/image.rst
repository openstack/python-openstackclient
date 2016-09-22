=====
image
=====

Image v1, v2

image add project
-----------------

*Only supported for Image v2*

Associate project with image

.. program:: image add project
.. code:: bash

    os image add project
        [--project-domain <project-domain>]
        <image> <project>

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name or ID).
    This can be used in case collisions between project names exist.

.. describe:: <image>

    Image to share (name or ID).

.. describe:: <project>

    Project to associate with image (name or ID)

image create
------------

*Image v1, v2*

Create/upload an image

.. program:: image create
.. code:: bash

    os image create
        [--id <id>]
        [--store <store>]
        [--container-format <container-format>]
        [--disk-format <disk-format>]
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
        [--tag <tag> [...] ]
        [--project <project> [--project-domain <project-domain>]]
        <image-name>

.. option:: --id <id>

    Image ID to reserve

.. option:: --store <store>

    Upload image to this store

    *Image version 1 only.*

.. option:: --container-format <container-format>

    Image container format (default: bare)

.. option:: --disk-format <disk-format>

    Image disk format (default: raw)

.. option:: --size <size>

    Image size, in bytes (only used with --location and --copy-from)

    *Image version 1 only.*

.. option:: --min-disk <disk-gb>

    Minimum disk size needed to boot image, in gigabytes

.. option:: --min-ram <disk-ram>

    Minimum RAM size needed to boot image, in megabytes

.. option:: --location <image-url>

    Download image from an existing URL

    *Image version 1 only.*

.. option:: --copy-from <image-url>

    Copy image from the data store (similar to --location)

    *Image version 1 only.*

.. option:: --file <file>

    Upload image from local file

.. option:: --volume <volume>

    Create image from a volume

.. option:: --force

    Force image creation if volume is in use (only meaningful with --volume)

.. option:: --checksum <checksum>

    Image hash used for verification

    *Image version 1 only.*

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

.. option:: --tag <tag>

    Set a tag on this image (repeat for multiple values)

    .. versionadded:: 2

.. option:: --project <project>

    Set an alternate project on this image (name or ID).
    Previously known as `--owner`.

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name or ID).
    This can be used in case collisions between project names exist.

    .. versionadded:: 2

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
        [--limit <limit>]
        [--marker <marker>]

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

.. option:: --limit <limit>

    Maximum number of images to display.

.. option:: --marker <marker>

    The last image (name or ID) of the previous page. Display list of images
    after marker. Display all images if not specified.

image remove project
--------------------

*Only supported for Image v2*

Disassociate project with image

.. program:: image remove project
.. code:: bash

    os image remove remove
        [--project-domain <project-domain>]
        <image> <project>

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name or ID).
    This can be used in case collisions between project names exist.

.. describe:: <image>

    Image to unshare (name or ID).

.. describe:: <project>

    Project to disassociate with image (name or ID)

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

*Image v1, v2*

Set image properties

.. program:: image set
.. code:: bash

    os image set
        [--name <name>]
        [--min-disk <disk-gb>]
        [--min-ram <disk-ram>]
        [--container-format <container-format>]
        [--disk-format <disk-format>]
        [--size <size>]
        [--protected | --unprotected]
        [--public | --private]
        [--store <store>]
        [--location <image-url>]
        [--copy-from <image-url>]
        [--file <file>]
        [--volume <volume>]
        [--force]
        [--checksum <checksum>]
        [--stdin]
        [--property <key=value> [...] ]
        [--tag <tag> [...] ]
        [--architecture <architecture>]
        [--instance-id <instance-id>]
        [--kernel-id <kernel-id>]
        [--os-distro <os-distro>]
        [--os-version <os-version>]
        [--ramdisk-id <ramdisk-id>]
        [--activate|--deactivate]
        [--project <project> [--project-domain <project-domain>]]
        <image>

.. option:: --name <name>

    New image name

.. option:: --min-disk <disk-gb>

    Minimum disk size needed to boot image, in gigabytes

.. option:: --min-ram <disk-ram>

    Minimum RAM size needed to boot image, in megabytes

.. option:: --container-format <container-format>

    Image container format (default: bare)

.. option:: --disk-format <disk-format>

    Image disk format (default: raw)

.. option:: --size <size>

    Size of image data (in bytes)

    *Image version 1 only.*

.. option:: --protected

    Prevent image from being deleted

.. option:: --unprotected

    Allow image to be deleted (default)

.. option:: --public

    Image is accessible to the public

.. option:: --private

    Image is inaccessible to the public (default)

.. option:: --store <store>

    Upload image to this store

    *Image version 1 only.*

.. option:: --location <image-url>

    Download image from an existing URL

    *Image version 1 only.*

.. option:: --copy-from <image-url>

    Copy image from the data store (similar to --location)

    *Image version 1 only.*

.. option:: --file <file>

    Upload image from local file

    *Image version 1 only.*

.. option:: --volume <volume>

    Update image with a volume

    *Image version 1 only.*

.. option:: --force

    Force image update if volume is in use (only meaningful with --volume)

    *Image version 1 only.*

.. option:: --checksum <checksum>

    Image hash used for verification

    *Image version 1 only.*

.. option:: --stdin

    Allow to read image data from standard input

    *Image version 1 only.*

.. option:: --property <key=value>

    Set a property on this image (repeat option to set multiple properties)

    .. versionadded:: 2

.. option:: --tag <tag>

    Set a tag on this image (repeat for multiple values)

    .. versionadded:: 2

.. option:: --architecture <architecture>

    Operating system architecture

    .. versionadded:: 2

.. option:: --instance-id <instance-id>

    ID of server instance used to create this image

    .. versionadded:: 2

.. option:: --kernel-id <kernel-id>

    ID of kernel image used to boot this disk image

    .. versionadded:: 2

.. option:: --os-distro <os-distro>

    Operating system distribution name

    .. versionadded:: 2

.. option:: --os-version <os-version>

    Operating system distribution version

    .. versionadded:: 2

.. option:: --ramdisk-id <ramdisk-id>

    ID of ramdisk image used to boot this disk image

    .. versionadded:: 2

.. option:: --activate

    Activate the image.

    .. versionadded:: 2

.. option:: --deactivate

    Deactivate the image.

    .. versionadded:: 2

.. option:: --project <project>

    Set an alternate project on this image (name or ID).
    Previously known as `--owner`.

.. option:: --project-domain <project-domain>

    Domain the project belongs to (name or ID).
    This can be used in case collisions between project names exist.

    .. versionadded:: 2

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

image unset
-----------

*Only supported for Image v2*

Unset image tags or properties

.. program:: image unset
.. code:: bash

    os image set
        [--tag <tag>]
        [--property <property>]
        <image>

.. option:: --tag <tag>

    Unset a tag on this image (repeat option to unset multiple tags)

.. option:: --property <property>

    Unset a property on this image (repeat option to unset multiple properties)

.. describe:: <image>

    Image to modify (name or ID)
