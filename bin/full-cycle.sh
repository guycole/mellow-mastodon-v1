#!/bin/bash
#
# Title: full-cycle.sh
# Description: download collector files, parse and load to DB and generate report
# Development Environment: Debian 10 (buster)/raspian
# Author: Guy Cole (guycole at gmail dot com)
#
PATH=/bin:/usr/bin:/etc:/usr/local/bin; export PATH
#
HOME_DIR="${HOME}/Documents/github"
#
time $HOME_DIR/mellow-mastodon/bin/fresh-from-s3.sh
time $HOME_DIR/mellow-mastodon/bin/loader.sh
#
