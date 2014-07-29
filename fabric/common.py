"""
Fabric fabfile for performing slepemapy.cz updates
"""

from fabric.api import env, run as fab_run, sudo as fab_sudo
import time


if not env.environment:
    env.environment = 'staging'


def validate_environment(environment):
    if environment not in ['staging', 'production']:
        raise Exception('uknown environment: ' + environment)


def mysqldump(name=None):
    if not name:
        name = time.strftime('%Y-%m-%d_%H-%M-%S')
    dest_file = run('echo $GEOGRAPHY_DATA_DIR') + '/' + name  + '.sql'
    run('mysqldump -p$GEOGRAPHY_DATABASE_PASSWORD -u$GEOGRAPHY_DATABASE_USER -h$GEOGRAPHY_DATABASE_HOST -P$GEOGRAPHY_DATABASE_PORT $GEOGRAPHY_DATABASE_NAME > ' + dest_file)


def run(command):
    validate_environment(env.environment)
    return fab_run('. /bin/' + env.environment + '-environment && cd $GEOGRAPHY_WORKSPACE_DIR && ' + command)


def sudo(command):
    validate_environment(env.environment)
    fab_sudo('. /bin/' + env.environment + '-environment && ' + command)


def aptget_upgrade():
    """
    Performs apt-get update and upgrade
    """
    sudo('apt-get update')
    sudo('apt-get upgrade')


def reload_httpd():
    """
    Gracefully reload httpd
    """
    sudo('service apache2 graceful')


def enable_maintenance():
    """
    Enable maintenance site and disable production site
    """
    if env.environment == 'staging':
        return
    validate_environment(env.environment)
    sudo('a2ensite maintenance-' + env.environment + '.slepemapy.cz')
    sudo('a2dissite ' + env.environment + '.slepemapy.cz')
    reload_httpd()


def disable_maintenance():
    """
    Disable maintenance site and enable production site
    """
    if env.environment == 'staging':
        return
    validate_environment(env.environment)
    sudo('a2dissite maintenance-' + env.environment + '.slepemapy.cz')
    sudo('a2ensite ' + env.environment + '.slepemapy.cz')
    reload_httpd()


def install_requirements():
    run('pip install --upgrade -r ./main/requirements.txt')


def npm_install():
    run('cd main && npm install')


def grunt_deploy():
    run('cd main && grunt deploy')


def collect_static():
    run('./main/manage.py collectstatic --noinput --traceback')


def migrate():
    run('./main/manage.py migrate geography --delete-ghost-migrations --traceback')


def custom_sql():
    run('./main/manage.py sqlcustom geography --traceback')


def update_maps():
    run('./main/manage.py update_maps --traceback')


def compilemessages():
    run('./main/manage.py compilemessages --traceback')


def remove_cache():
    run('rm -rf $GEOGRAPHY_DATA_DIR/.django_cache')


def backup(name=None):
    mysqldump(name)


def derive_knowledge():
    now = time.strftime('%Y-%m-%d_%H-%M-%S')
    dest_file = run('echo $GEOGRAPHY_DATA_DIR') + '/knowledge_data_' + now + '.sql'
    enable_maintenance()
    run('./main/manage.py derived_knowledge_data | tee ' + dest_file + ' | ./main/manage.py dbshell')
    disable_maintenance()


def get_version():
    return run('git rev-parse HEAD')


def get_release_version():
    if env.environment == 'staging':
        return 'origin/master'
    else:
        return run("git fetch origin && git tag -l | grep release | sort | tail -n 1")


def update_release_version():
    run('git fetch origin')
    last_head = get_version()
    to_release = get_release_version()
    modified = bool(run(
        'if [[ `git diff --name-only ' + str(last_head) + ' ' + str(to_release) + '` ]]; then'
        '  echo 1;'
        'else'
        '  echo 0;'
        'fi;'
    ))
    run('git reset ' + to_release + ' --hard')
    run('git clean -df')
    return modified
