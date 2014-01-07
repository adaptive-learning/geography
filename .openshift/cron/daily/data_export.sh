#!/bin/bash


source $OPENSHIFT_HOMEDIR/python/virtenv/bin/activate

python "$OPENSHIFT_REPO_DIR"wsgi/openshift/manage.py dumpdata geography.answer > ${OPENSHIFT_DATA_DIR}export.json
zip ${OPENSHIFT_DATA_DIR}export_json ${OPENSHIFT_DATA_DIR}export.json
python "$OPENSHIFT_REPO_DIR"wsgi/openshift/manage.py csv_answers ${OPENSHIFT_DATA_DIR}export.csv
zip ${OPENSHIFT_DATA_DIR}export_csv ${OPENSHIFT_DATA_DIR}export.csv
