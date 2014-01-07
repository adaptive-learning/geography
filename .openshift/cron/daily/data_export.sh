#!/bin/bash


source $OPENSHIFT_HOMEDIR/python/virtenv/bin/activate

python "$OPENSHIFT_REPO_DIR"wsgi/openshift/manage.py dumpdata geography.answer --format=xml> ${OPENSHIFT_DATA_DIR}export.xml
zip ${OPENSHIFT_DATA_DIR}export_xml ${OPENSHIFT_DATA_DIR}export.xml
rm -rf ${OPENSHIFT_DATA_DIR}export.xml
python "$OPENSHIFT_REPO_DIR"wsgi/openshift/manage.py csv_answers ${OPENSHIFT_DATA_DIR}export.csv
zip ${OPENSHIFT_DATA_DIR}export_csv ${OPENSHIFT_DATA_DIR}export.csv
rm -rf ${OPENSHIFT_DATA_DIR}export.csv
