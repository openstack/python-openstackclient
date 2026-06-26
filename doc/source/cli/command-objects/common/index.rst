===============
Common Commands
===============


availability zone
-----------------

An **availability zone** is a logical partition of cloud block storage,
compute and network services.

.. autoprogram-cliff:: openstack.common
   :command: availability zone list


command
-------

Installed commands in the OSC process.

.. autoprogram-cliff:: openstack.cli
   :command: command *


complete
--------

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


configuration
-------------

.. _configuration-show:

.. autoprogram-cliff:: openstack.common
   :command: configuration show


extension
---------

Many OpenStack server APIs include API extensions that enable
additional functionality.

.. autoprogram-cliff:: openstack.common
   :command: extension *


limits
------

The Compute and Block Storage APIs have resource usage limits.

.. autoprogram-cliff:: openstack.common
   :command: limits *


module
------

Installed Python modules in the OSC process.

.. autoprogram-cliff:: openstack.cli
   :command: module *


project cleanup
---------------

Clean resources associated with a specific project based on OpenStackSDK
implementation

.. autoprogram-cliff:: openstack.common
   :command: project cleanup


quota
-----

Resource quotas appear in multiple APIs, OpenStackClient presents them as a
single object with multiple properties.

.. autoprogram-cliff:: openstack.common
   :command: quota *


versions
--------

Get a list of every version of every service in a given cloud.

.. autoprogram-cliff:: openstack.common
   :command: versions show
