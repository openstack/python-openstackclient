=======================
volume transfer request
=======================

Block Storage v1, v2

volume transfer request accept
------------------------------

Accept volume transfer request

.. program:: volume transfer request accept
.. code:: bash

    os volume transfer request accept
        <transfer-request>
        <auth-key>

.. _volume_transfer_request_accept:
.. describe:: <transfer-request>

    Volume transfer request to accept (name or ID)

.. describe:: <auth-key>

    Authentication key of transfer request

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

volume transfer request delete
------------------------------

Delete volume transfer request(s)

.. program:: volume transfer request delete
.. code:: bash

    os volume transfer request delete
        <transfer-request> [<transfer-request> ...]

.. _volume_transfer_request_delete-transfer-request:
.. describe:: <transfer-request>

    Volume transfer request(s) to delete (name or ID)

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

volume transfer request show
----------------------------

Show volume transfer request details

.. program:: volume transfer request show
.. code:: bash

    os volume transfer request show
        <transfer-request>

.. _volume_transfer_request_show-transfer-request:
.. describe:: <transfer-request>

    Volume transfer request to display (name or ID)
