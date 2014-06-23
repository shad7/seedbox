CHANGES
=======

2.2.3
-----

* Updating version to 2.2.3
* added link to ChangeLog to published documentation

2.2.2
-----

* updated ChangeLog and tag release
* fixed the generated ChangeLog to represent the entire history Updated version to 2.2.2 as that is the next release strting
* updated requirements file to include sandman and click
* fixed bug where a downloaded file was within a subdirectory, and the subdirectory name is included in the filename cache attribute. Moved the subdirectory name to the filepath
* minor update to documentation configuration

2.2.1
-----

* updated changelog
* bumped to dot release
* test on travis-ci seemed to fail when writing to /tmp/<dir> so added in logic to create the <dir> under /tmp before trying to create files within <dir>

2.2
---

* changes added to ChangeLog
* added auto release of successfully built versions that include a tag
* mades changes such that seedbox works as package name but pypi still sees it as SeedboxManager
* updated sample configuration based on changes in the code and the removal of many unncessary options
* updated documentation to reflect the changes
* updated requirements based on changes from sqlobjects to sqlalchemy etc
* generally replaced or rewrote majority of the modules to simplify for the long run
* added test cases for cli to provide coverage
* replaced manager with cli to better refelct the purpose of the module and remove unncessary code
* added constants to hold flow states that are leveraged in multiple places throughout
* removed workaround for name of package causing issues with version; solved by update from pbr
* updated tests for common components
* updated the common components to remove unncessary code, apply minor fixes
* updated test cases to support changes within loader
* updated torrent loader to leverage new database implementation and models, and minor clean up. minor tweaks to parser
* added test cases to support the new process flow
* simplified the process/workflow to get rid of the elaborate steps to find out which task(s) to execute next and in what order. Instead of only being able to execute sync in parallel, now all tasks are executed in parallel
* added test cases for all tasks (plugins)
* simplified plugin model by migrating to stevedore and providing a simple abstract base task such that a task must only implement execute() and/or the optional is_actionable() method
* added testing to support new implementation based on sqlalchemy
* replaced SQLObjects with sqlalchemy to lay the foundation for supporting multi-threaded/multi-process with databases that include actual multiple concurrent requests. Added public object model for interacting with data without resulting in direct database interactions (fetch, create, update). Included sqlalchemy-migration to handle version the database schema
* moved gen_config to the tools directory to keep main directory clean
* added other details to setup.cfg
* PBR added '--use-mailcap' in the call to git log to load AUTHORS which is causing it to no longer be found as git log does not recognize the option. So removing the use of AUTHORS for a while
* added sample config generation anoptoin within tox
* some cleanup activities to reduce clutter and noise. Also small patch to version since my install library PBR seems to struggle with app name being different from package name
* updated README to remove a badge
* another fix to publish coverage results
* updated README
* tweaks for coverage
* trying something
* update settings for travis-ci
* minor tweaks
* documentation updates
* updating changelog and increasing version

2.1
---

* updating changelog and increasing version
* code fixes and cleanup
* made several updates to clean up code and added significant amount of test code to finally reach ~75% code coverage
* added test cases for options module
* Added more test cases and removed extraneous lines of code
* Added test cases for common/timeutil
* regenerated ChangeLog and generated sample configuration file
* significant refactor to simplify and become more DRY. Also reshaping the structure to align to future plans to replace the entire workflow approach currently leveraged
* Updated reference to travis ci
* Updating import from __future__ entries
* Instead of printing to stderr when the lockfile is there, simply write to the standard log to avoid having to check logs in multiple locations. Also a few pep8 updates
* Seems a variable named errno was used which took over the namespace of the imported errno module. Needed to remove the local variable to avoid clash
* Moved to leverage six instead of doing manual checks for PY2/PY3 and fixed some basic pep8 issues
* Removed old code left over as part of pssh
* MANIFEST.in had a missing 'c' so it was excluding all .py files instead of .pyc

2.0
---

* updated README
* added reference to travis-cli
* travis still
* fixing travis
* small change to get travis to work
* updated travis config and coverage config
* pep8 compliance integration with travis-ci
* fixed bug that cause version to stop working from cli
* added cli option --gen-sample so that generation of sample configuration can be accomplished via seedmgr as well as shell script stored with project
* documentation config update
* updatd documentation configuration
* Updated release info and started work on making sample config generation a cli option instead of through a shell script
* fixed setup.cfg to support upload into PyPi; ChangeLog automatic
* see previous commit with details. Moving to version 2.0
* Changed approach for configuration to simplify code and setup. Included is a generator to create a sample configuration file with help, all available options, their type, default value, and what is required

0.1.20
------

* added ability for user to specifiy filetypes in configuration file to reduce hardcoding of filetypes. The initial values are still supported by default

0.1.19
------

* fixed typo

0.1.18
------

* reved to next release version
* added logging of stacktrace in plugins

0.1.17
------

* bug fix: format(

0.1.16
------

* bug fix: forgot to escape sql input when doing select statement

0.1.15
------

* Reduced excess info logging to avoid growing logs while in cron mode. Added validate_phase plugin. The new plugin will make sure all torrents are in the proper state before allowing them to continue to the next phase. Optimized torrentparser; added dependency on Bittorrent-bencode as after performance testing it was substantially more efficient but also stricter. Therefore it will work 98% of the time and the remaiing 2% of the time we'll leverage the custom parser to extract files associated with torrent

0.1.14
------

* bumping version for next upload
* added patch to make sure using loglevel option was case insensitive
* added unittest for action module and resulted in bug fixes

0.1.13
------

* lockfile on pypi is out of date by nearly 2 years. I pulled from GitHub to get latest version. No longered required extension to lockfile
* updated README
* updated README
* updated README

0.1.12
------

* bugfix: date calculation to determine when to perform db back
* updated README
* updated README
* updated README
* updated README
* updated README
* updated README info

0.1.11
------

* fixed bug related to how frequently to do backups of db

0.1.10
------

* added lockfile support to make sure that when running as a cron that multiple instances do not run at the same time

0.1.9
-----

* undo change to filesync

0.1.8
-----

* general cleanup
* removed commented code

0.1.7
-----

* bug fix: variable name changed but didn't change all locations

0.1.6
-----

* updated the backup db routine to work similar to RotatingLogFiles
* renamed test folder to tests
* added shutilwhich to setup.py as dependency

0.1.5
-----

* moved purge from plugin to internals of datamanager. Deleted actual filepurge.py as it is no longer needed. Also added in dependency on shutilwhich since running as a cron made it difficult to find unrar

0.1.4
-----

* bumped the rev
* updated logext to default to user folder/directory if available; else cwd
* updated README; added new required attribute to configfile

0.1.3
-----

* found bug where if torrent was still downloading it would be marked as missing and then purged without ever doing sync. Added check to make sure it waits and checks again later. (automation will really help you find issues

0.1.1
-----

* forgot to include ez_setup.py in distribution
* no longer needed with setuptools model
* Changes to support packaging and distribution
* added LICENSE; MIT
* removed logfile option from filesync given it is now redundant since logging from the subprocess is now directly supported
* subprocess module will output to stdout/stderr but I wanted everything consistently going to logging so it can be properly controlled. So I added an extension to subprocess to handle attaching logging to the child process and created unit testing for the new module. Then updated filesync which uses rsync for remote syncing of files to leverage new module
* updated distribution related files
* deleted old test files since they are replaced will real unit test modules
* added sample config files to support testing
* Added another test set related to processing options and command line
* Started using unittest module for doing proper testing and converting some of the scripts I had been using to do proper unit testing. This was the first one
* updated readme
* updated readme
* Updated readme
* made adjustment so that filecopy works the same as fileunrar, after copy create a new entry for syncing. And then within delete, simply ignore any file that does not exist to avoid any exceptions
* Bug fixes related to database backup, some extra logging

0.1
---

* adding setup/distribution related files
* Initial creation
* Initial commit
