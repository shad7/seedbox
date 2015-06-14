Sample Configuration
====================
::

        [DEFAULT]
        
        #
        # Options defined in seedbox.options
        #
        
        # **REQUIRED** Base path (string value)
        #base_path=<None>
        
        # Location torrent client stores data files (string value)
        #base_client_path=<None>
        
        
        [database]
        
        #
        # Options defined in seedbox.db
        #
        
        # The connection string used to connect to the database (string value)
        #connection=sqlite:///$config_dir/torrent.db
        
        # Timeout before idle sql connections are reaped (integer value)
        #idle_timeout=3600
        
        # Verbosity of SQL debugging information. 0=None, 100=All (integer value)
        #connection_debug=0
        
        
        [process]
        
        #
        # Options defined in seedbox.process.flow
        #
        
        # name of tasks associated with prepare phase (list value)
        #prepare=
        
        # name of tasks associated with activate phase (list value)
        #activate=
        
        # name of tasks associated with complete phase (list value)
        #complete=
        
        
        #
        # Options defined in seedbox.process.manager
        #
        
        # max processes to use for performing sync of torrents (integer value)
        #max_processes=4
        
        
        [tasks]
        
        #
        # Options defined in seedbox.tasks.base
        #
        
        # Location to temp media copies for syncing to library (string value)
        #sync_path=/tmp/sync
        
        
        [tasks_filesync]
        
        #
        # Options defined in seedbox.tasks.filesync
        #
        
        # rsync dryrun option (boolean value)
        #dryrun=false
        
        # rsync verbose option (boolean value)
        #verbose=false
        
        # rsync progress option (boolean value)
        #progress=false
        
        # rsync perms option (boolean value)
        #perms=true
        
        # rsync delayupdates option (boolean value)
        #delayupdates=true
        
        # rsync recursive option (boolean value)
        #recursive=true
        
        # rsync chmod option (string value)
        #chmod=ugo+rwx
        
        # rsync-ssh identity option (ssh key) (string value)
        #identity=<None>
        
        # rsync-ssh port (string value)
        #port=22
        
        # User name on remote system (ssh) (string value)
        #remote_user=<None>
        
        # Host name/IP Address of remote system (string value)
        #remote_host=<None>
        
        # rsync destination path (string value)
        #remote_path=<None>
        
        
        [tasks_synclog]
        
        #
        # Options defined in seedbox.tasks.subprocessext
        #
        
        # Output directory for stdout files (string value)
        #stdout_dir=$config_dir/sync_out
        
        # Output directory for stderr files (string value)
        #stderr_dir=$config_dir/sync_err
        
        # Write output to stdout (boolean value)
        #stdout_verbose=false
        
        # Output verbose details about exceptions (boolean value)
        #stderr_verbose=true
        
        
        [torrent]
        
        #
        # Options defined in seedbox.torrent
        #
        
        # **REQUIRED** Location of the .torrent files (string value)
        #torrent_path=<None>
        
        # **REQUIRED** Location(s) of the media files (list value)
        #media_paths=<None>
        
        # **REQUIRED** Location of the downloading torrents (string value)
        #incomplete_path=<None>
        
        # List of video filetypes to support. (ignore others) (list value)
        #video_filetypes=.avi,.mp4,.mkv,.mpg
        
        # List of compressed filetypes to support. (ignore others) (list value)
        #compressed_filetypes=.rar
        
        # Minimum file size of a media file (integer value)
        #minimum_file_size=75000000
