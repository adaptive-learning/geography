"""
Upgrade procedures for slepemapy.cz
"""

import common


def deploy():
    common.backup('release_before_' + common.get_release_version().replace("/", "-"))
    if not common.update_release_version():
        return
    common.npm_install()
    common.grunt_deploy()
    common.collect_static()
    common.update_maps()
    common.migrate()
    common.custom_sql()
    common.remove_cache()
    common.backup('release_after_' + common.get_release_version().replace("/", "-"))
