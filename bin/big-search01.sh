#!/bin/bash
#
# Title: big-search01.sh
# Description: mastodon collection (118M to 960M)
# Development Environment: Ubuntu 22.04.05 LTS
# Author: Guy Cole (guycole at gmail dot com)
#
PATH=/bin:/usr/bin:/etc:/usr/local/bin; export PATH
#
VARMEL_DIR=/var/mellow/mastodon
#
BIN_SIZE=10k
DURATION=5m
FREQ_LOW=117.975M
FREQ_HIGH=960M
REPORT=1m 
#
HOST_NAME=$(hostname)
SCRIPT_NAME=$0
TODAY=$(date '+%Y-%m-%d')
UUID=$(uuidgen)
#
RTL_POWER="/usr/local/bin/rtl_power"
#
POWER_FILE_NAME="${UUID}.csv"
#
time $RTL_POWER -f $FREQ_LOW:$FREQ_HIGH:$BIN_SIZE -i $REPORT -e $DURATION > /tmp/$POWER_FILE_NAME
#
mv /tmp/$POWER_FILE_NAME $VARMEL_DIR/fresh/$POWER_FILE_NAME
#
