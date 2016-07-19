Make sure that you have a SSH authentication key pair in $HOME/.ssh: 

.. code-block:: bash

   ~$ ls .ssh/id_*
   .ssh/id_rsa  .ssh/id_rsa.pub

If not create certificates with ``ssh-keygen``. Just press enter when the program asks for setting a passphrase.

.. code-block:: bash

   ~$ ssh-keygen 

Copy the public key to the target machine(s) with ``ssh-copy-id`` (the default root password for eTOXlab is ``etoxws``). In the following
example the target is the local machine:

.. code-block:: bash

   ssh-copy-id root@localhost
   ssh root@localhost whoami

The last command should return ``root`` w/o asking for a password.

