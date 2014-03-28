
==============
Installing CIS
==============

First, clone the git repository: ``$ git clone http://proj.badc.rl.ac.uk/git/jasmin_cis.git``

If you have admin rights, simply run the `setup.py install` script. It will check your system for dependencies but won't install them for you (installations scripts specifically for ubuntu 12 and fedora 17 are provided under the 'scripts' directory, but these come with no warranty).

If you haven't got admin rights, all is not lost! you can still install CIS by first creating a virtual environment::

  $ virtualenv CISENV -p /usr/bin/python2.7 --system-site-packages
  $ source CISENV/bin/activate


To deactivate the virtual environment, simply type ``$ deactivate``

.. todo:: Information specific to JASMIN should be moved to it's own section

Note that, on the Jasmin cluster, some ports needs to be to open to make virtualenv works with::

  $ export http_proxy=wwwcache.rl.ac.uk:8080
  $ export https_proxy=wwwcache.rl.ac.uk:8080


Then simply run the setup.py script as you normally would. Now you're ready to rock and roll!

To check that CIS is installed correctly, simply type ``cis`` from the command line and should see something like::

  (CISENV)[user@computer ~]$ cis
  usage: CIS [-h] {plot,info,col,version} ...
  CIS: error: too few arguments


Checking the version
====================

Typing ``cis version`` displays the version number, for example::

  (CISENV)[user@computer ~]$ cis version
  Using CIS version: V0R6M0 (Development)



Dependencies
============

Use the following command to check the dependencies that CIS requries to run::

  $ python setup.py checkdep
