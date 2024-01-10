#!/bin/bash

###########################################################################################
# This script is a wrapper around the `smartctl` command
# It runs a SMART test on a disk -> waits for the test to finish -> prints the results
# This script is intended to be run by the `smart-runner.py` script
###########################################################################################

set -e

function print_usage() {
  echo "Usage: $0 [short|long] [disk_or_mount]"
}

function run_smart_test_on_disk() {
  local TEST=$1
  local DISK=$2

  echo "Starting $TEST SMART test for $DISK..."

  smartctl --test="$TEST" --log=error --log=selftest "$DISK" > /dev/null 2>&1
}

function wait_for_test_to_finish() {
  local TEST=$1
  local DISK=$2
  local MINS_WAITED=0

  while true; do
    if smartctl --all "$DISK" | grep -q "Self-test routine in progress"; then

      # print every 15 minutes
      if [ $((MINS_WAITED % 15)) -eq 0 ]; then
        echo "Waiting for $TEST SMART test to finish for $DISK..."
      fi

      sleep 60
      MINS_WAITED=$((MINS_WAITED + 1))
    else
      break
    fi
  done
}

function get_test_result() {
  local TEST=$1
  local DISK=$2
  local FULL_OUTPUT=$(smartctl --all "$DISK")
  local TEST_RESULT=$(echo "$FULL_OUTPUT" | grep "test result" | awk '{print $NF}')
  local RETURN_CODE

  if [ "$TEST_RESULT" != "PASSED" ]; then
    echo "$TEST SMART test finished for $DISK with status $TEST_RESULT" >&2
    RETURN_CODE=1
  else
    echo "$TEST test finished for $DISK with status $TEST_RESULT"
    RETURN_CODE=0
  fi

  echo ""
  echo "$FULL_OUTPUT"
  echo ""

  return $RETURN_CODE
}

function get_disk() {
  local MOUNT=$1

  if [ -e "$MOUNT" ]; then
    df --output=source "$MOUNT" | awk 'NR==2 {print $1}'
  else
    echo ""
  fi
}

function main() {
  local TEST=$1
  local DISKORMOUNT=$2

  if [ "$TEST" != "short" ] && [ "$TEST" != "long" ]; then
    echo "Unrecognised test type \"$TEST\", exiting..." >&2
    exit 1
  fi

  if [ ! "$DISKORMOUNT" ]; then
    echo "No disk or mount specified, exiting..." >&2
    exit 0
  fi

  DISK=$(get_disk "$DISKORMOUNT")

  if [ ! "$DISK" ]; then
    echo "No disk found for $DISKORMOUNT, exiting..." >&2
    exit 1
  elif [ "$DISKORMOUNT" != "$DISK" ]; then
    echo "$DISKORMOUNT resolved to disk $DISK"
  fi

  run_smart_test_on_disk "$TEST" "$DISK"
  wait_for_test_to_finish "$TEST" "$DISK"
  get_test_result "$TEST" "$DISK"

  RETURN_CODE=$?

  exit $RETURN_CODE
}

if [ $# -eq 0 ]; then
  print_usage
  exit 1
fi

main "$@"
