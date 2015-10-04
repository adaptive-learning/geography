#!/bin/bash

WORKSPACE="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# install python dependencies
pip install -r $WORKSPACE/requirements.txt

# install client's code
cd $WORKSPACE/geography
npm install
grunt
$WORKSPACE/manage.py collectstatic --noinput

$WORKSPACE/manage.py migrate

$WORKSPACE/manage.py compilemessages

$WORKSPACE/manage.py load_configab_experiments $WORKSPACE/ab_experiments.json

# reload http server
sudo apachectl -k graceful
