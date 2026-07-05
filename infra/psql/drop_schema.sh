#!/bin/bash
#
# Title:drop_schema.sh
# Description: remove schema
# Development Environment: OS X 10.15.2/postgres 12.12
# Author: G.S. Cole (guy at shastrax dot com)
#
export PGDATABASE=mastodon
export PGHOST=localhost
export PGPASSWORD=woofwoof
export PGUSER=mastodon_admin
#
#psql $PGDATABASE -c "drop table mastodon_v1.observation"
psql $PGDATABASE -c "drop table mastodon_load_log"
#psql $PGDATABASE -c "drop table mastodon_v1.population"
#psql $PGDATABASE -c "drop table mastodon_v1.site"
#psql $PGDATABASE -c "drop table mastodon_v1.equipment"
#
