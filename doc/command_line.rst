======================
Using the command line
======================

Run the following command to print help and check that it runs: ``cis --help``

The following should be displayed::

  usage: cis [-h] {plot,info,col,aggregate,subset,version} ...

  positional arguments:
    {plot,info,col,aggregate,subset,version}
      plot           Create plots
      info           Get information about a file
      col            Perform colocation
      aggregate      Perform aggregation
      subset         Perform subsetting
      eval           Evaluate a numeric expression
      stats          Perform statistical comparison of two datasets
      version        Display the CIS version number
    
  optional arguments:
    -h, --help   show this help message and exit


There are 8 commands the program can execute the moment:

  * ``plot`` which is used to plot the data
  * ``info`` which prints information about a given input file
  * ``col`` which is used to perform colocation on data
  * ``aggregate`` which is used to perform aggregation along coordinates in the data
  * ``subset`` which is used to perform subsetting of the data
  * ``eval`` which is used to evaluate a numeric expression on data
  * ``stats`` which is used to perform a statistical comparison of two datasets
  * ``version`` which is used to display the version number of CIS


If an error occurs while running any of these commands, you may wish to check the log file 'cis.log'; the default
location for this is the current user's home directory.
