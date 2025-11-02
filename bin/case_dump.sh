#!/bin/bash
#
# Title: case_dump.sh
# Description: 
# Development Environment: Ubuntu 22.04.05 LTS
# Author: Guy Cole (guycole at gmail dot com)
#
PATH=/bin:/usr/bin:/etc:/usr/local/bin; export PATH
#
HOME_DIR="${HOME}/Documents/github"
#
echo "begin case_dump"
cd $HOME_DIR/mellow-mastodon/src/backend
source venv/bin/activate
time python3 ./case_dump.py
#
echo "end case_dump"
#
