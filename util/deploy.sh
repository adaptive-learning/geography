#!/bin/bash
SELF=$0
SELF_DIR=`dirname $SELF`
if [ $GEOGRAPHY_WORKSPACE_DIR ]; then
	WORKSPACE_DIR=$GEOGRAPHY_WORKSPACE_DIR;
else
	WORKSPACE_DIR=$SELF_DIR/..
fi
WORK_TREE=$WORKSPACE_DIR
APP_DIR="$WORKSPACE_DIR/main"
if [ "$GEOGRAPHY_DATA_DIR" ]; then
	DATA_DIR="$GEOGRAPHY_DATA_DIR"
else
	DATA_DIR="$APP_DIR"
fi
GIT_DIR=$WORK_TREE/.git
GIT_COMMAND="git --git-dir=$GIT_DIR --work-tree=$WORK_TREE"


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
# checkout the requested version
###############################################################################

$GIT_COMMAND fetch origin
LAST_HEAD=`$GIT_COMMAND rev-parse HEAD`
echo " * original HEAD: $LAST_HEAD"

if [ $GEOGRAPHY_ON_PRODUCTION ]; then
	DEPLOY_VERSION=release-`git tag -l | grep release | sort | tail -n 1 | awk -F "-" '{print $2}'`;
elif [ $GEOGRAPHY_ON_STAGING ]; then
	DEPLOY_VERSION="origin/master"
else
	echo "You have to set your environment to production or staging before the deployment";
	exit 1
fi

echo " * reset to $DEPLOY_VERSION"
$GIT_COMMAND reset $DEPLOY_VERSION --hard
$GIT_COMMAND clean -df
NEW_HEAD=`$GIT_COMMAND rev-parse HEAD`
echo " * new HEAD: $NEW_HEAD"


###############################################################################
# reset the application
###############################################################################

echo " * collect static"
$APP_DIR/manage.py collectstatic --noinput
echo "HASHES = $( python $APP_DIR/manage.py static_hashes )" > $APP_DIR/hashes.py

echo " * update maps"
$APP_DIR/manage.py update_maps

echo " * migrate"
$APP_DIR/manage.py migrate geography --delete-ghost-migrations --traceback
echo " * load custom SQLs"
$APP_DIR/manage.py sqlcustom geography | $APP_DIR/manage.py dbshell
if $GIT_COMMAND diff --name-only $LAST_HEAD origin/master | egrep 'main\/geography\/models\/(knowledge\.py|prior.py|current.py)'; then
	echo " * derive knowledge data"
	$APP_DIR/manage.py derived_knowledge_data
fi
echo " * remove django cache"
rm -rf $DATA_DIR/.django_cache


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
