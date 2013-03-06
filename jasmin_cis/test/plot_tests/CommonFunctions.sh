#!/bin/bash
# TEST HARNESS - COMPILE AND RUN

CompareResultsAndClean()
{
# Compare the results of the test harness run and clean up.
echo Output
cat "$HARNESS_DIR/O$SUBJECT.dat"

if [ -f "$HARNESS_DIR/O$SUBJECT.png" -a -f "$HARNESS_DIR/O$SUBJECT.png.ref" ]
then
  local DIFFERENCE=`diff -w -a "$HARNESS_DIR/O$SUBJECT.png" "$HARNESS_DIR/O$SUBJECT.png.ref"`

  if [ -n "$DIFFERENCE" ]
  then
     echo
     echo "------------"
     echo "Differences:"
     echo "------------"
     diff -w -a "$HARNESS_DIR/O$SUBJECT.png" "$HARNESS_DIR/O$SUBJECT.png.ref"
     COMPARE_RESULTS_RETURN_VALUE=1

     echo "-----------------------------------------------------"
     echo "TEST FAILED:- There are differences in results files."
     echo "              See above."
     echo "-----------------------------------------------------"
  else
     echo "------------"
     echo "TEST PASSED."
     echo "------------"
     COMPARE_RESULTS_RETURN_VALUE=0
  fi
else
   COMPARE_RESULTS_RETURN_VALUE=2
     echo "------------------------------------------------------"
     echo "TEST FAILED:- Either new or old output file is missing"
     echo "------------------------------------------------------"
fi

}
