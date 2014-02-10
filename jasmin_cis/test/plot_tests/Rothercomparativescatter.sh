#!/bin/bash -e

SUBJECT=othercomparativescatter

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

cis plot AOT_440:${source_dir}920801_091128_Agoufou_small.lev20:color=red,itemstyle=s AOT_870:${source_dir}920801_091128_Agoufou_small.lev20 --type comparativescatter --xlabel overiddenx --ylabel overiddeny --title overiddentitle --fontsize 7 --height 5 --width 5 --xmin 0 --xmax 1 --ymin 0 --ymax 0.5 --itemwidth 400 --grid --output "O$SUBJECT.png"

end_time="$(($(date +%s)-start_time))"
echo "Time taken: ${end_time}s"
#################################
#
# Call standard function that compares the results and removes and unnecessary files
CompareResultsAndClean
# exit code is 0 for success and 1 for failure.
exit $COMPARE_RESULTS_RETURN_VALUE

######################### END OF SCRIPT ####################################
