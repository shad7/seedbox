"""Wrapper for sandman

replacement for sandmanctl that provides additional options
not available via sandmanctl
"""
import logging
import os

import click
from oslo_config import cfg
from passlib.hash import sha256_crypt
import sandman
from sandman import model

from seedbox import options


def load_passfile():

    options.initialize([])

    pwfile = cfg.CONF.find_file('.admin_pass')
    if not pwfile:
        pwfile = os.path.join(cfg.CONF.config_dir, '.admin_pass')
    return pwfile


@sandman.auth.verify_password
def verify_password(username, password):
    if username != 'admin':
        return False
    pw = None
    with open(load_passfile(), 'r') as fd:
        pw = fd.read()
    return sha256_crypt.verify(password, pw)


@sandman.app.before_request
@sandman.auth.login_required
def before_request():
    pass


@click.group()
def cli():
    pass


@cli.command('passwd')
@click.password_option()
def save_password(password):
    """Set admin password for accessing admin UI"""
    with open(load_passfile(), 'w') as fd:
        fd.write(sha256_crypt.encrypt(password))


@cli.command()
@click.option('--generate-pks/--no-generate-pks', default=False,
              help='Have sandman generate primary keys for tables without one')
@click.option('--show-pks/--no-show-pks', default=False,
              help='Have sandman show primary key columns in the admin view')
@click.option('--host', default='0.0.0.0',
              help='Hostname of database server to connect to')
@click.option('--port', default=5000,
              help='Port of database server to connect to')
@click.option('--debug', default=False,
              help='Enable debug output from webserver')
@click.argument('URI', metavar='<URI>')
def run(generate_pks, show_pks, host, port, debug, uri):
    """Start the admin UI for managing data

    <URI> is the database connection uri
    ex. sqlite:////path/to/file
    """
    sandman.app.config['SQLALCHEMY_DATABASE_URI'] = uri
    sandman.app.config['SANDMAN_GENERATE_PKS'] = generate_pks
    sandman.app.config['SANDMAN_SHOW_PKS'] = show_pks
    sandman.app.config['SERVER_HOST'] = host
    sandman.app.config['SERVER_PORT'] = port
    model.activate(name='SeedboxManager Admin', browser=False)

    # set logging to dump output if in debug mode
    reqlogger = logging.getLogger('werkzeug')
    reqlogger.setLevel(logging.ERROR)
    if debug:
        reqlogger.setLevel(logging.DEBUG)

    sandman.app.run(host=host, port=int(port), debug=debug)
