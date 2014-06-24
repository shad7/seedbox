#!/bin/bash
set -e

txtbld=$(tput bold)             # Bold
bldred=${txtbld}$(tput setaf 1) #  red
txtrst=$(tput sgr0)             # Reset

if [ -z "$1" ]
  then
    echo -e "${bldred}No release version supplied${txtrst}" && exit 1
fi

# make sure all requirements are installed; else setup.py develop fails
pip install -r requirements.txt

# intialize release with a version
git flow release start $1

# update version within setup; commit and tag
sed -i -e "s/version = .*/version = $1/g" setup.cfg
python setup.py develop
git commit setup.cfg -m "Update to version v$1"
COMMIT_HASH=$(git log -1 --pretty=format:"%h")
git tag -a $1 -m "version $1" ${COMMIT_HASH}

# generate ChangeLog and updated docs; commit and move tag
python setup.py sdist
cp ChangeLog doc/source/ChangeLog.rst
git commit --amend --no-edit ChangeLog doc/source/ChangeLog.rst
COMMIT_HASH=$(git log -1 --pretty=format:"%h")
git tag -f -a $1 -m "version $1" ${COMMIT_HASH}

# upload the latest version to pypi
python setup.py sdist bdist_egg upload
git commit --amend --no-edit ChangeLog

# finish release and push to remote git
git flow release finish -p $1


