====================
Identity v3 Commands
====================


access rule
-----------

Access rules are fine-grained permissions for application credentials. An access
rule comprises of a service type, a request path, and a request method. Access
rules may only be created as attributes of application credentials, but they may
be viewed and deleted independently.

.. autoprogram-cliff:: openstack.identity.v3
   :command: access rule delete

.. autoprogram-cliff:: openstack.identity.v3
   :command: access rule list

.. autoprogram-cliff:: openstack.identity.v3
   :command: access rule show


access token
------------

An **access token** is used by the Identity service's OS-OAUTH1 extension. It
is used by the **consumer** to request new Identity API tokens on behalf of the
authorizing **user**.

.. autoprogram-cliff:: openstack.identity.v3
   :command: access token create


application credential
----------------------

With application credentials, a user can grant their applications limited
access to their cloud resources. Once created, users can authenticate with an
application credential by using the ``v3applicationcredential`` auth type.

.. autoprogram-cliff:: openstack.identity.v3
   :command: application credential *


catalog
-------

A **catalog** lists OpenStack services that are available on the cloud.

.. autoprogram-cliff:: openstack.identity.v3
   :command: catalog *


consumer
--------

An **consumer** is used by the Identity service's OS-OAUTH1 extension. It
is used to create a **request token** and **access token**.

.. autoprogram-cliff:: openstack.identity.v3
   :command: consumer *


credential
----------

.. autoprogram-cliff:: openstack.identity.v3
   :command: credential *


domain
------

A **domain** is a collection of **users**, **groups**, and **projects**. Each
**group** and **project** is owned by exactly one **domain**.

.. autoprogram-cliff:: openstack.identity.v3
   :command: domain create

.. autoprogram-cliff:: openstack.identity.v3
   :command: domain delete

.. autoprogram-cliff:: openstack.identity.v3
   :command: domain list

.. autoprogram-cliff:: openstack.identity.v3
   :command: domain set

.. autoprogram-cliff:: openstack.identity.v3
   :command: domain show


ec2 credentials (Identity v3)
-----------------------------

.. autoprogram-cliff:: openstack.identity.v3
   :command: ec2 credentials *


endpoint group
--------------

A **endpoint group** is used to create groups of endpoints that then
can be used to filter the endpoints that are available to a project.

.. autoprogram-cliff:: openstack.identity.v3
   :command: endpoint group *


endpoint (Identity v3)
----------------------

.. autoprogram-cliff:: openstack.identity.v3
   :command: endpoint add project

.. autoprogram-cliff:: openstack.identity.v3
   :command: endpoint create

.. autoprogram-cliff:: openstack.identity.v3
   :command: endpoint delete

.. autoprogram-cliff:: openstack.identity.v3
   :command: endpoint list

.. autoprogram-cliff:: openstack.identity.v3
   :command: endpoint remove project

.. autoprogram-cliff:: openstack.identity.v3
   :command: endpoint set

.. autoprogram-cliff:: openstack.identity.v3
   :command: endpoint show


federation domain/project
-------------------------

.. autoprogram-cliff:: openstack.identity.v3
   :command: federation domain *

.. autoprogram-cliff:: openstack.identity.v3
   :command: federation project *


federation protocol
-------------------

A **federation protocol** is used by the Identity service's OS-FEDERATION
extension. It is used by **identity providers** and **mappings**.

.. autoprogram-cliff:: openstack.identity.v3
   :command: federation protocol *


group
-----

.. autoprogram-cliff:: openstack.identity.v3
   :command: group *


identity provider
-----------------

An **identity provider** is used by the Identity service's OS-FEDERATION
extension. It is used by **federation protocols** and **mappings**.

.. autoprogram-cliff:: openstack.identity.v3
   :command: identity provider *


implied role
------------

.. autoprogram-cliff:: openstack.identity.v3
   :command: implied role *


limit
-----

Limits are used to specify project-specific limits thresholds of resources.

.. autoprogram-cliff:: openstack.identity.v3
   :command: limit *


mapping
-------

A **mapping** is used by the Identity service's OS-FEDERATION
extension. It is used by **federation protocols** and **identity providers**.

.. autoprogram-cliff:: openstack.identity.v3
   :command: mapping *


policy
------

A **policy** is an arbitrarily serialized policy engine rule set to be consumed
by a remote service.

.. autoprogram-cliff:: openstack.identity.v3
   :command: policy *


project (Identity v3)
---------------------

.. autoprogram-cliff:: openstack.identity.v3
   :command: project *


region
------

A **region** is a general division of an OpenStack deployment. You can associate
zero or more sub-regions with a region to create a tree-like structured
hierarchy.

.. autoprogram-cliff:: openstack.identity.v3
   :command: region *


registered limit
----------------

Registered limits are used to define default limits for resources within a
deployment.

.. autoprogram-cliff:: openstack.identity.v3
   :command: registered limit *


request token
-------------

A **request token** is used by the Identity service's OS-OAUTH1 extension. It
is used by the **consumer** to request **access tokens**.

.. autoprogram-cliff:: openstack.identity.v3
   :command: request token *


role assignment
---------------

.. autoprogram-cliff:: openstack.identity.v3
   :command: role assignment list


role (Identity v3)
------------------

.. autoprogram-cliff:: openstack.identity.v3
   :command: role *


service provider
----------------

A **service provider** is used by the Identity service's OS-FEDERATION
extension. It is used by to register another OpenStack Identity service.

.. autoprogram-cliff:: openstack.identity.v3
   :command: service provider *


service (Identity v3)
---------------------

.. autoprogram-cliff:: openstack.identity.v3
   :command: service create

.. autoprogram-cliff:: openstack.identity.v3
   :command: service delete

.. autoprogram-cliff:: openstack.identity.v3
   :command: service list

.. autoprogram-cliff:: openstack.identity.v3
   :command: service show

.. autoprogram-cliff:: openstack.identity.v3
   :command: service set


token (Identity v3)
-------------------

.. autoprogram-cliff:: openstack.identity.v3
   :command: token *


trust
-----

A **trust** provide project-specific role delegation between users, with
optional impersonation. Requires the OS-TRUST extension.

.. autoprogram-cliff:: openstack.identity.v3
   :command: trust *


user (Identity v3)
------------------

.. autoprogram-cliff:: openstack.identity.v3
   :command: user *
