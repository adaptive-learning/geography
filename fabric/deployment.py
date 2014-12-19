"""
Upgrade procedures for slepemapy.cz
"""

import common


def deploy():
    version_prepared = common.get_release_version().replace("/", "-").replace(" ", "-")
    common.backup('release_before_' + version_prepared)
    if not common.update_release_version():
        return
    common.npm_install()
    common.install_requirements()
    common.manage_py('syncdb')
    common.manage_py('migrate geography --delete-ghost-migrations')
    common.manage_py('compilemessages')
    common.reload_httpd()
    common.grunt_deploy()
    common.manage_py('collectstatic --noinput')
    common.static_hashes()
    common.manage_py('update_maps')
    common.manage_py('sqlcustom geography')
    common.remove_cache()
    common.backup('release_after_' + version_prepared)
