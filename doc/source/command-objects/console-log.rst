===========
console log
===========

Server console text dump

Compute v2

console log show
----------------

Show server's console output

.. program:: console log show
.. code:: bash

    os console log show
        [--lines <num-lines>]
        <server>

.. option:: --lines <num-lines>

    Number of lines to display from the end of the log (default=all)

.. describe:: <server>

    Server to show log console log (name or ID)
