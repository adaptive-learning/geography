#!/bin/bash
SELF=$0
SELF_DIR=`dirname $SELF`
if [ $GEOGRAPHY_WORKSPACE_DIR ]; then
	WORKSPACE_DIR=$GEOGRAPHY_WORKSPACE_DIR;
else
	WORKSPACE_DIR=$SELF_DIR/..
fi
APP_DIR="$WORKSPACE_DIR/main"


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
$APP_DIR/manage.py derived_knowledge_data | $APP_DIR/manage.py dbshell


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
