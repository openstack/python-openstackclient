======
limits
======

The Compute and Volume APIs have resource usage limits.

limits show
-----------

Show compute and volume limits

.. program:: limits show
.. code:: bash

    os limits show
        --absolute [--reserved] | --rate

.. option:: --absolute

    Show absolute limits

.. option:: --rate

    Show rate limits

.. option:: --reserved

    Include reservations count [only valid with :option:`--absolute`]
