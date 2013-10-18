#!/bin/bash


source $OPENSHIFT_HOMEDIR/python/virtenv/bin/activate

python "$OPENSHIFT_REPO_DIR"wsgi/openshift/manage.py dumpdata questions.answer > ${OPENSHIFT_DATA_DIR}export.json
