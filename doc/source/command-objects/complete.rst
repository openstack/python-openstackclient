========
complete
========

The ``complete`` command is inherited from the `python-cliff` library, it can
be used to generate a bash-completion script. Currently, the command will
generate a script for bash versions 3 or 4. The bash-completion script is
printed directly to standard out.

Typical usage for this command is::

  openstack complete | sudo tee /etc/bash_completion.d/osc.bash_completion > /dev/null

If installing ``python-openstackclient`` from a package (``apt-get`` or ``yum``),
then this command will likely be run for you.

complete
--------

print bash completion command

.. program:: complete
.. code:: bash

    os complete
