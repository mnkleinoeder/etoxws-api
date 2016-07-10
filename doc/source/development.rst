Development
===========

.. role:: py(code)
   :language: py
   :class: highlight

.. _prepare-env:

Preparation
-----------

Source code and virtualenv
~~~~~~~~~~~~~~~~~~~~~~~~~~

For development and testing a local instance of the code and a working configuration must be created first.

Please execute the following steps. 

.. include:: inc_create_venv.rst

Now, you should have a working copy of the code and a virtual environment with all required packages.

.. _runtime-env:

Runtime environment
~~~~~~~~~~~~~~~~~~~

Next, you need to create a runtime environment (``make_env.sh``):

.. include:: inc_makeenv.rst

Creating the development database and job queue
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In order not to interfere with the production version (see :doc:`deployment`) a development stack can easily be deployed on the same
machine.

.. include:: inc_prepare_venv.rst

Finally, execute ansible (if you get an authentication error please refer to :ref:`ssh-setup`).
   
.. code-block:: bash

   (venv)etoxws-v2:~/etoxws/etoxws-api/deploy $> ansible-playbook site.yml -vv -e ETOXWS_PRODUCTION=false

This process will create a development database and job queue. 
 
Running the web application in development mode
-----------------------------------------------

The webservice implementation consists of two main components, the job queue and the http server. In production the two components are
executed as daemons (supervisor and apache/httpd). The deployment in production mode is described here: :doc:`deployment`.

During development of the adapter code between the webservice and the model execution it is recommended to run the web application in development
mode.

Please open two different terminal windows and follow the next steps. 

.. _start-job-queue:

Starting the job queue in development mode
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. note::
   Your adapter code will run in the process of the job queue. Therefore, you need to kill and restart celery after a code modification
   of the adapter code. (Ctrl-C in the terminal window and re-run ``./launch_celery.sh`` again.


In the first terminal please follow these instructions:

.. code-block:: bash

   etoxws-v2:~ $> cd etoxws/etoxws-api/
   etoxws-v2:~/etoxws/etoxws-api $> ./launch_celery.sh
   ...
   [2015-11-26 18:45:52,285: INFO/MainProcess] Connected to amqp://etoxwsapi_dev:**@localhost:5672/etoxwsapi_dev
   ...

Please note that the console output should contain the line "Connected to ..." as shown below. If otherwise an error is printed
the settings are not correct.

.. _start-dev-server:

Starting the django server in development mode
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the second terminal please follow these instructions:

.. code-block:: bash

   etoxws-v2:~ $> cd etoxws/etoxws-api/
   etoxws-v2:~/etoxws/etoxws-api $> ./launch_devserver.sh
   ...
   0 errors found
   November 26, 2015 - 18:52:07
   Django version 1.6.8, using settings 'etoxwsapi.settings.etoxlabdev'
   Starting development server at http://0.0.0.0:8000/
   Quit the server with CONTROL-C.


.. _testing-client:

The test client
---------------

.. include:: inc_testclient.rst

Please note that the local development environment will be used as webservice endpoints base url by default.
Please refer to sections :ref:`start-job-queue` and :ref:`start-dev-server`.

If you are about to develop and debug the integration of your predictions you will have three active terminal windows open:
the job queue, the development server, and one for executing the client program. As soon as you start the client program
such as ``python src/client/cli.py test`` you will see corresponding log output in all three terminals.

.. _testing-debug:

Using a debugger
~~~~~~~~~~~~~~~~

If ``ETOXWS_PRODUCTION`` is ``false`` (ie. the application runs in debug mode) a remote debugging tool is delivered and
ready to use: the PyDev remote debugger (http://pydev.org/manual_adv_remote_debugger.html).

Just set a breakpoint at an arbitrary location in your code by adding the following line of code:

Debugging on ``localhost``:

   :py:`import pydevd; pydevd.settrace()`

Debugging remotely, ie., your development machine is, e.g., ``192.168.1.236`` (the machine were your Eclipse is running and 
the PyDev debugging server has been started):

   :py:`import pydevd; pydevd.settrace("192.168.1.236")`

.. note::
   You need to restart celery after code modifications
   
   * production mode: ``supervisorctl restart etoxwsapi``.
   * dev mode: see :ref:`start-job-queue`

Please refer also to http://brianfisher.name/content/remote-debugging-python-eclipse-and-pydev.

Example
'''''''

Let us assume we want to debug the ``calculate_impl`` method in ``/home/modeler/soft/eTOXlab/ws/view2.py``. So, we start
the pydev debugger on ``192.168.1.236`` (your develpment machine) and add the settrace call to the beginning of our method.

Finally, we reload celery ``supervisorctl reload etoxwsapi`` and triggering the calculation (using the testapp.py). In Eclipse/PyDev
we should now see the code as below -- stopped at the line where the breakpoint was set.

.. code-block:: py
   :emphasize-lines: 3

   def calculate_impl(self, jobobserver, calc_info, sdf_file):   
     import pydevd; pydevd.settrace("192.168.1.236")
   
     itag  = self.my_tags[calc_info ['id']]      # -e tag for predict.py
     itype = self.my_type[calc_info ['id']]      # quant/qualit endpoint


