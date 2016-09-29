The reference implementation
============================

Introduction
------------

The eTOXsys prediction webservice API v3 is available as Django application.
This is a ready-to-use webapplication that can easily be integrated with existing
prediction workflows such as eTOXlab. Only a few methods have to be implemented in order to
result in a API v3 compliant webservice application.

Installation
------------

The source code is available on \GitHub: https://github.com/mnkleinoeder/etoxws-api.git

Several components are required to run the reference implementation

* Django 1.6.* (Django 1.7 is not supported on CentOS 6 b/c of old Python version 2.6.*)
* A DBMS such as MySQL, MariaDB, or Postgres
* Celery running as background service
* RabbitMQ running as background service

It is not required to do the setup manually. The entire process of setting up the environment, the
webapplication and the apache webserver configuration can be performed automatically as documented here:
:doc:`deployment`.

Integration of prediction workflows
-----------------------------------

Adapter to calculation module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The django application only handles the aspects related to the API, ie. definition of JSON-Schemas for
data exchange and the configuration of the URLs.

For the actual calculations an implementation class is required. The django app uses an interface class
located in the module ``etoxwsapi.v3.wsbase``.  This class defines abstract methods required to implement
the  webservice. These methods have to be implemented by the adapter (i.e., a subclass of
``etoxwsapi.v3.wsbase.WebserviceImplementationBase``).

The connection between the django app and the calculation adapter is made via the Django settings mechanism
``etoxwsapi/settings/``.

Local settings are defined in a file ``etoxwsapi/settings/settings_local.py``. A template file is provided
``etoxwsapi/settings/settings_local.py.in`` which contains usable settings for eTOXlab in development mode.
This file needs only to be copied in order to obtain a working development environment.

The production settings for the WSGI/Apache settings are automatically deployed during the deployment (:doc:`deployment`).

The package contains a sample implementation of the webservice adapter in the ``sampleimpl`` directory.
This example should demonstrate how to implement the calculation adapter.

The actual implementation should be located outside of the etoxwsapi django application and also not
stored in the same git repository. The connection can easily be done using PYTHONPATH and the settings mechanism.

Implementation
~~~~~~~~~~~~~~

Please refer to :ref:`prepare-env` in order to have a working environment.

#. create a new python module
#. set the PYTHONPATH to ``/path/to/etoxws-api/src``
#. import required classes and packages from etoxwsapi::

      from etoxwsapi.v3 import schema
      from etoxwsapi.v3.wsbase import WebserviceImplementationBase

#. derive an implementation class from ``WebserviceImplementationBase``
#. implement the methods ``info_impl``, ``dir_impl``, and ``calculate_impl``

Please refer to the sample implementation for details (``src/etoxwsapi/sampleimpl``).

The ``calculate_impl`` must be overwritten with the actual implementation of the calculation.
This method will be described in more detail:

calculate_impl(self, jobobserver, calc_info, sdf_file)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:jobobserver: this object is used to communicate with the calling class that implements the job management.
:calc_info: represents the actual calculation request (see `calc_info schema`_)
:sdf_file: the string representation of the incoming SDFile

.. _`calc_info schema`: apispec.html#calculation-info

Please refer to the file ``sampleimpl/ws_impl_v2.py``. This file provides a ``calculation_impl`` sample implementation.

Please note the error management: the entire prediction execution part is wrapped in a try/except block. Furthermore, the
cleanup of temporary files is done in a ``finally`` block - so it will always be executed.

Finally, please note the execution of ``subprocess.Popen``. The ``stderr`` argument is set to a file object. It turned out that a pipe
caused serious problems when to much error output was generated. It is highly recommended to follow the pattern as shown in the sample
implementation.

Schema management
~~~~~~~~~~~~~~~~~

All schemas are stored in ``etoxwsapi/v3/schema`` as python modules.
The python representation of the schemas can be obtained using ``schema.get(name)``.
A schema object can be used to create new self validating instances of a schema
(ie, python representations of the JSON structure).::

   ws_info_schema = schema.get('ws_info')
   ws_info = ws_info_schema.create_object(provider="test", admin_email="test@example.com")
   ws_info_json = ws.to_json()

Testing the implementation
~~~~~~~~~~~~~~~~~~~~~~~~~~

During installation it is recommended to start the components in development mode as described here:
:doc:`testing`.

Class documentation
-------------------

.. automodule:: etoxwsapi.v3.wsbase
   :members:

.. autoclass:: etoxwsapi.v3.jobs_v3.tasks.JobObserver
   :members:

..   :undoc-members: etoxwsapi.v3.jobs.views.DummyLock



