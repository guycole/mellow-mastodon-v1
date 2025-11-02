#!/bin/bash 
#
# Title: archiver.sh
# Description: create daily archive file of collection results
# Development Environment: Ubuntu 22.04.05 LTS
# Author: Guy Cole (guycole at gmail dot com)
#
PATH=/bin:/usr/bin:/etc:/usr/local/bin:/opt/homebrew/bin/aws; export PATH
#
if [[ $# -eq 0 ]] ; then
    echo "missing site argument"
    exit 1
fi
#
TODAY=$(date '+%Y-%m-%d')
FILE_NAME="$1-${TODAY}.tgz"
#
EXPORT_DIR="export"
PEAKER_DIR="peaker"
WORK_DIR="/var/mellow/mastodon"
#
echo "start archive for $FILE_NAME"
#
cd ${WORK_DIR}
tar -cvzf ${FILE_NAME} ${PEAKER_DIR}
mv ${FILE_NAME} ${EXPORT_DIR}
#
echo "cleanup"
rm -rf ${PEAKER_DIR}
mkdir ${PEAKER_DIR}
#
echo "end archive"
#
