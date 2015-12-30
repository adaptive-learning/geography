# geography
An intelligent application for practicing geography. 

## Development

### Initial setup

Install [pip](https://pip.pypa.io/en/latest/installing/)

Install [virtualenvwrapper](http://virtualenvwrapper.readthedocs.org/en/latest/install.html)

  $ pip install virtualenvwrapper

Setup your local virtual environment:

  mkvirtualenv geography
  workon geography

Install python dependencies

```
cd <path_to_your_local_git_repo>
pip install -r requirements.txt
```
It might require to install (with yum, apt-get or whatever) the following:
* [python developer package](http://stackoverflow.com/questions/6230444/how-to-install-python-developer-package), 
* [SciPy](http://www.scipy.org/), 
* PostgreSQL (On Ubuntu it is `postgresql postgresql-contrib`),
* PostgreSQL developer package (On Ubuntu it is [libpq-dev](https://packages.debian.org/sid/libpq-dev)).

To setup database run
```
sudo -i -u postgres
psql
```
and in the postgreSQL shell opened by `psql` command run
```
CREATE DATABASE geography;
CREATE USER geography WITH PASSWORD 'geography';
GRANT ALL PRIVILEGES ON DATABASE "geography" to geography;
```
Add this line
```
export DATABASE_URL=postgres://geography:geography@localhost/geography
```
to 
```
~/.virtualenvs/geography/bin/postactivate
```
and run again
```
workon geography
```
apply migrations
```
./manage.py migrate
```

Install client dependencies

```
cd geography
npm install
grunt
```
On Ubuntu you might need also the following to make `grunt` work
```
sudo apt-get install nodejs-legacy
```

### When developing

Run the server on localhost:8003
```
cd <path_to_your_local_git_repo>
workon geography
./manage.py runserver 8003
```
In order to see the changes when editing  client files (e.g. `*.sass` and `*.js`) you need to run also
```
cd  geography
grunt watch
```

### Manage translations
To update translations on [transifex.com/adaptive-learning/slepemapycz](https://www.transifex.com/adaptive-learning/slepemapycz) set up your [~/.transifexrc](http://docs.transifex.com/client/config/#transifexrc) and use [Transifex client](http://docs.transifex.com/client/)
```
tx push -s
```
To pull translated stings
```
tx pull -a
```
