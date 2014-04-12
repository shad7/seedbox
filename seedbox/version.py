"""
Access to the version as configured as part of installation package.
Leverages pbr (Python Build Reasonableness)
"""
from pbr import version as pbr_version

# stupid workaround to solve the problem where pbr can not
# handle the fact that my registered name 'SeedboxManager'
# is different from my package name 'seedbox' when I attempt
# to generate coverage results. So I'm forced to change the name
# within setup.cfg to seedbox for coverage to work.
version_info = pbr_version.VersionInfo('SeedboxManager')
alt_version_info = pbr_version.VersionInfo('seedbox')


def version_string():
    try:
        return version_info.version_string()
    except ValueError:
        return alt_version_info.version_string()


def release_string():
    try:
        return version_info.release_string()
    except ValueError:
        return alt_version_info.release_string()
