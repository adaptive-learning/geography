
# Geography

[![Build Status](https://travis-ci.org/proso/geography.png)](https://travis-ci.org/proso/geography)

## Deployment

The content of this repository is continuously built by [https://travis-ci.org](https://travis-ci.org/proso/geography)
which deploys the current code to the [staging server](https://travis-ci.org/proso/geography).

During the release the content of the repository has to be pushed to the Openshift GIT repository.
You should add the Openshift GIT repository to your remotes:

	git add remote openshift ssh://51bb5930500446923f000201@geography-conqueror.rhcloud.com/~/git/geography.git/

To release `master` branch as a version `X.Y.Z` do the following:

	git push openshift master
	git tag tag release-X.Y.Z
	git push origin release-X.Y.Z

## Repository Layout

* `wsgi/` - Externally exposed wsgi code goes
* `wsgi/static/` - Public static content gets served here
* `libs/` - Additional libraries
* `data/` - For not-externally exposed wsgi code
* `setup.py` - Standard setup.py, specify deps here
* `../data` - For persistent data (also env var: OPENSHIFT_DATA_DIR)
* `.openshift/action_hooks/pre_build` - Script that gets run every git push before the build
* `.openshift/action_hooks/build` - Script that gets run every git push as part of the build process (on the CI system if available)
* `.openshift/action_hooks/deploy` - Script that gets run every git push after build but before the app is restarted
* `.openshift/action_hooks/post_deploy` - Script that gets run every git push after the app is restarted


## Openshift Environment Variables

OpenShift provides several environment variables to reference for ease
of use.  The following list are some common variables but far from exhaustive:

	os.environ['OPENSHIFT_APP_NAME']  - Application name
	os.environ['OPENSHIFT_DATA_DIR']  - For persistent storage (between pushes)
	os.environ['OPENSHIFT_TMP_DIR']   - Temp storage (unmodified files deleted after 10 days)
	os.environ['OPENSHIFT_MYSQL_DB_HOST']      - DB host
	os.environ['OPENSHIFT_MYSQL_DB_PORT']      - DB Port
	os.environ['OPENSHIFT_MYSQL_DB_USERNAME']  - DB Username
	os.environ['OPENSHIFT_MYSQL_DB_PASSWORD']  - DB Password

To get a full list of environment variables, simply add a line in your
.openshift/action_hooks/build script that says "export" and push.


