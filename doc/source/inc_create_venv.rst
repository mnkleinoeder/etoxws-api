.. code-block:: bash

   etoxws-v2:~ $> mkdir etoxws
   etoxws-v2:~ $> cd etoxws
   etoxws-v2:~/etoxws $> git clone https://github.com/mnkleinoeder/etoxws-api.git
   etoxws-v2:~/etoxws $> virtualenv venv
   etoxws-v2:~/etoxws $> . venv/bin/activate
   (venv)etoxws-v2:~/etoxws $> pip install -U pip
   (venv)etoxws-v2:~/etoxws $> pip install -r etoxws-api/src/etoxwsapi/req.pip
