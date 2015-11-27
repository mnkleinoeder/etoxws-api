Development and Testing
=======================

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

.. code-block:: bash

   etoxws-v2:~ $> mkdir etoxws
   etoxws-v2:~ $> cd etoxws
   etoxws-v2:~/etoxws $> git clone https://github.com/mnkleinoeder/etoxws-api.git
   etoxws-v2:~/etoxws $> virtualenv venv
   etoxws-v2:~/etoxws $> . venv/bin/activate
   (venv)etoxws-v2:~/etoxws $> pip install -U pip
   (venv)etoxws-v2:~/etoxws $> pip install -r etoxws-api/src/etoxwsapi/req.pip

Now, you should have a working copy of the code and a virtual environment with all required packages.

.. _runtime-env:

Runtime environment
~~~~~~~~~~~~~~~~~~~

Next, you need to create a runtime environment (``make_env.sh``):

.. code-block:: bash

   (venv)etoxws-v2:~/etoxws/etoxws-api $> cp make_env.sh.in make_env.sh

The template file ``make_env.sh.in`` contains the local settings that will work with eTOXlab.
So a copy should just create a suitable ``make_env.sh``. If you work outside of eTOXlab please change
paths in the copied file as needed.

Please also note that the ``make_env.sh`` file will contain the ``DJANGO_SETTINGS_MODULE`` variable for defining the settings
to be loaded.

Creating the development database and job queue
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In order not to interfere with the production version (see :doc:`deployment`) a development stack can easily be deployed on the same
machine.

.. code-block:: bash

   etoxws-v2:~ $> cd etoxws
   etoxws-v2:~/etoxws $> . venv/bin/activate
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

The test client
---------------

The reference implementation provides a client program for testing the webservice, both in development mode and production.

Please start a new terminal window and activate the environment created before.

.. code-block:: bash

   etoxws-v2:~ $> cd etoxws/etoxws-api/
   etoxws-v2:~/etoxws/etoxws-api $> . make_env.sh

Now, you are ready to run the command line client:

.. code-block:: bash

   (venv)etoxws-v2:~/etoxws/etoxws-api $> python src/client/cli.py --help
   usage: cli.py [-h] [-b BASEURL] [-l LOGLEV] {test,info,calc,cleanup} ...
   
   Command line interface to access the eTOX webservices (based on API v2)
   
   positional arguments:
     {test,info,calc,cleanup}
                           available subcommands
       test                test help
       calc                calculation help
       info                prints info and dir from webservice implementation
                           running at base url
       cleanup             cancels and deletes jobs
   
   optional arguments:
     -h, --help            show this help message and exit
     -b BASEURL, --base-url BASEURL
                           base url of webservice to be tested [default:
                           http://localhost:8000/etoxwsapi/v2]
     -l LOGLEV, --log-level LOGLEV
                           set verbosity level [default: WARN] (see python
                           logging module)

The client program supports subcommands for specific tasks. Please refer to the command line help.

Please note that the local development environment will be used as webservice endpoints base url by default.
Please refer to sections :ref:`start-job-queue` and :ref:`start-dev-server`.

If you are about to develop and debug the integration of your predictions you will have three active terminal windows open:
the job queue, the development server, and one for executing the client program. As soon as you start the client program
such as ``python src/client/cli.py test`` you will see corresponding log output in all three terminals.

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


