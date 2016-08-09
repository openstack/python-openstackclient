=======================
volume transfer request
=======================

Block Storage v1, v2

volume transfer request create
------------------------------

Create volume transfer request

.. program:: volume transfer request create
.. code:: bash

    os volume transfer request create
        [--name <name>]
        <volume>

.. option:: --name <name>

    New transfer request name (default to None)

.. _volume_transfer_request_create-volume:
.. describe:: <volume>

    Volume to transfer (name or ID)

volume transfer request list
----------------------------

Lists all volume transfer requests.

.. program:: volume transfer request list
.. code:: bash

    os volume transfer request list
        --all-projects

.. option:: --all-projects

    Shows detail for all projects. Admin only.
    (defaults to False)
