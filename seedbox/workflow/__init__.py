from oslo.config import cfg

OPTS = [
    cfg.ListOpt('plugin_paths',
                default=[],
                help='Location(s) of additional plugins'),
    cfg.ListOpt('disabled_phases',
                default=[],
                help='List of phases to disable for execution '
                     '(prepare, activate, complete)'),
    cfg.IntOpt('max_retry',
               default=5,
               help='Maximum number of times to retry a failed torrent'),
]

cfg.CONF.register_opts(OPTS, group='workflow')

CLI_OPTS = [
    cfg.BoolOpt('retry',
                default=False,
                help='only executes entries that failed previously'),
]

cfg.CONF.register_cli_opts(CLI_OPTS, group='workflow')

_INIT = False


def _initialize():
    """
    Load up all the plugins and then setup workflow to plugin mapping
    """
    global _INIT

    from seedbox.workflow import pluginmanager
    from seedbox.workflow import processmap

    # load up the plugins
    pluginmanager.load_plugins()

    # generate a map by phase of each of the plugins we just loaded
    for phase in processmap.get_run_phases():
        processmap.make_phasemap(phase, pluginmanager.get_plugins(phase))

    # now initialize the processmap for the workflow
    processmap.init()

    _INIT = True


def start():
    """
    Start workflow process; initialize if needed
    """
    if not _INIT:
        _initialize()

    from seedbox.workflow import wfmanager
    wfmanager.start()
