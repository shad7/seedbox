"""
Access to the version as configured as part of installation package.
Leverages pbr (Python Build Reasonableness)
"""
from pbr import version as pbr_version

version_info = pbr_version.VersionInfo('SeedboxManager')


def version_string():
    return version_info.version_string()


def release_string():
    return version_info.release_string()
