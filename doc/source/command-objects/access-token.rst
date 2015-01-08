============
access token
============

Identity v3

`Requires: OS-OAUTH1 extension`

access token create
-------------------

Create an access token

.. program:: access token create
.. code:: bash

    os access token create
        --consumer-key <consumer-key>
        --consumer-secret <consumer-secret>
        --request-key <request-key>
        --request-secret <request-secret>
        --verifier <verifier>

.. option:: --consumer-key <consumer-key>

    Consumer key (required)

.. option:: --consumer-secret <consumer-secret>

    Consumer secret (required)

.. option:: --request-key <request-key>

    Request token to exchange for access token (required)

.. option:: --request-secret <request-secret>

    Secret associated with <request-key> (required)

.. option:: --verifier <verifier>

    Verifier associated with <request-key> (required)
