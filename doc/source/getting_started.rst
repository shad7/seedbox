Getting Started
===============

Create `virtualenv <http://www.virtualenv.org/en/latest/>`_ ::

    virtualenv ~/seedbox/

Start `virtualenv <http://www.virtualenv.org/en/latest/>`_ ::

    cd ~/seedbox
    source bin/activate

Install `SeedboxManager <https://pypi.python.org/pypi/SeedboxManager>`_ in the virtualenv::

    mkdir etc
    pip install SeedboxManager

Running SeedboxManager::

    seedmgr

Running SeedboxManager from crontab::

    crontab -e
    @hourly /home/USER/seedbox/bin/seedmgr >> /home/USER/seedbox/etc/seedbox/cron-sync.log 2>&1

.. note::

    As part of installing in virtualenv the sample configuration files will be installed into the
    **~/seedbox/etc/seedbox** folder.

Starting Admin UI and REST API::

    dbadmin passwd --password <your_password>
    dbadmin run sqlite:////home/USER/.seedbox/torrent.db >> /home/USER/seedbox/etc/seedbox/admin.log 2>&1


Available Tasks by Phase
------------------------

**Phases and Built-in Tasks**


.. list-table::
    :widths: 15 15 40
    :header-rows: 1

    * - Phase
      - Task
      - Description
    * - prepare
      - filecopy
      - copy supported media files related to torrents from download directory to sync directory
    * - 
      - fileunrar
      - decompress rar media files related to torrents from download directory to sync directory
    * - activate
      - filesync
      - rsync files in sync directory to remote server location
    * - complete
      - filedelete
      - delete media files from sync directory after successful sync to remote server location


**Congiguration**

Possible configuration file locations (General to specific)::

    /etc
    /etc/seedbox
    # if virtualenv used
    ~/seedbox/etc
    ~/seedbox/etc/seedbox
    ~
    ~/.seedbox
    <current working directory>

.. note::

    configuration filename: **seedbox.conf**

    virtualenv approach is the recommended approach. Multiple configuration files are supported such
    that each supported folder is checked for a configuration file and loaded from most general
    to more specific. Each successive file will override values from the previous.

    The folder of the most specific configuration file found will be considered the resource folder 
    where all log files are stored by default.

Command line interface::

        usage: seedmgr [-h] [--config-dir DIR] [--config-file PATH] [--cron]
                       [--logconfig LOG_CONFIG] [--logfile LOG_FILE]
                       [--loglevel LOG_LEVEL] [--version] [--nocron]

        optional arguments:
          -h, --help            show this help message and exit
          --config-dir DIR      Path to a config directory to pull *.conf files from.
                                This file set is sorted, so as to provide a
                                predictable parse order if individual options are
                                over-ridden. The set is parsed after the file(s)
                                specified via previous --config-file, arguments hence
                                over-ridden options in the directory take precedence.
          --config-file PATH    Path to a config file to use. Multiple config files
                                can be specified, with values in later files taking
                                precedence. The default files used are: None.
          --cron                Disable console output when running via cron
          --logconfig LOG_CONFIG
                                specific path and filename of logging configuration
                                (override defaults)
          --logfile LOG_FILE    specify name of log file default: None
          --loglevel LOG_LEVEL  specify logging level to log messages: None
          --version             show program's version number and exit
          --nocron              The inverse of --cron


:doc:`seedbox-config`
        A generated configuration file that contains each option a designation for required,
        a help message, default value, and associated type.


.. toctree::
    :hidden:

    seedbox-config
