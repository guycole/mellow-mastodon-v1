#!/bin/bash
#
# Title: loader.sh
# Description: parse files from s3 and load into database
# Development Environment: Ubuntu 22.04.05 LTS
# Author: Guy Cole (guycole at gmail dot com)
#
PATH=/bin:/usr/bin:/etc:/usr/local/bin; export PATH
#
HOME_DIR="${HOME}/Documents/github"
WORK_DIR="/var/mellow/mastodon"
#
echo "start load"
cd $HOME_DIR/mellow-mastodon/src/backend
source venv/bin/activate
time python3 ./loader.py
echo "end load"
#
