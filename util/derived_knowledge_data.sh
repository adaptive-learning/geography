#!/bin/bash
SELF=$0
SELF_DIR=`dirname $SELF`
if [ $GEOGRAPHY_WORKSPACE_DIR ]; then
	WORKSPACE_DIR=$GEOGRAPHY_WORKSPACE_DIR;
else
	WORKSPACE_DIR=$SELF_DIR/..
fi
APP_DIR="$WORKSPACE_DIR/main"
if [ "$GEOGRAPHY_DATA_DIR" ]; then
	DATA_DIR="$GEOGRAPHY_DATA_DIR"
else
	DATA_DIR="$APP_DIR"
fi


###############################################################################
# disable site
###############################################################################

if [ $GEOGRAPHY_ON_PRODUCTION ]; then
	echo " * disable production"
	a2ensite maintenance-production.slepemapy.cz
	a2dissite production.slepemapy.cz
	service apache2 reload
fi


###############################################################################
# derive knowledge data
###############################################################################

echo " * derive knowledge data"
DEST_FILE=$DATA_DIR/derived_knowledge_`date +"%Y-%m-%d_%H-%M-%S"`.sql
$APP_DIR/manage.py derived_knowledge_data | tee $DEST_FILE | $APP_DIR/manage.py dbshell


###############################################################################
# enable site
###############################################################################
if [ $GEOGRAPHY_ON_PRODUCTION ]; then
	echo " * enable production"
	a2dissite maintenance-production.slepemapy.cz
	a2ensite production.slepemapy.cz
fi

echo " * reload httpd"
service apache2 reload
