#!/bin/bash
#
# Title: csv2json.sh
# Description: read CSV files and convert to JSON
# Development Environment: Ubuntu 22.04.05 LTS
# Author: Guy Cole (guycole at gmail dot com)
#
PATH=/bin:/usr/bin:/etc:/usr/local/bin; export PATH
#
HOME_DIR="${HOME}/Documents/github"
#
echo "begin csv2json"
#
cd $HOME_DIR/mellow-mastodon/src/collector 
source venv/bin/activate
time python3 csv2json.py
# 
echo "end csv2json"
#
