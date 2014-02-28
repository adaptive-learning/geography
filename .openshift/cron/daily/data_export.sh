#!/bin/bash
SELF=`readlink -f $0`
SELF_DIR=`dirname $SELF`

source $OPENSHIFT_HOMEDIR/python/virtenv/bin/activate

ROOT_DIR=${OPENSHIFT_REPO_DIR:="$SELF_DIR/../../../"}
DATA_DIR=${OPENSHIFT_DATA_DIR:="$SELF_DIR/../../../wsgi/openshift/"}

for MODEL in place placerelation answer answer_options; do
	python "$ROOT_DIR"wsgi/openshift/manage.py table2csv geography_$MODEL ${DATA_DIR}geography.$MODEL.csv
	zip --junk-paths ${DATA_DIR}geography.$MODEL.zip ${DATA_DIR}geography.$MODEL.csv
	rm -rf ${DATA_DIR}geography.$MODEL.csv
done
