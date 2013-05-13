seedbox
=======
After getting my first seedbox, the most glaring problem was a simple and efficient process that would handle
synchronizing files from the seedbox to my home library. I searched the internet for anything that would do
this for me so I could just use it. 

I found the following:
http://filesharingtalk.com/threads/436669-One-way-syncing-downloads-from-seedbox-to-home

The concept was quite simple so I leverage it as the start of my original idea. But found that I still needed
to handle copying files or decompressing files from my download directory to a directory to perform the sync.
Again another manual task that I would prefer not to have to do. At first it was a shell script but I really
wanted the caching/database aspect of the original script that does the sync. I started looking for frameworks
that could be easily extended via plugins for adding these features. The best option was http://flexget.com/ 
for doing easy extension. I really wasn't a big fan of YAML as it was a pain to work with and with all the
examples provided on flexget site, it was still difficult to get a good one configured. And I'm still not
ready to go full steam ahead with automated download of torrents. 

So I decided to build my own application that would do everything I needed. It is completely over-engineered
for what this really needed to do. I also used this as an opportunity to learn Python. After going through
a process to encapsulate all the database interactions, I decided to see what easy solutions already existed.
And then I wanted to add in a workflow to control which set of plugins were executed when.

Dependencies
-------------
* sqlite3: http://docs.python.org/2/library/sqlite3.html
* SQLObject (1.3.2): http://www.sqlobject.org/
* xworkflows (0.4.1): https://xworkflows.readthedocs.org/en/latest/
* rarfile (2.6): https://rarfile.readthedocs.org/en/latest/
* torrentparser: https://github.com/mohanraj-r/torrentparse
* lockfile: https://pypi.python.org/pypi/lockfile
* shutilwhich: https://pypi.python.org/pypi/shutilwhich
 
How does it all work?
---------------------
The manager handles setting up all the resources (configuration files, database, plugins/tasks, and workflow/process flow).
The pluginmanager handles defining the decorator required to identify a plugin method and the corresponding API for
registering itself. It will then load up all the plugins based on location and whether a method is properly decorated
and registered. The taskmanager handles setting up the workflow and executing all tasks/plugins configured for the phase
that the workflow is currently processing. The torrentmanager encapsulates calling the torrentparser to determine
what files have been downloaded and the database for storing/caching details about the torrents and associated media files.
   
On startup the manager will delegate to torrentmanager to establish a database connection and then load up any new
torrents. Then manager will delegate to taskmanager to execute all the plugins for each of the phases to complete the
end to end process flow.
  
Phases and Built-in Tasks
-------------------------- 
* prepare: filecopy and fileunrar
* activate: filesync
* complete: filedelete

filecopy: copy supported media files related to torrents from download directory to sync directory
fileunrar: decompress rar media files related to torrents from download directory to sync directory
filesync: rsync files in sync directory to remote server location
filedelete: delete media files from sync directory after successful sync to remote server location

Configuration
--------------
By default it will look for a configuration file named seedbox.cfg located in the following locations:
* current working directory
* USER_HOME_DIRECTORY/.seedbox/seedbox.cfg
* site-wide install directory (do not recommend this except for really general purpose info)

Required configuration inputs:
* torrent_path (actual .torrent file location)
* incomplete_path (location where files are initially downloaded to)
* media_paths (list of paths) (location where files are typically moved after downloading completes)
* sync_path

Optional configuration inputs:
* plugin_paths (list of paths)
* disabled_phases (list of phases, see above; to disable ALL plugins for a specific phase or execute only a single phase)

Optional configuration for all plugins:
* disabled=yes  (so you can disable a specific plugin)

syncfile (required)
* remote_path

syncfile (optional)
* verbose (DEFAULT: false)
* progress (DEFAULT: false)
* perms (DEFAULT: false)
* delayupdates (DEFAULT: false)
* recursive (DEFAULT: false)
* chmod (DEFAULT: ugo+rwx)
* identity (SSH key pub file)
* port (SSH port: default 22)

Logging
--------
Supports python logging framework. All modules use <code>__name__</code> (package.module) so you can enable or disable based on your choice.
For developers, you can put a logging configuration file (logging.cfg) in the same location as the seedbox.cfg file and it will
configure logging using that file.


