.. code-block:: bash

   (venv)etoxws-v2:~/etoxws $> cd ~/etoxws/etoxws-api/deploy

Check for the file ``hosts``. If it does not exist create it by copying from ``hosts.in``. By default localhost is listed which
is sufficient if you work within eTOXlab.
 
.. code-block:: bash

   (venv)etoxws-v2:~/etoxws/etoxws-api/deploy $> cp hosts.in hosts
   (venv)etoxws-v2:~/etoxws/etoxws-api/deploy $> vi hosts # adapt as needed
