"""
Wrapper for sandman; replacement for sandmanctl that provides additional
options not available via sandmanctl
"""
import logging

import click
from sandman import app
from sandman.model import activate

from seedbox import version


def print_version(ctx, value):
    """Print the current version of sandman and exit.
    :param ctx: application context
    :param value:
    """
    if not value:
        return
    click.echo('SeedboxManager v%s' % (version.version_string()))
    ctx.exit()


@click.command()
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
@click.option('--version', is_flag=True,
              callback=print_version, expose_value=False, is_eager=True)
@click.argument('URI', metavar='<URI>')
def run(generate_pks, show_pks, host, port, debug, uri):
    """Connect sandman to <URI> and start the API server/admin
    :param generate_pks: Have sandman generate primary keys for tables
    without one
    :param show_pks: Have sandman show primary key columns in the admin view
    :param host: Hostname of database server to connect to
    :param port: Port of database server to connect to
    :param debug: Enable debug output from webserver
    :param uri: database uri
    interface."""
    app.config['SQLALCHEMY_DATABASE_URI'] = uri
    app.config['SANDMAN_GENERATE_PKS'] = generate_pks
    app.config['SANDMAN_SHOW_PKS'] = show_pks
    app.config['SERVER_HOST'] = host
    app.config['SERVER_PORT'] = port
    activate(name='SeedboxManager Admin', browser=False)

    # set logging to dump output if in debug mode
    reqlogger = logging.getLogger('werkzeug')
    reqlogger.setLevel(logging.ERROR)
    if debug:
        reqlogger.setLevel(logging.DEBUG)

    app.run(host=host, port=int(port), debug=debug)
