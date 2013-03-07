#!/bin/bash
# TEST HARNESS - COMPILE AND RUN

CompareResultsAndClean()
{
# Compare the results of the test harness run and clean up.

if [ -f "$TEST_DIR/O$SUBJECT.png" -a -f "$TEST_DIR/O$SUBJECT.png.ref" ]
then
  local DIFFERENCE=`diff -w -a "$TEST_DIR/O$SUBJECT.png" "$TEST_DIR/O$SUBJECT.png.ref"`

  if [ -n "$DIFFERENCE" ]
  then
     echo "-----------------------------------------------------"
     echo "TEST FAILED:- There are differences in results files."
     echo "-----------------------------------------------------"
     COMPARE_RESULTS_RETURN_VALUE=1
  else
     echo "------------"
     echo "TEST PASSED."
     echo "------------"
     COMPARE_RESULTS_RETURN_VALUE=0
     rm "$TEST_DIR/O$SUBJECT.png"
  fi
else
   COMPARE_RESULTS_RETURN_VALUE=2
     echo "------------------------------------------------------"
     echo "TEST FAILED:- Either new or old output file is missing"
     echo "------------------------------------------------------"
fi

}
