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
    common.grunt_deploy()
    common.collect_static()
    common.update_maps()
    common.migrate()
    common.custom_sql()
    common.remove_cache()
    common.compilemasseges()
    common.backup('release_after_' + version_prepared)
