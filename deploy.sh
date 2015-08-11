#!/bin/bash

WORKSPACE="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# install client's code
cd $WORKSPACE/geography
npm install
grunt
$WORKSPACE/manage.py collectstatic --noinput

# install python dependencies
# pip install -r $WORKSPACE/requirements.txt

$WORKSPACE/manage.py migrate

$WORKSPACE/manage.py load_configab_experiments $WORKSPACE/ab_experiments.json

# reload http server
sudo service apache2 reload
