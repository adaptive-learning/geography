WORKSPACE="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# install client's code
cd $WORKSPACE/geography
npm install
grunt
$WORKSPACE/manage.py collectstatic --noinput

# install python dependencies
pip install -r $WORKSPACE/requirements.txt

# reload http server
sudo service apache2 reload
