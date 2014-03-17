#!/bin/bash
SELF=`readlink -f $0`
SELF_DIR=`dirname $SELF`
GIT_DIR=$SELF_DIR/../.git


###############################################################################
# disable site
###############################################################################

if [ $GEOGRAPHY_ON_PRODUCTION ]; then
	echo " * disable production"
	sudo a2ensite maintenance-production.slepemapy.cz
	sudo a2dissite production.slepemapy.cz
	sudo service apache2 reload
fi


###############################################################################
# checkout the requested version
###############################################################################


git --git-dir=$GIT_DIR fetch origin
if [ $GEOGRAPHY_ON_PRODUCTION ]; then
	DEPLOY_VERSION=release-`git tag -l | grep release | sort | tail -n 1 | awk -F "-" '{print $2}'`;
elif [ $GEOGRAPHY_ON_STAGING ]; then
	DEPLOY_VERSION=master
else
	echo "You have to set your environment to production or staging before the deployment";
	exit 1
fi

echo " * reset to origin/$DEPLOY_VERSION"
git --git-dir=$GIT_DIR reset origin/$DEPLOY_VERSION --hard


###############################################################################
# reset the application
###############################################################################

APP_DIR="$SELF_DIR/../main"
if [ "$GEOGRAPHY_DATA_DIR" ]; then
	DATA_DIR="$GEOGRAPHY_DATA_DIR"
else
	DATA_DIR="$APP_DIR"
fi

echo " * collect static"
$APP_DIR/manage.py collectstatic --noinput
echo "HASHES = $( python $APP_DIR/manage.py static_hashes )" > $APP_DIR/hashes.py

echo " * migrate"
$APP_DIR/manage.py migrate geography --delete-ghost-migrations --traceback
echo " * load custom SQLs"
$APP_DIR/manage.py sqlcustom geography | $APP_DIR/manage.py dbshell
if git --git-dir=$GIT_DIR diff --summary HEAD origin/master | egrep 'main\/geography\/models\/(knowledge\.py|prior.py|current.py)'; then
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
	sudo a2dissite maintenance-production.slepemapy.cz
	sudo a2ensite production.slepemapy.cz
fi

echo " * reload httpd"
sudo service apache2 reload
