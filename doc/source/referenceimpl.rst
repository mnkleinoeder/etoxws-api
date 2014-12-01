The reference implementation
============================

Introduction
------------

The eTOXsys prediction webservice API v2 is available as Django application.
The idea is to have a ready-to-use webapplication that can easily be integrated with existing
prediction workflows such as eTOXlab. Only a few methods have to be implemented in order to
result in a API v2 compliant webservice application.

Installation
------------

The source code is available on \GitHub: https://github.com/mnkleinoeder/etoxws-api.git

Several components are required to run the reference implementation

* Django 1.6.* (Django 1.7 is not supported on CentOS 6 b/c of old Python version 2.6.*)
* A DBMS such as MySQL, MariaDB, or Postgres
* Celery running as background service
* RabbitMQ running as background service

The database backend and the rabbitmq messaging queue are configured in
``/path/to/etoxwsapi/src/etoxwsapi/settings_local.py``. A sample configuration is given in the corresponding
``settings_local.py.in`` file.

It is not required to do this setup manually. The entire process of setting up the environment, the
webapplication and the apache webserver configuration can be performed automatically as documented here:
:doc:`deployment`.

Integration of prediction workflows
-----------------------------------

Adapter to calculation module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The django application only handles the aspects related to the API, ie. definition of JSON-Schemas for
data exchange and the configuration of the URLs.

For the actual calculations an implementation class is required. The django app uses an interface class
located in the module ``etoxwsapi.v2.wsbase``.  This class defines abstract methods required to implement
the  webservice. These methods have to be implemented by the adapter (i.e., a subclass of
``etoxwsapi.v2.wsbase.WebserviceImplementationBase``).

The connection between the django app and the calculation adapter is made in the file
``etoxwsapi/settings_local.py``. This file is shipped as template (settings_local.py.in).
Please rename to settings_local.py and set the implementation class(es) in that file.

Furthermore, the settings_local.py file contains a variable for controlling if the django app implements
synchronous or asynchronous execution of jobs. In the production version the webservice should be
asynchronous. During development and debugging a synchronous execution is favorable.

The package contains a sample implementation of the webservice adapter in the ``sampleimpl`` directory.
This example should demonstrate how to implement the calculation adapter.

The actual implementation should be located outside of the etoxwsapi django application and also not
stored in the same git repository. The connection can easily be done using PYTHONPATH and
``settings_local.py``.

Implementation
~~~~~~~~~~~~~~

#. create a new python module
#. set the PYTHONPATH to ``/path/to/etoxwsapi/src``
#. import required classes and packages from etoxwsapi::

      from etoxwsapi.v2 import schema
      from etoxwsapi.v2.wsbase import WebserviceImplementationBase

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

During execution of the calculation the progress should be reported by calling
``jobobserver.report_progress(current_record)``. This progress indication will be presented to the user in eTOXsys
while a calculation is running. ``current_record`` is a integer number and refers to the current record from the
SDFile processed.

As soon as the calculation is completed this must be reported by ``jobobserver.report_status(retcode, errmsg)``.
The ``retcode`` is obtained from the system call if an external program is executed. Otherwise it should be ``0``
on success and ``1`` on failure.

Finally, the calculation results must be reported by using ``jobobserver.report_result(cur_rec, result)``.
This method can be called during job execution in case of processing in python or after an external program has
completed and during parsing the result file. ``cur_rec`` is the number of the current record referencing to the
``sdf_file``.

Schema management
~~~~~~~~~~~~~~~~~

All schemas are stored in ``etoxwsapi/v2/schema`` as python modules.
The python representation of the schemas can be obtained using ``schema.get(name)``.
A schema object can be used to create new self validating instances of a schema
(ie, python representations of the JSON structure).::

   ws_info_schema = schema.get('ws_info')
   ws_info = ws_info_schema.create_object(provider="test", admin_email="test@example.com")
   ws_info_json = ws.to_json()

Testing the implementation
~~~~~~~~~~~~~~~~~~~~~~~~~~

A python application is available in the ``src/testclient`` directory as a test client.

First, the webservice has to be started (``python manage.py runserver``, see above). The test client
can now be executed with ``python testapp.py``.

Class documentation
-------------------

.. automodule:: etoxwsapi.v2.wsbase
   :members:

..   :undoc-members: etoxwsapi.v2.jobs.views.DummyLock



