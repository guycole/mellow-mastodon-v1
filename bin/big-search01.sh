#!/bin/bash
#
# Title: big-search01.sh
# Description: mastodon collection (118M to 960M)
# Development Environment: Ubuntu 22.04.05 LTS
# Author: Guy Cole (guycole at gmail dot com)
#
PATH=/bin:/usr/bin:/etc:/usr/local/bin; export PATH
#
FRESH_DIR=/var/wombat/fresh/mastodon
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
WORK_DIR="/home/wombat/Documents/github/mellow-mastodon/src/collector"
#
echo "start collection"
sleep 13
cd $WORK_DIR
source venv/bin/activate
python3 ./collector.py ${UUID}
#
time $RTL_POWER -f $FREQ_LOW:$FREQ_HIGH:$BIN_SIZE -i $REPORT -e $DURATION > /tmp/$POWER_FILE_NAME
#
mv /tmp/$POWER_FILE_NAME $FRESH_DIR/$POWER_FILE_NAME
#
