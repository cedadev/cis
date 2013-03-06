#!/bin/bash
#
# Purpose: Run all test harnesses.

declare -a ALL_RESULTS
declare -i TEST_NUMBER
declare -i NUMBER_OF_FAILS
declare -i NUMBER_OF_INCOMPLETE

ALL_SCRIPTS=`find ./* -name 'R*.sh'`

rm -rf test_details.txt

TEST_NUMBER=0
NUMBER_OF_FAILS=0
NUMBER_OF_INCOMPLETE=0
for SCRIPT in $ALL_SCRIPTS
do

    TEST_NUMBER=$TEST_NUMBER+1
    echo "Running TEST $TEST_NUMBER : $SCRIPT"

    cd $(dirname $SCRIPT)
    ./$(basename $SCRIPT) >& TEST_OUTPUT

    ALL_RESULTS[$TEST_NUMBER]=$?

    if [ "${ALL_RESULTS[$TEST_NUMBER]}" != "0" ]
    then
      if [ "${ALL_RESULTS[$TEST_NUMBER]}" = "2" ]
      then
        NUMBER_OF_INCOMPLETE=$NUMBER_OF_INCOMPLETE+1
        cat TEST_OUTPUT
      else
        NUMBER_OF_FAILS=$NUMBER_OF_FAILS+1
        cat TEST_OUTPUT
      fi
    fi

    cat TEST_OUTPUT >> ../test_details.txt
    rm TEST_OUTPUT

done

# Now summarise results of tests

echo
echo
echo
echo "=============================================="
echo "               SUMMARY OF TESTS"
echo "=============================================="
echo

TEST_NUMBER=0
for SCRIPT in $ALL_SCRIPTS
do

    TEST_NUMBER=$TEST_NUMBER+1

    if [ "${ALL_RESULTS[$TEST_NUMBER]}" == "0" ]
    then
      echo "PASSED:         $(basename $SCRIPT)"
    elif [ "${ALL_RESULTS[$TEST_NUMBER]}" == "2" ]
    then
      echo "INCOMPLETE:     $(basename $SCRIPT)"
    else
      echo "FAILED: :-(     $(basename $SCRIPT)"
    fi

done

echo
echo "=============================================="
echo "       $TEST_NUMBER tests were run,"
echo "       $(($TEST_NUMBER-$NUMBER_OF_INCOMPLETE)) tests completed, "
echo "       $NUMBER_OF_FAILS tests failed."
echo "=============================================="
echo

