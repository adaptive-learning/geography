#!/bin/bash


source $OPENSHIFT_HOMEDIR/python/virtenv/bin/activate

python "$OPENSHIFT_REPO_DIR"wsgi/openshift/manage.py csv_answers ${OPENSHIFT_DATA_DIR}export.csv
zip --junk-paths ${OPENSHIFT_DATA_DIR}export_csv ${OPENSHIFT_DATA_DIR}export.csv
rm -rf ${OPENSHIFT_DATA_DIR}export.csv
