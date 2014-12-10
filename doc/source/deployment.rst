Deployment of the reference implementation with Ansible
=======================================================

.. role:: py(code)
   :language: py
   :class: highlight

Introduction
------------

The new webservice implementation as released on 2014-12-01 requires several components installed and configured:

* Postgres and a database with r/w access
* Celery running as background service
* \RabbitMQ running as background service and a message queue available for celery

Also, the HTTP communication between the eTOXsys components should be encrypted, both for the online version and the in-house versions
(as requested by industry partners). 

In order to assist all modelers with the setup of the required components the reference implementation provides a
deployment procedure using Ansible (http://www.ansible.com). Also HTTPS is configured automatically by this procedure.

This page guides you through the steps required to deploy the new implementation and required components.

.. note:: This guide is written in a general manner, so the webservice implementation can be deployed on any
   CentOS/Ubuntu based system. If you want to install on a local eTOXlab virtual machine just log into eTOXlab
   as normal and work as user ``modeler`` and with host ``localhost`` as target machine.

Requirements
------------

* Check that the target machine has access to the internet
* You need root access to the target machine
* Deployment has been tested on \CentOS 6.5 and Ubuntu 12.04.

Preparation
-----------

Backup
~~~~~~

Before you start the deployment process it is recommended to make a backup of your system. For the eTOXlab virtual machine (or any virtual 
machine based system) just take a snapshot of the current state of the VM (see https://www.virtualbox.org/manual/ch01.html#snapshots).

Password-free SSH access to the target machine(s)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Make sure that you have a SSH authentication key pair in $HOME/.ssh: 

.. code-block:: bash

   ~$ ls .ssh/id_*
   .ssh/id_rsa  .ssh/id_rsa.pub

If not create authentication keys with ``ssh-keygen``. Just press enter when the program asks for setting a passphrase.

.. code-block:: bash

   ~$ ssh-keygen 

Copy the public key to the target machine(s) with ``ssh-copy-id`` (the default root password for eTOXlab is ``etoxws``). In the following
example the target is the local machine:

.. code-block:: bash

   ssh-copy-id root@localhost
   ssh root@localhost whoami

The last command should return ``root`` w/o asking for a password.

Install ansible in a virtualenv
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Run the following commands

.. code-block:: bash

   ~$ mkdir upgrade
   ~$ cd upgrade/
   ~/upgrade$ virtualenv ansible
   ~/upgrade$ . ansible/bin/activate
   (ansible)~/upgrade$ pip install ansible==1.8.1

Check that ansible is now available:

.. code-block:: bash

   (ansible)~/upgrade$ ansible --version
   ansible 1.8.1

Execution
---------

Download and configure the deployment code
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   (ansible)~/upgrade$ git clone https://github.com/mnkleinoeder/etoxws-api.git
   (ansible)~/upgrade$ cd etoxws-api/deploy
   
Now, open the file ``hosts``. You'll find ``localhost`` in the section ``[etoxlab]``. This section contains all eTOXlab instances
that the implementation should be deployed to - by default only to the local machine. You can add further host machines here,
eg., if you have a master copy of eTOXlab your are logged in currently (localhost) and a dedicated instance to host the online-version of your prediction
webservices to be used by eTOXsys.

Further, please open the file ``etoxlabvm.yml``. Check that the variables in the ``vars`` section are correct. The defaults are
suitable for a recent eTOXlab version. Otherwise, change to fit to your local setup.

Apache setup
~~~~~~~~~~~~

Per default apache is installed and a virtual host configuration is created. This virtual host will support SSL encryption.

If you deploy to a machine that has already a working virtual host configuration (including SSL support) you can comment out the ``{ role: apache }`` 
in the ``etoxlabvm.yml`` file. In that case you have to define the two variables

* ``VHOST_CONF_DIR``: location of the virtual host configuration directory.
* ``APACHE_WEBAPP_DIR``: location where the webapp code will be located (eg.: ``/srv/www/webapps``)

Running Ansible
~~~~~~~~~~~~~~~

You should be ready to run ansible:

.. code-block:: bash

   (ansible)~/upgrade/etoxws-api/deploy$ ansible-playbook site.yml -vv

Ansible should now download all required packages and bits-and-pieces and configure the task management toolchain
as well as integration with the apache webserver.

Start a web-browser and enter \https://<ip_or_hostname>/etoxwsapi/v2/info. You should see a JSON string corresponding to
the information given in the webservice implementation class.

.. note:: The SSL certificate for the virtual host is self-signed. Therefore, all browser will issue a certificate error
   when the webservice is accessed by a browser. This is not a problem for the webservice infrastructure as
   eTOXsys is aware of those self-signed certificate and can ignore the warnings when accessing.

.. note:: Ansible is designed to establish a certain configuration state as expressed in simple yaml files. Therefore, Ansible
   can be run several times safely. If the state is already reached no further changes will be performed.

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

ETOXWS_NPROC
   number of processor cores used simultanously for calculations. Jobs are queued if all nodes are occupied and new jobs are submitted.
   
   default:  

::

   ETOXWS_NPROC: 0

which means: detect the number of cores and use this number.

Testing
-------
The webapp code provides a testing tool for submitting test jobs and observing the calculation progress via the webservice
interface.

Requires the etoxws virtual env loaded.

.. code-block:: bash

   ~$ . /opt/virtualenv/etoxwsapi/bin/activate
   (etoxws-v2)~$ cd ~/upgrade/etoxws-api/src/testclient
   (etoxws-v2)~/upgrade/etoxws-api/src/testclient$ export PYTHONPATH=$PWD/..
   (etoxws-v2)~/upgrade/etoxws-api/src/testclient$ python testapp.py --help
   usage: testapp.py [-h] [-b BASEURL] [-l LOGLEV] [-t TESTFILE] [-p N] [-d N]
                     [-c N]
   
   optional arguments:
     -h, --help            show this help message and exit
     -b BASEURL, --base-url BASEURL
                           base url of webservice to be tested [default:
                           https://localhost/etoxwsapi/v2]
     -l LOGLEV, --log-level LOGLEV
                           set verbosity level [default: WARN] (see python
                           logging module)
     -t TESTFILE, --test-file TESTFILE
                           SDFile to be used for the test run. [default:
                           ~/upgrade/etoxws-api/src/testclient/tiny.sdf]
     -p N, --poll-interval N
                           poll status each N sec [default: 5]
     -d N, --duration N    stop this program after N sec [default: -1]
     -c N, --delete-after N
                           issue a DELETE request after N polls [default: -1]
   
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

Observing the log files
~~~~~~~~~~~~~~~~~~~~~~~

Log-files should be tracked:

.. code-block:: bash

   tailf /var/log/celery/etoxwsapi.log

and 

.. code-block:: bash

   tailf /var/log/httpd/etoxws-v2-ssl.com_error.log

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
   After modifications to your webservice implementation code please restart celery with ``supervisorctl restart etoxwsapi``.

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


