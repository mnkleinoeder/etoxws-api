The reference implementation provides a client program for testing the webservice, both in development mode and production.

Please start a new terminal window and activate the environment created before.

.. code-block:: bash

   etoxws-v2:~/etoxws/etoxws-api $> . make_env.sh

Now, you are ready to run the command line client:

.. code-block:: bash

   (venv)etoxws-v2:~/etoxws/etoxws-api $> python src/client/cli.py --help
   usage: cli.py [-h] [-b BASEURL] [-l LOGLEV] [-v]
                 {test,test-long,calc,inspect-jobs,etoxvault-check,info,kill} ...
   
               Command line interface to access the eTOX webservices (v2 and v3 are supported)
               running calculation can be stopped anytime by Ctrl-C.
   
   positional arguments:
     {test,test-long,calc,inspect-jobs,etoxvault-check,info,kill}
                           Available subcommands:
       test                Run models with a tiny dataset of three simple
                           molecules (./tiny.sdf). This is useful only while
                           developing and debugging.
       test-long           Run models with an extensive test-suite (i.e., all
                           sdf-files in testdata/ subdir). This test must pass
                           before a VM is accepted for deployment.
       calc                Run calculations of a given webservice in order to
                           obtain an SDFile with results.
       inspect-jobs        Inspect all jobs of a given webservice.
       etoxvault-check     Check if a eTOXvault record is available for all
                           models.
       info                Prints info and dir from webservice implementation
                           running at base url.
       kill                Cancels and deletes all running jobs. Jobs will not be
                           erased from the webservice.
   
   optional arguments:
     -h, --help            show this help message and exit
     -b BASEURL, --base-url BASEURL
                           base url of webservice to be tested [default:
                           http://localhost:8100/etoxwsapi/v3]
     -l LOGLEV, --log-level LOGLEV
                           set verbosity level [default: WARN] (see python
                           logging module)
     -v, --verbose         write output sequentially to the terminal

The client program supports subcommands for specific tasks. Please refer to the command line help.

