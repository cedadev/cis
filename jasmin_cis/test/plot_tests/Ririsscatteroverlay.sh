#!/bin/bash -e

SUBJECT=irisscatteroverlay

#########################################
# Code in this section not to be modified.
#########################################
# The current directory.
TEST_DIR=`pwd`
# The full path of the directory containing the common build and run scripts.
ROOT_TEST_DIR="${TEST_DIR}/.."

source_dir="${ROOT_TEST_DIR}/test_files/"

rm -f "O$SUBJECT.png"
# load in the standard functions
. "$TEST_DIR/CommonFunctions.sh"
########################################

#################################
# Place the execution lines below.
#
#################################
start_time="$(date +%s)"

cis plot rain:${source_dir}xglnwa.pm.k8dec-k9nov.col.tm.nc snow:${source_dir}xglnwa.pm.k8dec-k9nov.col.tm.nc:itemstyle=^,label=snowlabel --type scatteroverlay --xlabel overiddenxlabel --height 10 --width 12 --xmin 0 --xmax 200 --xstep 10 --cbarorient horizontal --ymin 0 --ymax 90 --vmin 0 --cbarorient horizontal --output "O$SUBJECT.png"

end_time="$(($(date +%s)-start_time))"
echo "Time taken: ${end_time}s"
#################################
#
# Call standard function that compares the results and removes and unnecessary files
CompareResultsAndClean
# exit code is 0 for success and 1 for failure.
exit $COMPARE_RESULTS_RETURN_VALUE

######################### END OF SCRIPT ####################################
