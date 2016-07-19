Testing
=======

.. role:: py(code)
   :language: py
   :class: highlight

.. _prepare-env_test:

Preparation
-----------

Virtualenv
~~~~~~~~~~

For executing the testing client a working configuration must be created first.

Please execute the following steps. 

.. include:: inc_create_venv.rst

Now, you should have a working copy of the code and a virtual environment with all required packages.

.. _testing-client_test:

The test client
---------------

.. include:: inc_testclient.rst

Please note that the local development environment will be used as webservice endpoints base url by default.
Please refer to sections :ref:`start-job-queue` and :ref:`start-dev-server`.

If you are about to develop and debug the integration of your predictions you will have three active terminal windows open:
the job queue, the development server, and one for executing the client program. As soon as you start the client program
such as ``python src/client/cli.py test`` you will see corresponding log output in all three terminals.

Please note that the local development environment will be used as webservice endpoints base url by default.
Please refer to sections :ref:`start-job-queue` and :ref:`start-dev-server`.

