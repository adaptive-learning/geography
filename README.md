# Geography

[![Build Status](https://travis-ci.org/proso/geography.png)](https://travis-ci.org/proso/geography)


## Deployment

### Staging Server

[staging.slepemapy.cz](http://staging.slepemapy.cz)

You have to log on the server and:

```
sudo su
. /bin/staging-environment
cd $GEOGRAPHY_WORKSPACE_DIR
./util/deploy.sh
```

### Production Server

[www.slepemapy.cz](http://www.slepemapy.cz)

Firstly you need to tag a new version:

```
git tag <new version>
git push origin <new version>
```

Then you have to log on the server and:

```
sudo su
. /bin/production-environment
cd $GEOGRAPHY_WORKSPACE_DIR
./util/deploy.sh
```

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
```
