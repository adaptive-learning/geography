#!/bin/bash
SELF=`readlink -f $0`
SELF_DIR=`dirname $SELF`

set -x

DATA_DIR=$(GEOGRAPHY_DATA_DIR:="$SELF_DIR")

$SELF_DIR/manage.py collectstatic --noinput
echo "HASHES = $( python $SELF_DIR/manage.py static_hashes )" > $SELF_DIR/hashes.py

$SELF_DIR/manage.py migrate geography --delete-ghost-migrations --traceback
$SELF_DIR/manage.py sqlcustom geography | $SELF_DIR/manage.py dbshell
$SELF_DIR/manage.py derived_knowledge_data
rm -rf $OPENSHIFT_DATA_DIR/.django_cache
