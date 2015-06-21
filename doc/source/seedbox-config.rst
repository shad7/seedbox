Sample Configuration
====================
::

        [DEFAULT]

        # Base path (string value)
        #base_path = /home/username

        # Location torrent client stores data files (string value)
        #base_client_path = $base_path/torrents/data


        [database]

        # The connection string used to connect to the database (string value)
        #connection = sqlite:///$config_dir/torrent.db

        # Timeout before idle sql connections are reaped (integer value)
        #idle_timeout = 3600

        # Verbosity of SQL debugging information. 0=None, 100=All (integer
        # value)
        #connection_debug = 0


        [process]

        # max processes to use for performing sync of torrents (integer value)
        #max_processes = 4

        # name of tasks associated with prepare phase (list value)
        #prepare = filecopy, fileunrar

        # name of tasks associated with activate phase (list value)
        #activate = filesync

        # name of tasks associated with complete phase (list value)
        #complete = filedelete


        [tasks]

        # Location to temp media copies for syncing to library (string value)
        #sync_path = /tmp/sync


        [tasks_filesync]

        # rsync dryrun option (boolean value)
        #dryrun = false

        # rsync verbose option (boolean value)
        #verbose = false

        # rsync progress option (boolean value)
        #progress = false

        # rsync perms option (boolean value)
        #perms = true

        # rsync delayupdates option (boolean value)
        #delayupdates = true

        # rsync recursive option (boolean value)
        #recursive = true

        # rsync chmod option (string value)
        #chmod = ugo+rwx

        # rsync-ssh identity option (ssh key) (string value)
        #identity = /home/username/.ssh/my_home.key

        # rsync-ssh port (string value)
        #port = 22

        # User name on remote system (ssh) (string value)
        #remote_user = username

        # Host name/IP Address of remote system (string value)
        #remote_host = home.example.com

        # rsync destination path (string value)
        #remote_path = /media/downloads


        [tasks_synclog]

        # Output directory for stdout files (string value)
        #stdout_dir = $config_dir/sync_out

        # Output directory for stderr files (string value)
        #stderr_dir = $config_dir/sync_err

        # Write output to stdout (boolean value)
        #stdout_verbose = false

        # Output verbose details about exceptions (boolean value)
        #stderr_verbose = true


        [torrent]

        # Location of the .torrent files (string value)
        #torrent_path = /home/username/.config/state

        # Location(s) of the media files (list value)
        #media_paths = $base_client_path/completed

        # Location of the downloading torrents (string value)
        #incomplete_path = $base_client_path/inprogress

        # List of video filetypes to support. (ignore others) (list value)
        #video_filetypes = .avi,.mp4,.mkv,.mpg

        # List of compressed filetypes to support. (ignore others) (list
        # value)
        #compressed_filetypes = .rar

        # Minimum file size of a media file (integer value)
        #minimum_file_size = 75000000
