.. code-block:: bash

   etoxws-v2:~ $> mkdir -p etoxws
   etoxws-v2:~ $> cd etoxws

If you checkout the API the first time please run the following command:

.. code-block:: bash

   etoxws-v2:~/etoxws $> git clone https://github.com/mnkleinoeder/etoxws-api.git
   etoxws-v2:~/etoxws $> virtualenv venv
   etoxws-v2:~/etoxws $> . venv/bin/activate
   etoxws-v2:~/etoxws $> cd etoxws-api
   (venv)etoxws-v2:~/etoxws/etoxws-api $> pip install -U pip
   (venv)etoxws-v2:~/etoxws/etoxws-api $> pip install -r pip_requirements.txt

If you upgrade from a previous version of the API please run the following commands:

.. code-block:: bash

   etoxws-v2:~/etoxws $> cd etoxws-api
   etoxws-v2:~/etoxws/etoxws-api $> git pull
   etoxws-v2:~/etoxws/etoxws-api $> cd ..
   etoxws-v2:~/etoxws $> . venv/bin/activate
   etoxws-v2:~/etoxws $> cd etoxws-api
   (venv)etoxws-v2:~/etoxws/etoxws-api $> pip install -U pip
   (venv)etoxws-v2:~/etoxws/etoxws-api $> pip install -r pip_requirements.txt

Finally, the following command has to be executed:

.. code-block:: bash

   etoxws-v2:~/etoxws/etoxws-api $> ./update_project.sh
