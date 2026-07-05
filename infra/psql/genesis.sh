#!/bin/bash
#
# Title:genesis.sh
# Description:
# Development Environment: OS X 10.15.2/postgres 12.12
# Author: G.S. Cole (guy at shastrax dot com)
#
psql -U postgres template1 (or psql -U gsc template1)

# (linux) su - postgres
createuser -U postgres -d -e -l -P -r -s mastodon_admin
woofwoof
createuser -U postgres -e -l -P mastodon_client
batabat

# as pg superuser
# create tablespace mastodon location '/mnt/pg_tablespace/mastodon';
# create tablespace mastodon location '/mnt/pp1/postgres/mastodon';
# create tablespace mastodon location '/Library/PostgreSQL/pg_tablespace/mastodon';

createdb mastodon -O mastodon_admin  -E UTF8 -T template0 -l C

# psql -h localhost -p 5432 -U mastodon_admin -d mastodon
# psql -h localhost -p 5432 -U mastodon_client -d mastodon

# as mastodon_admin
create schema mastodon_v1;
grant usage on schema mastodon_v1 to mastodon_client;
