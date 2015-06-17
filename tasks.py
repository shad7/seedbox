# flake8: noqa
from __future__ import print_function, unicode_literals

import io
import logging
import os

from invoke import task, run
import pkg_resources

try:
    pkg_resources.require('semantic_version')
    pkg_resources.require('twine')
    pkg_resources.require('wheel')
except pkg_resources.DistributionNotFound:
    # see urllib3 regarding InsecureRequestWarning and InsecurePlatformWarning
    logging.captureWarnings(True)
    run('pip -q install semantic_version twine wheel')


@task
def install_gitflow():
    """Install git-flow if not found"""
    if not run('which git-flow', hide=True, warn=True).ok:
        run('wget --no-check-certificate -q -O /tmp/gitflow-installer.sh  https://raw.github.com/petervanderdoes/gitflow/develop/contrib/gitflow-installer.sh')
        run('sudo bash /tmp/gitflow-installer.sh install stable')
        run('rm /tmp/gitflow-installer.sh')


@task
def next_release(major=False, minor=False, patch=True):
    """Get next release version (by major, minor or patch)"""

    import semantic_version

    prev = run('git describe --abbrev=0 --tags', hide=True).stdout
    ver = semantic_version.Version(prev)
    if major:
        return ver.next_major()
    if minor:
        return ver.next_minor()
    if patch:
        return ver.next_patch()
    return None


@task(install_gitflow)
def start_rel_branch(relver):
    """Start release branch"""
    print('start release branch', relver)
    run('git flow release start {}'.format(relver), hide=True)


@task(install_gitflow)
def finish_rel_branch(relver):
    """Finish release branch"""
    print('finish release branch', relver)
    run('git flow release finish --keepremote -F -p -m "version {ver}" {ver}'.format(ver=relver), hide=True)


@task
def package():
    """Package application for release"""
    print('packaging application')
    run('python setup.py sdist bdist_egg bdist_wheel', hide=True)


def _iter_changelog(changelog):
    """Convert a oneline log iterator to formatted strings.

    :param changelog: An iterator of one line log entries like
        that given by _iter_log_oneline.
    :return: An iterator over (release, formatted changelog) tuples.
    """
    first_line = True
    current_release = None
    prev_msg = None

    yield current_release, 'CHANGES\n=======\n\n'
    for hash, tags, msg in changelog:

        if prev_msg is None:
            prev_msg = msg
        else:
            if prev_msg.lower() == msg.lower():
                continue
            else:
                prev_msg = msg

        if tags:
            current_release = max(tags, key=pkg_resources.parse_version)
            underline = len(current_release) * '-'
            if not first_line:
                yield current_release, '\n'
            yield current_release, (
                '%(tag)s\n%(underline)s\n\n' %
                dict(tag=current_release, underline=underline))

        if not msg.startswith('Merge '):
            if msg.endswith('.'):
                msg = msg[:-1]
            yield current_release, '* %(msg)s\n' % dict(msg=msg)
        first_line = False


def _iter_log_inner(debug):
    """Iterate over --oneline log entries.

    This parses the output intro a structured form but does not apply
    presentation logic to the output - making it suitable for different
    uses.

    :return: An iterator of (hash, tags_set, 1st_line) tuples.
    """
    if debug:
        print('Generating ChangeLog')

    changelog = run('git log --oneline --decorate', hide=True).stdout.strip().decode('utf-8', 'replace')
    for line in changelog.split('\n'):
        line_parts = line.split()
        if len(line_parts) < 2:
            continue
        # Tags are in a list contained in ()'s. If a commit
        # subject that is tagged happens to have ()'s in it
        # this will fail
        if line_parts[1].startswith('(') and ')' in line:
            msg = line.split(')')[1].strip()
        else:
            msg = ' '.join(line_parts[1:])

        if 'tag:' in line:
            tags = set([
                tag.split(',')[0]
                for tag in line.split(')')[0].split('tag: ')[1:]])
        else:
            tags = set()

        yield line_parts[0], tags, msg


def _iter_log_oneline(debug):
    """Iterate over --oneline log entries if possible.

    This parses the output into a structured form but does not apply
    presentation logic to the output - making it suitable for different
    uses.
    """
    return _iter_log_inner(debug)


@task
def write_changelog(debug=False):
    """Write a changelog based on the git changelog."""
    changelog = _iter_log_oneline(debug)
    if changelog:
        changelog = _iter_changelog(changelog)
    if not changelog:
        return
    if debug:
        print('Writing ChangeLog')
    new_changelog = os.path.join(os.path.curdir, 'ChangeLog')
    # If there's already a ChangeLog and it's not writable, just use it
    if (os.path.exists(new_changelog)
            and not os.access(new_changelog, os.W_OK)):
        return
    with io.open(new_changelog, 'w', encoding='utf-8') as changelog_file:
        for release, content in changelog:
            changelog_file.write(content)


@task
def prepare_release(ver=None):
    """Prepare release artifacts"""
    write_changelog(True)
    if ver is None:
        ver = next_release()
    print('saving updates to ChangeLog')
    run('git commit ChangeLog -m "[RELEASE] Update to version v{}"'.format(ver), hide=True)
    sha = run('git log -1 --pretty=format:"%h"', hide=True).stdout
    run('git tag -a "{ver}" -m "version {ver}" {sha}'.format(ver=ver, sha=sha), hide=True)
    package()
    write_changelog()
    run('git tag -d {}'.format(ver), hide=True)
    run('git commit --all --amend --no-edit', hide=True)


@task
def publish(idx=None):
    """Publish packaged distributions to pypi index"""
    if idx is None:
        idx = ''
    else:
        idx = '-r ' + idx
    run('python setup.py register {}'.format(idx))
    run('twine upload {} dist/*.whl dist/*.egg dist/*.tar.gz'.format(idx))


@task
def release(major=False, minor=False, patch=True, pypi_index=None):
    """Overall process flow for performing a release"""
    relver = next_release(major, minor, patch)
    start_rel_branch(relver)
    prepare_release(relver)
    finish_rel_branch(relver)
    publish(pypi_index)
