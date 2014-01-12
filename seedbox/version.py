"""
Access to the version as configured as part of installation package.
Leverages pbr (Python Build Reasonableness)
"""

import pbr.version

version_info = pbr.version.VersionInfo('SeedboxManager')
