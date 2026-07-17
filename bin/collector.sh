#!/bin/bash
#
# Title: collector.sh
# Description: mastodon collection
# Development Environment: Debian 10 (buster)/raspian
# Author: Guy Cole (guycole at gmail dot com)
#
PATH=/bin:/usr/bin:/etc:/usr/local/bin; export PATH
#LD_LIBRARY_PATH=/usr/local/lib/arm-linux-gnueabihf; export LD_LIBRARY_PATH
#
BIN_DIR="$HOME/github/mellow-mastodon-v1/bin"
WORK_DIR="$HOME/github/mellow-mastodon-v1/src/collector"
CONFIG_FILE="$WORK_DIR/config.yaml"
#
echo "start collection"
#
RECEIVER_TASK=$(yq -r '.receiver.task' "$CONFIG_FILE")
echo "receiver task: $RECEIVER_TASK"
#
if [ "$RECEIVER_TASK" = "mastodon-v1-bs1" ]; then
    echo "invoking big-search01"
    $BIN_DIR/big-search01.sh
else
    echo "unknown receiver task: $RECEIVER_TASK"
fi
#
echo "end collection"
#
