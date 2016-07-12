.. code-block:: bash

   etoxws-v2:~ $> mkdir etoxws
   etoxws-v2:~ $> cd etoxws
   etoxws-v2:~/etoxws $> git clone https://github.com/mnkleinoeder/etoxws-api.git
   etoxws-v2:~/etoxws $> cd etoxws-api
   etoxws-v2:~/etoxws/etoxws-api $> ./update_project.sh
   etoxws-v2:~/etoxws/etoxws-api $> cd ..
   etoxws-v2:~/etoxws $> virtualenv venv
   etoxws-v2:~/etoxws $> . venv/bin/activate
   (venv)etoxws-v2:~/etoxws $> pip install -U pip
   (venv)etoxws-v2:~/etoxws $> pip install -r pip_requirements.txt
