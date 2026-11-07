#!/bin/bash

###########################################################################################
# This script is a wrapper around the `smartctl` command
# It runs a SMART test on a disk -> waits for the test to finish -> prints the results
# This script is intended to be run by the `smart-runner.py` script
###########################################################################################

set -u

# smartctl exit status bits (see `man smartctl`, EXIT STATUS)
SMARTCTL_DEVICE_ERROR=3        # bit 0: command line error, bit 1: device open failed
SMARTCTL_COMMAND_FAILED=7      # bits 0-1, plus bit 2: SMART command to the disk failed
SMARTCTL_DISK_FAILING=8        # bit 3: overall-health self-assessment is FAILING
SMARTCTL_PREFAIL_THRESHOLD=16  # bit 4: pre-fail attributes at or below threshold

function print_usage() {
  echo "Usage: $0 [short|long] [disk_or_mount]"
}

function fail() {
  echo "$1" >&2
  exit 1
}

# runs smartctl and only treats the given exit status bits as a failure
function smartctl_checked() {
  local FAILURE_BITS=$1
  shift
  local OUTPUT
  local STATUS

  OUTPUT=$(smartctl "$@" 2>&1)
  STATUS=$?

  if [ $((STATUS & FAILURE_BITS)) -ne 0 ]; then
    echo "$OUTPUT" >&2
    return 1
  fi

  echo "$OUTPUT"
}

function resolve_disk() {
  local TARGET=$1
  local SOURCE

  if [ -b "$TARGET" ]; then
    SOURCE=$TARGET
  else
    SOURCE=$(findmnt --noheadings --first-only --output SOURCE --mountpoint "$TARGET") || return 1
  fi

  lsblk --list --noheadings --inverse --paths --output NAME,TYPE "$SOURCE" 2> /dev/null \
    | awk '$2 == "disk" { print $1; exit }'
}

function self_test_in_progress() {
  local DISK=$1
  local CAPABILITIES

  CAPABILITIES=$(smartctl_checked $SMARTCTL_COMMAND_FAILED --capabilities "$DISK") \
    || fail "Failed to read SMART self-test status for $DISK"

  echo "$CAPABILITIES" | grep -q "Self-test routine in progress"
}

function wait_for_test_to_finish() {
  local DISK=$1
  local MINS_WAITED=0

  while self_test_in_progress "$DISK"; do

    # print every 15 minutes
    if [ $((MINS_WAITED % 15)) -eq 0 ]; then
      echo "Waiting for SMART self-test to finish for $DISK..."
    fi

    sleep 60
    MINS_WAITED=$((MINS_WAITED + 1))
  done
}

function read_self_test_log() {
  local DISK=$1

  smartctl_checked $SMARTCTL_COMMAND_FAILED --log=selftest "$DISK" \
    || fail "Failed to read SMART self-test log for $DISK"
}

function report_test_result() {
  local TEST=$1
  local DISK=$2
  local SELF_TEST_LOG_BEFORE=$3
  local SELF_TEST_LOG
  local NEWEST_RESULT
  local FULL_OUTPUT
  local STATUS

  SELF_TEST_LOG=$(read_self_test_log "$DISK") || exit 1
  NEWEST_RESULT=$(echo "$SELF_TEST_LOG" | grep -m 1 "^# *1 ")

  FULL_OUTPUT=$(smartctl --all "$DISK" 2>&1)
  STATUS=$?

  echo ""
  echo "$FULL_OUTPUT"
  echo ""

  if [ $((STATUS & SMARTCTL_DEVICE_ERROR)) -ne 0 ]; then
    fail "Failed to read SMART data for $DISK"
  fi

  if [ "$SELF_TEST_LOG" == "$SELF_TEST_LOG_BEFORE" ]; then
    fail "$TEST SMART test for $DISK did not record a result in the self-test log"
  fi

  if [[ "$NEWEST_RESULT" != *"Completed without error"* ]]; then
    fail "$TEST SMART test failed for $DISK: $NEWEST_RESULT"
  fi

  if [ $((STATUS & SMARTCTL_DISK_FAILING)) -ne 0 ]; then
    fail "SMART overall-health self-assessment reports $DISK is failing"
  fi

  if [ $((STATUS & SMARTCTL_PREFAIL_THRESHOLD)) -ne 0 ]; then
    fail "SMART reports pre-fail attributes at or below threshold for $DISK"
  fi

  echo "$TEST SMART test passed for $DISK: $NEWEST_RESULT"
}

function main() {
  local TEST=$1
  local TARGET=$2
  local DISK
  local SELF_TEST_LOG_BEFORE

  if [ "$TEST" != "short" ] && [ "$TEST" != "long" ]; then
    fail "Unrecognised test type \"$TEST\", exiting..."
  fi

  DISK=$(resolve_disk "$TARGET")

  if [ -z "$DISK" ]; then
    fail "No disk found for $TARGET, is it a block device or mount point?"
  fi

  if [ "$TARGET" != "$DISK" ]; then
    echo "$TARGET resolved to disk $DISK"
  fi

  if self_test_in_progress "$DISK"; then
    echo "A SMART self-test is already running for $DISK, waiting for it to finish..."
    wait_for_test_to_finish "$DISK"
  fi

  SELF_TEST_LOG_BEFORE=$(read_self_test_log "$DISK") || exit 1

  echo "Starting $TEST SMART test for $DISK..."
  smartctl_checked $SMARTCTL_COMMAND_FAILED --test="$TEST" "$DISK" > /dev/null \
    || fail "Failed to start $TEST SMART test for $DISK"

  # give the disk a moment to report the test as in progress
  sleep 5
  wait_for_test_to_finish "$DISK"

  report_test_result "$TEST" "$DISK" "$SELF_TEST_LOG_BEFORE"
}

if [ $# -ne 2 ]; then
  print_usage >&2
  exit 1
fi

main "$@"
