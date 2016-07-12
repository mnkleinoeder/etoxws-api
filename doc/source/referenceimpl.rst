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
``etoxwsapi/settings/*.py``.

* the default development setting ``etoxwsapi/settings/dev.py`` loads the sample implementation.
* there is a etoxlab specific dev settings file ``etoxwsapi/settings/etoxlabdev.py`` which connects the etoxlab implementation class.
* in production the prod settings are loaded and the actual settings injected via a settings_local.py file.

The settings to be used are defined by an environment variable ``DJANGO_SETTINGS_MODULE``,
e.g., ``export DJANGO_SETTINGS_MODULE=etoxwsapi.settings.etoxlabdev`` for loading the etoxlab specific settings. See also :ref:`runtime-env`.
 
The package contains a sample implementation of the webservice adapter in the ``sampleimpl`` directory.
This example should demonstrate how to implement the calculation adapter.

The actual implementation should be located outside of the etoxwsapi django application and also not
stored in the same git repository. The connection can easily be done using PYTHONPATH and the settings mechanism.

Implementation
~~~~~~~~~~~~~~

Please refer to :ref:`prepare-env` in order to have a working environment.

#. create a new python module
#. set the PYTHONPATH to ``/path/to/etoxwsapi/src``
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

If you use subprocess to execute an external program the process id (pid) of the created subprocess must be
communicated to the jobobserver:::

        p = subprocess.Popen([sys.executable, calculation_program, calc_info['id'], calc_info['version'], infile, outfile]
                                                ,stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        jobobserver.report_started(p.pid)

This allows the correct cleanup of resources in case the job is killed by the ``[DELETE] /jobs/<job_id>`` method.

During execution of the calculation the progress should be reported by calling
``jobobserver.report_progress(current_record)``. This progress indication will help to present the progress
to the user in eTOXsys while a calculation is running. ``current_record`` is a integer number and refers to
the current record from the SDFile processed:::

        while True:
            retcode = p.poll() #returns None while subprocess is running
            line = p.stdout.readline()
            if (retcode is not None):
                break
            else:
                m = regex.search(line)
                if m:
                    jobobserver.report_progress(int(m.group(1)))

As soon as the calculation is completed this must be reported by ``jobobserver.report_status(retcode, errmsg)``.
The ``retcode`` is obtained from the system call if an external program is executed. Otherwise it should be ``0``
on success and ``1`` on failure, such as:::

        jobobserver.report_status(retcode, p.stderr.read())

Finally, the calculation results must be reported by using ``jobobserver.report_result(cur_rec, result)``.
This method can be called during job execution in case of processing in python or after an external program has
completed and during parsing the result file. ``cur_rec`` is the number of the current record referencing to the
``sdf_file``:::

        if retcode == 0:
            with open(outfile) as fp:
                for i, line in enumerate(fp):
                    r = line.strip().split('\t')
                    result = result_endpoint_schema.create_object()
                    result['cmp_id'] = str(i)
                    result['value'] = float(r[0])
                    result['success'] = True
                    result['AD'] = { "value": float(r[1]), "success": True, "message": "" }
                    result['RI'] = { "value": float(r[2]), "success": True, "message": "" }
                    jobobserver.report_result(i, json.dumps(result))


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

.. autoclass:: etoxwsapi.v3.jobs.tasks.JobObserver
   :members:

..   :undoc-members: etoxwsapi.v3.jobs.views.DummyLock



