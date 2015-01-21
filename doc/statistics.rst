.. _statistics:
.. |nbsp| unicode:: 0xA0

**********
Statistics
**********

The Community Intercomparison Suite allows you to perform statistical analysis on two variables using the 'stats'
command. For example, you might wish to examine the correlation between a model data variable and actual measurements.
The 'stats' command will calculate:

#. Number of data points used in the analysis.
#. The mean and standard deviation of each dataset (separately).
#. The mean and standard deviation of the absolute difference (var2 - var1).
#. The mean and standard deviation of the relative difference ((var2 - var1) / var1).
#. The Linear Pearson correlation coefficient.
#. The Spearman Rank correlation coefficient.
#. The coefficients of linear regression (i.e. var2 = a var1 + b ), r-value, p-value and standard error.

.. note::
    Both variables used in a statistical analysis **must** be of the same shape in order to be compatible, i.e. the
    same number of points in each dimension, and of the same type (Ungridded or Gridded). This means that, for example,
    operations between different data products are unlikely to work correctly - performing a colocation or aggregation
    onto a common grid would be a good pre-processing step.

The statistics syntax looks like this::

    $ cis stats <datagroup>... [-o <outputfile>]

where:

``datagroup``
  is of the format ``<variable>...:<filename>[:product=<productname>]``. One or more
  datagroups should be given, but the total number of variables declared in all datagroups must be exactly two.

  * ``variable`` is a mandatory argument used to specify the name of the variable in the file to use. You may
    specify more than one variable to load, in which case you should separate them with commas.

  * ``filename`` is a mandatory argument specifying the file to read the variable or variables from. You may specify
    multiple filenames separated using commas; each filename should be one of:

      \1. |nbsp| a single filename - this should be the full path to the file

      \2. |nbsp| a single directory - all files in this directory will be read

      \3. |nbsp| a wildcarded filename - A filename with any wildcards compatible with the python module glob, so that \*, ? and [] can all be used. E.g., ``/path/to/my/test*file_[0-9]``.

    Note that when multiple files are specified (whether through use of commas, pointing at a directory, or wildcarding),
    then all those files must contain all of the variables in that datagroup and the files should be 'compatible' - it
    should be possible to aggregate them together using a shared dimension (in a NetCDF file this is usually the unlimited
    dimension). So selecting multiple monthly files for a model run would be OK, but selecting files from two different
    datatypes would not be OK.

  * ``productname`` is an optional argument used to specify the type of files being read. If omitted, the program will
    attempt to figure out which product to use based on the filename. See :ref:`data-products-reading` to see a list of
    available products and their file signatures.

``outputfile``
  is an optional argument specifying a file to output to. This will be automatically given a ``.nc`` extension if not
  present. This must not be the same file path as any of the input files. If not provided, then the output will not be
  saved to a file and will only be displayed on screen.