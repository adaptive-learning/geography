#!/bin/bash

WORKSPACE="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# install python dependencies
pip install -r $WORKSPACE/requirements.txt

# install client's code
cd $WORKSPACE/geography
npm install
$WORKSPACE/geography/node_modules/grunt-cli/bin/grunt -v --force
$WORKSPACE/manage.py collectstatic --noinput

$WORKSPACE/manage.py migrate

$WORKSPACE/manage.py compilemessages

$WORKSPACE/manage.py load_flashcards --skip-language-check $WORKSPACE/data/geography-flashcards.json

$WORKSPACE/manage.py load_configab_experiments $WORKSPACE/ab_experiments.json
