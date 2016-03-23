======
limits
======

The Compute and Block Storage APIs have resource usage limits.

Compute v2, Block Storage v1

limits show
-----------

Show compute and block storage limits

.. program:: limits show
.. code:: bash

    os limits show
        --absolute [--reserved] | --rate
        [--project <project>]
        [--domain <domain>]

.. option:: --absolute

    Show absolute limits

.. option:: --rate

    Show rate limits

.. option:: --reserved

    Include reservations count [only valid with :option:`--absolute`]

.. option:: --project <project>

    Show limits for a specific project (name or ID) [only valid with --absolute]

.. option:: --domain <domain>

    Domain the project belongs to (name or ID) [only valid with --absolute]
