#!/bin/bash
#
# Title: collector.sh
# Description: mastodon collection
# Development Environment: Debian 10 (buster)/raspian
# Author: Guy Cole (guycole at gmail dot com)
#
# * * * * * /ho/gsc/Documents/github/mellow-hyena/bin/adsb-collector.sh > /dev/null 2>&1
#
PATH=/bin:/usr/bin:/etc:/usr/local/bin; export PATH
#LD_LIBRARY_PATH=/usr/local/lib/arm-linux-gnueabihf; export LD_LIBRARY_PATH
#
BIN_DIR="$HOME/github/mellow-mastodon-v1/bin"
WORK_DIR="$HOME/github/mellow-mastodon-v1/src/collector"
CONFIG_FILE="$WORK_DIR/config.yaml"
#
echo "start collection"
sleep 13
#
RECEIVER_MODE=$(yq -r '.receiver.mode' "$CONFIG_FILE")
echo "receiver mode: $RECEIVER_MODE"
#
if [ "$RECEIVER_MODE" = "big-search01" ]; then
    echo "invoking big-search01"
    $BIN_DIR/big-search01.sh
else
    echo "unknown receiver mode: $RECEIVER_MODE"
fi
#
echo "end collection"
#
