Sample Configuration
====================
::

        [DEFAULT]
        
        #
        # Options defined in seedbox.options
        #
        
        # **REQUIRED**  Base path (string value)
        #base_path=<None>
        
        # Location torrent client stores data files (string value)
        #base_client_path=<None>
        
        # **REQUIRED**  Location of the .torrent files (string value)
        #torrent_path=<None>
        
        # **REQUIRED**  Location(s) of the media files (list value)
        #media_paths=<None>
        
        # **REQUIRED**  Location of the downloading torrents (string value)
        #incomplete_path=<None>
        
        # **REQUIRED**  Location to temp media copies for syncing to library (string value)
        #sync_path=<None>
        
        # Location(s) of additional plugins (list value)
        #plugin_paths=
        
        # List of phases to disable for execution (prepare, activate, complete) (list
        # value)
        #disabled_phases=
        
        # List of video filetypes to support. (ignore others) (list value)
        #video_filetypes=.avi,.mp4,.mkv,.mpg
        
        # List of compressed filetypes to support. (ignore others) (list value)
        #compressed_filetypes=.rar
        
        # Maximum number of times to retry a failed torrent (integer value)
        #max_retry=5
        
        
        [filesync]
        
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
        
        # flag to enable parallel threads of rsync (boolean value)
        #enable_parallel=true
        
        
        [plugins]
        
        #
        # Options defined in seedbox.tasks.filecopy
        #
        
        # disable this plugin (boolean value)
        #copy_file_v1_disabled=false
        
        
        #
        # Options defined in seedbox.tasks.filedelete
        #
        
        # disable this plugin (boolean value)
        #delete_file_v1_disabled=false
        
        
        #
        # Options defined in seedbox.tasks.filesync
        #
        
        # disable this plugin (boolean value)
        #sync_file_v1_disabled=false
        
        
        #
        # Options defined in seedbox.tasks.fileunrar
        #
        
        # disable this plugin (boolean value)
        #unrar_file_v1_disabled=false
        
        
        #
        # Options defined in seedbox.tasks.prepare
        #
        
        # disable this plugin (boolean value)
        #copy_file_v2_disabled=false
        
        # disable this plugin (boolean value)
        #unrar_file_v2_disabled=false
        
        
        #
        # Options defined in seedbox.tasks.validate_phase
        #
        
        # disable this plugin (boolean value)
        #phase_validator_v1_disabled=false
        
        
        [prepare]
        
        #
        # Options defined in seedbox.tasks.prepare
        #
        
        # storage (GB) allocated to seedbox slot (integer value)
        #slot_size=50
        
        # minimum storage (GB) threshold before processing stops (integer value)
        #min_storage_threshold=5
        
        # flag to override checking storage, if True then `min_storage_threshold` must
        # have positive value (boolean value)
        #storage_check_override=false
        
        # storage system offset (traditional = 1024 bytes), (si = 1000 bytes) (string
        # value)
        #storage_system=traditional
        
        
        [prsync]
        
        #
        # Options defined in seedbox.tasks.filesync
        #
        
        # Max number of parallel threads (integer value)
        #rsync_threads=5
        
        # Timeout (secs) (0 = no timeout) (integer value)
        #thread_timeout=0
        
        # Output directory for stdout files (string value)
        #stdout_dir=<None>
        
        # Output directory for stderr files (string value)
        #stderr_dir=<None>
        
        # Write output to stdout (boolean value)
        #print_out=false
        
        # Buffer stdout until thread ends (boolean value)
        #stdout_buffer=false
        
        # Buffer stderr until thread ends (boolean value)
        #stderr_buffer=false
        
        # Output verbose details about exceptions (boolean value)
        #stderr_verbose=true


