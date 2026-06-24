#!/bin/bash
#
# Title: bootboy.sh
# Description: configure collector
# Development Environment: Ubuntu 22.04.05 LTS
# Author: Guy Cole (guycole at gmail dot com)
#
PATH=/bin:/usr/bin:/etc:/usr/local/bin; export PATH
#
WORK_DIR="/home/wombat/Documents/github/mellow-mastodon/src/collector"
#
echo "start bootboy"

if ! command -v systemctl >/dev/null 2>&1; then
	echo "systemctl not found" >&2
	exit 1
fi

cd $WORK_DIR
source venv/bin/activate
python3 ./bootboy.py
echo "end bootboy"
#
