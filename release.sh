#!/bin/bash

if [ ! "$OPENSHIFT_SSH" ]; then
	OPENSHIFT_SSH=51bb5930500446923f000201@geography-conqueror.rhcloud.com;
fi
OPENSHIFT_REMOTE_REPOSITORY=ssh://$OPENSHIFT_SSH/~/git/geography.git/;


################################################################################
# Determine last and next release version
################################################################################

LAST_VERSION=`git tag -l | grep release | sort | tail -n 1 | awk -F "-" '{print $2}'`;
LAST_MAJOR=`echo $LAST_VERSION | awk -F "." '{print $1}' | tr -d '[A-Za-z]'`;
LAST_MINOR=`echo $LAST_VERSION | awk -F "." '{print $2}' | tr -d '[A-Za-z]'`;
LAST_MICRO=`echo $LAST_VERSION | awk -F "." '{print $3}' | tr -d '[A-Za-z]'`;

if [ ! "$NEXT_VERSION" ]; then
	read -p "Do you want to release (1) major (2) minor or (*3) micro version? " RELEASE_TYPE;
	case $RELEASE_TYPE in
		1)
			NEXT_VERSION=$(($LAST_MAJOR+1)).0.0;;
		2)
			NEXT_VERSION=$LAST_MAJOR.$(($LAST_MINOR+1)).0;;
		*)
			NEXT_VERSION=$LAST_MAJOR.$LAST_MINOR.$(($LAST_MICRO+1));;
	esac;
fi

echo "Is the following information correct?"
echo "    - last release: $LAST_VERSION";
echo "    - next release: $NEXT_VERSION";
echo "    - ssh connection: $OPENSHIFT_SSH";
read -p "Press ENTER to continue or Ctrl+C for exit...";


################################################################################
# Check validity of your local repository
################################################################################

git update-index -q --refresh;
LOCAL_CHANGES=$(git diff-index --name-only HEAD --);
if [ -n "$LOCAL_CHANGES" ]; then
	echo "You can't release with changes in your local repository";
	exit 1;
fi

git fetch origin;
git checkout master;
NOT_COMMITED=$(git diff master..origin/master);
if [ -n "$NOT_COMMITED" ]; then
	echo "Your local master branch differs from the remote one.";
	exit 1;
fi


################################################################################
# Prepare remote openshift repository
################################################################################

OPENSHIFT_REMOTE_NAME=`git remote -v | grep $OPENSHIFT_REMOTE_REPOSITORY | head -n 1 | awk -F " " '{print $1}'`;
if [ -z "$OPENSHIFT_REMOTE_NAME" ]; then
	OPENSHIFT_REMOTE_NAME=openshift;
	echo "adding $OPENSHIFT_REMOTE_NAME remote to your local repository";
	git remote add $OPENSHIFT_REMOTE_NAME $OPENSHIFT_REMOTE_REPOSITORY;
fi


################################################################################
# Download pre-release MySQL dump
###############################################################################

read -p "please ENTER to download pre-release MySQL dump...";

DUMP_COMMAND='mysqldump -p$OPENSHIFT_MYSQL_DB_PASSWORD -u$OPENSHIFT_MYSQL_DB_USERNAME -h$OPENSHIFT_MYSQL_DB_HOST -P$OPENSHIFT_MYSQL_DB_PORT $OPENSHIFT_APP_NAME';
ssh $OPENSHIFT_SSH -t "$DUMP_COMMAND > /tmp/pre-release-$NEXT_VERSION.dump.sql";
scp $OPENSHIFT_SSH:/tmp/pre-release-$NEXT_VERSION.dump.sql ./;


###############################################################################
# Create tag for the release version
###############################################################################

read -p "please ENTER to tag the release version..."
git tag release-$NEXT_VERSION;
git push origin release-$NEXT_VERSION;


###############################################################################
# Push master branch to the openshift repository
###############################################################################

read -p "please ENTER to push code from the master branch to the remote openshift repository...";
git push $OPENSHIFT_REMOTE_NAME master;


################################################################################
# Download post-release MySQL dump
################################################################################

read -p "please ENTER to download post-release MySQL dump...";
ssh $OPENSHIFT_SSH -t "$DUMP_COMMAND > /tmp/post-release-$NEXT_VERSION.dump.sql";
scp $OPENSHIFT_SSH:/tmp/post-release-$NEXT_VERSION.dump.sql ./;


################################################################################
# Clean MySQL dumps
################################################################################

read -p "please ENTER to clean MySQL dumps from the server...";
ssh $OPENSHIFT_SSH -t "rm -rf /tmp/{pre,post}-release-$NEXT_VERSION.dump.sql";

################################################################################
# Clean remote openshift branch
################################################################################

read -p "please ENTER to remove $OPENSHIFT_REMOTE_NAME remote from your local repository...";
git remote remove $OPENSHIFT_REMOTE_NAME;
