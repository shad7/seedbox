"""
Access to the version as configured as part of installation package.
Leverages pbr (Python Build Reasonableness)
"""
from pbr import version as pbr_version

version_info = pbr_version.VersionInfo('SeedboxManager')


def version_string():
    """
    Provide a string representing the version of the project.

    :return: project version
    :rtype: string
    """
    return version_info.version_string()


def release_string():
    """
    Provide a string representing the release of the project.

    :return: project release
    :rtype: string
    """
    return version_info.release_string()
