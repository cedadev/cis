======================
Using the command line
======================

Run the following command to print help and check that it runs: `` $ cis --help``

The following should be displayed::

  usage: cis [-h] {plot,info,col,subset,version} ...

  positional arguments:
    {plot,info,col,subset,version}
      plot           Create plots
      info           Get information about a file
      col            Perform colocation
      subset         Perform subsetting
      version        Display the CIS version number
    
  optional arguments:
    -h, --help   show this help message and exit


There are 5 commands the program can execute the moment:

  * `` plot `` which is used to plot the data
  * `` info `` which prints information about a given input file
  * `` col `` which is used to perform colocation on data
  * `` subset `` which is used to perform subsetting of the data
  * `` version `` which is used to display the version number of CIS
