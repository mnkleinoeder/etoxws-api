Deployment of the reference implementation with Ansible
=======================================================

.. role:: py(code)
   :language: py
   :class: highlight

.. include:: inc_general_notes.rst

Introduction
------------

In order to assist all modelers with the setup of the required components the reference implementation provides a
deployment procedure using Ansible (http://www.ansible.com). Also HTTPS is configured automatically by this procedure.

This page guides you through the steps required to deploy or update the implementation and all required components.

Requirements
------------

* Check that the target machine has access to the internet
* This procedure has been designed for and carefully tested on the eTOXlab virtual machine environment 

* Please check the :ref:`deploy-appendix` for further information

Preparation
-----------

In order to execute the upgrade procedure a local instance of the code and a working configuration must be created first.

Please run the following steps. 

.. include:: inc_create_venv.rst

Now, you should be ready for executing the upgrade process as described in the next section.

Running Ansible
---------------

The upgrade process is executed by Ansible within the virtual environment as created in the previous step:

.. include:: inc_prepare_venv.rst

Finally, execute ansible (if you get an authentication error please refer to :ref:`ssh-setup`).

.. code-block:: bash

   (venv)etoxws-v2:~/etoxws/etoxws-api/deploy $> ansible-playbook site.yml -vv

Ansible should now download all required packages and bits-and-pieces and configure the task management tool-chain
as well as integration with the apache webserver.

Start a web-browser and enter \https://<ip_or_hostname>/etoxwsapi/v3/info. You should see a JSON string corresponding to
the information given in the webservice implementation class.

.. note:: The SSL certificate for the virtual host is self-signed. Therefore, all browsers will issue a certificate error
   when the webservice is accessed by a browser. This is not a problem for the webservice infrastructure as
   eTOXsys is aware of those self-signed certificate and can ignore the warnings when accessing.

.. note:: Ansible is designed to establish a certain configuration state as expressed in simple yaml files. Therefore, Ansible
   can be run several times safely. If the state is already reached no further changes will be performed.

Testing
-------

Run-time environment
~~~~~~~~~~~~~~~~~~~~

A few environment variables have to be set in order to start testing. Create a helper script as follows which will set these variables:   

.. include:: inc_makeenv.rst

The test client
~~~~~~~~~~~~~~~

.. include:: inc_testclient.rst

For instance, the next sample command will run a very basic test with your local models:

.. code-block:: bash

   (venv)etoxws-v2:~/etoxws/etoxws-api $> python src/client/cli.py -b http://localhost/etoxwsapi/v2 test


Maintainance
------------

.. note::
   The configuration files are managed by Ansible as described above. Manual edits will be overwritten
   when Ansible is executed again.

.. note::
   In this section you'll find references to a variable ``{{HOSTNAME}}``. ``{{HOSTNAME}}`` is assigned by DHCP or
   set in ``/etc/hostname``.

Linux services are maintained by the ``service`` command, eg. ``service httpd reload``. Following the service names are
documented. Please enter ``service <service name> <action>`` as root or by sudo in order to achieve a certain management
action.
 
Webserver (apache/httpd)
~~~~~~~~~~~~~~~~~~~~~~~~

Configuration files
'''''''''''''''''''

``CentOS``:
   ``/etc/httpd/conf.d/{{HOSTNAME}}.d/``
``Ubuntu``:
   ``/etc/apache2/sites-available/{{HOSTNAME}}.d/``

``/srv/www/webapps/etoxwsapi/src/etoxwsapi/settings_local.py``
   Configuration of the Django webapplication.

Service
'''''''

``CentOS``:
   service name: ``httpd``
``Ubuntu``:
   service name: ``apache2``

Log files
'''''''''
``CentOS``:
   log base dir: ``/var/log/httpd/``
``Ubuntu``:
   log base dir: ``/var/log/apache2/``

Each virtual host, both w/ or w/o SSL support will have two dedicated log file, one for stderr and one for stdout.
Filenames are derived from the virtual hostname, e.g., ``/var/log/httpd/etoxws-v2-ssl.com_error.log``.

Task queue (Celery/Supervisor)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The package used for job management and queuing, ``celery``, is controlled by a service management tool called ``supervisord``. 
On CentOS 6.x a rather old version (2.x) is available in the official software repos. Therefore, ansible is 
installing a recent version from PyPi.
On Ubuntu 12.04/14.04 the official repositories provide a reasonable recent version (3.x) and this one is intalled and used.

Configuration files
'''''''''''''''''''

``OS independent``:
   ``/etc/supervisor/conf.d/etoxwsapi.celeryd.conf``

Service
'''''''

``OS independent``:
   service name: ``supervisord``

``supervisord`` is designed to controll any kind of Linux services. The individual services are managed by
a tool called ``supervisorctl``:

``supervisorctl`` is used to control the etoxwsapi task queue:

status:
   ``supervisorctl status etoxwsapi``
restart:
   ``supervisorctl restart etoxwsapi``

For further commands: ``supervisorctl help``

Log files
'''''''''

``OS independent``:
   ``/var/log/celery/etoxwsapi.log``

All log messages from the webservice implementation (eg., :py:`jobobserver.log_info("my message")`) will appear in this log file.

Debugging
---------

For debugging please create a :doc:`development environment <testing>` and refer to these sections: :ref:`testing-client` and :ref:`testing-debug`.


Observing the log files
~~~~~~~~~~~~~~~~~~~~~~~

Log-files should be tracked:

.. code-block:: bash

   tailf /var/log/celery/etoxwsapi.log

and 

.. code-block:: bash

   tailf /var/log/httpd/etoxws-{{HOSTNAME}}-ssl_error.log # if access via https
   tailf /var/log/httpd/etoxws-{{HOSTNAME}}_error.log # if access via http


.. _deploy-appendix:

Appendix
--------

Technical information
~~~~~~~~~~~~~~~~~~~~~

The reference implementation for API version 2/3 requires several components installed and configured:

* Postgres and a database with r/w access
* Celery running as background service
* \RabbitMQ running as background service and a message queue available for celery

Also, the HTTP communication between the eTOXsys components should be encrypted, both for the online version and the in-house versions
(as requested by industry partners). 

All these components will be installed and configured by the Ansible procedure as described above.

Backup
~~~~~~

Before you start the deployment process it is recommended to make a backup of your system. For the eTOXlab virtual machine (or any virtual 
machine based system) just take a snapshot of the current state of the VM (see https://www.virtualbox.org/manual/ch01.html#snapshots).

.. _ssh-setup:

Password-free SSH access to the target machine(s)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. include:: inc_prepare_ssh.rst

Apache setup
~~~~~~~~~~~~

.. note::
   Ignore this section if you work with an eTOXlab VM!

Per default the ansible procedure ensures that Apache is installed and a virtual host configuration is created.
This virtual host will support SSL encryption.

If you deploy to a machine that has already a working virtual host configuration (including SSL support) you can comment out the ``{ role: apache }`` 
in the ``etoxlabvm.yml`` file. In that case you have to define the two variables

* ``VHOST_CONF_DIR``: location of the virtual host configuration directory.
* ``APACHE_WEBAPP_DIR``: location where the webapp code will be located (eg.: ``/srv/www/webapps``)

Ansible variables
~~~~~~~~~~~~~~~~~
The deployment can be adjusted by several variables as defined in ``deploy/roles/etoxws-server/defaults/main.yml``. Variables are redefined in
the ``vars`` section of the ``etoxlabvm.yml`` file.

.. note:: The defaults should perfectly work for eTOXlab. No need to change those variables.

The main variables are as follows:

ETOXWS_NAME
   Name of the instance. Used as default for all kind of configuration, such as DB name, username, password as well
   as baseurl (i.e., \https://<hostname>/{{ETOXWS_NAME}} and virtual env (i.e., ``/opt/virtualenv/{{ETOXWS_NAME}}``).

   default:

::
   
   ETOXWS_NAME: etoxwsapi


ETOXWS_IMPL_V2:
   yaml dict with path, package name and class name of the webservice implementation class (v2)

   default (defined in ``etoxlabvm.yml``):
   
::

   ETOXWS_IMPL_V2:
      PYPATH: "/home/modeler/soft/eTOXlab/ws/"
      PYPCK: "views2"
      PYCLASS: "WS2"

ETOXWS_IMPL_V3:
   see ETOXWS_IMPL_V2, adapt to match for V3 implementation

ETOXWS_NPROC
   number of processor cores used simultanously for calculations. Jobs are queued if all nodes are occupied and new jobs are submitted.
   
   default:  

::

   ETOXWS_NPROC: 0

which means: detect the number of cores and use this number.

