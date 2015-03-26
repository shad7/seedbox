#!/usr/bin/env bash
set -e

txtbld=$(tput bold)             # Bold
bldred=${txtbld}$(tput setaf 1) #  red
txtrst=$(tput sgr0)             # Reset

if [ -z "$1" ]
  then
    echo -e "${bldred}No release version supplied${txtrst}" && exit 1
fi

# make sure all requirements are installed; else setup.py develop fails
pip install -q -r requirements.txt

######
# Prepare release by updating version, generating updated ChangeLog
#####

# intialize release with a version
git flow release start "$1"

# update version within setup
sed -i -e "s/version = .*/version = $1/g" setup.cfg
python setup.py -q develop
git commit setup.cfg -m "[RELEASE] Update to version v$1"

# tag the last commit such that pbr picks up the tag as
# the version number; also required when generating the
# ChangeLog file updates.
COMMIT_HASH=$(git log -1 --pretty=format:"%h")
git tag -a "$1" -m "version $1" "${COMMIT_HASH}"

# generate ChangeLog and updated docs; commit
python setup.py sdist bdist_egg bdist_wheel

# delete tag (only needed temporary to workaround our issue with pbr;
# git flow will add it back in and push it
git tag -d "$1"

# should result in updating the previous commit to now include
# AUTHOR, ChangeLog, doc/source/ChangeLog.rst
git commit --all --amend --no-edit

# finish release and push to remote git which does all of the
# following steps:
#
#       git checkout master
#       git fetch origin master
#       git merge --no-ff $1
#       git tag -a $1
#       git push origin master
#       git checkout develop
#       git fetch origin develop
#       git merge --no-ff $1
#       git push origin develop
#       git branch -d $1
#
#   As you can see there are quite a few things that is done here.
#   To explain this simply you can read the following list:
#
#       Latest objects have been fetched from 'origin'
#       Release branch has been merged into 'master'
#       The release was tagged '$1'
#       Release branch has been back-merged into 'develop'
#       Release branch 'release/$1' has been deleted
#       'develop', 'master' and tags have been pushed to 'origin'
#       Release branch 'release/$1' in 'origin' has been deleted.
#
# Because we do not publish the release branch; and do a push, it is
# resulting in an error when the deletion of the branch from remote
# happens; as such we check for unable to delete in error message to determine
# if we continue with execution and upload the distribution.
errstr="unable to delete"
[[ $(git flow release finish -F -p -m "version $1" "$1" 2>&1) =~ $errstr ]]

#####
# Release has been tagged and merged; now prepare to publish
# new version for subscribers
#####

# now upload the source, egg, and wheel
twine upload dist/*

