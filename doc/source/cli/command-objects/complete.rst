========
complete
========

The ``complete`` command is inherited from the `python-cliff` library, it can
be used to generate a bash-completion script. Currently, the command will
generate a script for bash versions 3 or 4. The bash-completion script is
printed directly to standard out.

Typical usage for this command is::

  openstack complete | sudo tee /etc/bash_completion.d/osc.bash_completion > /dev/null

It is highly recommended to install ``python-openstackclient`` from a package
(``apt-get`` or ``yum``). In some distributions the package ``bash-completion`` is shipped
as dependency, and the `openstack complete` command will be run as a post-install action,
however not every distribution include this dependency and you might need to install
``bash-completion`` package to enable autocomplete feature.

complete
--------

print bash completion command

.. program:: complete
.. code:: bash

    openstack complete
