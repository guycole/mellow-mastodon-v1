#!/bin/bash
#
# Title:add_schema.sh
# Description:
# Development Environment: OS X 10.15.2/postgres 12.12
# Author: G.S. Cole (guy at shastrax dot com)
#
export PGDATABASE=mastodon
export PGHOST=localhost
export PGPASSWORD=woofwoof
export PGUSER=mastodon_admin
#
#psql < equipment.psql
#psql < site.psql
psql < load_log.psql
#psql < population.psql
#psql < observation.psql
#
