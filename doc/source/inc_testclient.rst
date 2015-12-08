The reference implementation provides a client program for testing the webservice, both in development mode and production.

Please start a new terminal window and activate the environment created before.

.. code-block:: bash

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

