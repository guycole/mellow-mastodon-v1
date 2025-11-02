#!/bin/bash 
#
# Title: wombat01-to-s3.sh
# Description: move mastodon files from local file system to s3
# Development Environment: Ubuntu 22.04.05 LTS
# Author: Guy Cole (guycole at gmail dot com)
#
PATH=/bin:/usr/bin:/etc:/usr/local/bin:/opt/homebrew/bin/aws; export PATH
#
DEST_BUCKET=s3://mellow-mastodon-uw2-m7766.braingang.net/fresh/
#
EXPORT_DIR="export"
PROCESSED_DIR="processed"
SOURCE_DIR="cooked"
WORK_DIR="/var/mellow/mastodon"
#
cd ${WORK_DIR}/${EXPORT_DIR}
#
echo "start s3 transfer" 
aws s3 mv . $DEST_BUCKET --recursive --profile=wombat01
#
echo "end archive"
#
