=====
usage
=====

Compute v2

usage list
----------

List resource usage per project

.. program:: usage list
.. code:: bash

    os usage list
        [--start <start>]
        [--end <end>]

.. option:: --start <start>

    Usage range start date, ex 2012-01-20 (default: 4 weeks ago)

.. option:: --end <end>

    Usage range end date, ex 2012-01-20 (default: tomorrow)

usage show
----------

Show resource usage for a single project

.. program:: usage show
.. code:: bash

    os usage show
        [--project <project>]
        [--start <start>]
        [--end <end>]

.. option:: --project <project>

    Name or ID of project to show usage for

.. option:: --start <start>

    Usage range start date, ex 2012-01-20 (default: 4 weeks ago)

.. option:: --end <end>

    Usage range end date, ex 2012-01-20 (default: tomorrow)
