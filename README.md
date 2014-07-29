# Geography

[![Build Status](https://travis-ci.org/proso/geography.png)](https://travis-ci.org/proso/geography)


## Deployment

Before the deployment on the production server, please release a new tag with
the following command:

```
git tag release-<new version>
git push origin release-<new version>
```

Connect to the [MUNI VPN](https://vpn.muni.cz) to be able to connect to
porsena.fi.muni.cz directly and use the following command:

```
fab -f deployment.py deploy --set=environment=<environment> -H porsena.fi.muni.cz -u <user>
```

where **environment** is 'production' or 'staging' and **user** is your username
used for porsena.fi.muni.cz (or just 'root').

## Localhost

[localhost:8000](http://localhost:8000)

```
cd <path_to_your_local_git_repo>/main
grunt deploy
./manage.py runserver
```
When editing `*.sass` and `*.js` files you need to run also
```
grunt watch
```
in order to see the changes

## Data

You can download data from the following url:

```
<server>/csv/<model name>
```

where `<server>` is the address of the server and `<model name>` is one of the following:

* `ab_group`,
* `ab_value`,
* `answer`,
* `answer_ab_values`,
* `answer_options`
* `place`
* `placerelation`
* `placerelation_related_places`

## Environment Variables

```
GEOGRAPHY_ON_PRODUCTION or GEOGRAPHY_ON_STAGING
GEOGRAPHY_DATABASE_ENGINE
GEOGRAPHY_DATABASE_NAME
GEOGRAPHY_DATABASE_USER
GEOGRAPHY_DATABASE_PASSWORD
GEOGRAPHY_DATABASE_HOST
GEOGRAPHY_DATABASE_PORT
GEOGRAPHY_DATA_DIR
GEOGRAPHY_SECRET_KEY
GEOGRAPHY_FACEBOOK_APP_ID
GEOGRAPHY_FACEBOOK_API_SECRET
GEOGRAPHY_WORKSPACE_DIR
GEOGRAPHY_VIRTUALENV
```
