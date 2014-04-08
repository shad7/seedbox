"""
package pssh (copied from parelle-ssh and modified)

License

Copyright (c) 2009, Andrew McNabb
Copyright (c) 2003-2008, Brent N. Chun

All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.

    * Redistributions in binary form must reproduce the above
      copyright notice, this list of conditions and the following
      disclaimer in the documentation and/or other materials provided
      with the distribution.

    * The names of its contributors may not be used to endorse or
      promote products derived from this software without specific
      prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


Original Authors:

@author: Andrew McNabb <amcnabb at mcnabbs.org>

@author: Brent Chun <bnc at theether.org>


ChangeLog:

.. versionadded:: 2.3.1
    2012-02-02 Andrew McNabb <amcnabb at mcnabbs.org>

    * Fixed a problem where man pages were omitted from the tar file.
    * Note that this release makes no changes to the programs.


.. versionadded:: 2.3
    2012-01-24 Andrew McNabb <amcnabb at mcnabbs.org>

    * Added a --inline-stdout option (issue #57). Thanks to
      pablo.barbachano for the patch.
    * Added a PSSH_HOST environment variable (issue #62).
    * Added a --version option (issues #33 and #45).
    * Expanded the pssh man page and added man pages for all other
      commands (issues #10 and #55).
    * Fixed askpass on Mac OS X 10.6.7 (issue #50).
    * Many other small fixes.

.. versionadded:: 2.2.2
    2011-02-02 Andrew McNabb <amcnabb at mcnabbs.org>

    * Fixed two crashes (issues 35 and 36).  One affects Python <= 2.5
      and the other affects all of the scripts except pssh.

.. versionadded:: 2.2.1
    2011-01-26 Andrew McNabb <amcnabb at mcnabbs.org>

    * Fixed a crash when the -l option was used in conjunction with a
      hosts file (issue #34).

.. versionadded:: 2.2
    2011-01-21 Andrew McNabb <amcnabb at mcnabbs.org>

    * Added a basic man page for pssh (issue #10).
    * Fixed askpass to work correctly in the presence of non-password
      prompts from ssh (issue #23).
    * Updated the -O option so that it can be specified multiple times
      (issue #25).  Thanks to soham.mehta for the patch.
    * Fixed host file loader to give an error instead of a backtrace
      if a file is not found.
    * Fixed prsync's "-ssh-args" mangling of its argument (issue #24).
      Thanks to jbyers for the patch.
    * Fixed some variable names to appease pylint.  Thanks to solj for
      the patch.
    * Improved pscp to be able to copy multiple local files.  Thanks
      to Carlo Marcelo Arenas Belon for the patch.
    * Deprecated the PSSH_HOSTS environment variable that seems to
      cause more problems than it's worth.
    * Added the ability to set multiple hosts with a single -H flag
      (issue #26). Thanks to ilya@sukhanov.net for the patch.
    * Stopped passing "-q" to ssh by default (this masked error messages
      and reduced usability).
    * Removed automatic reading from stdin (deprecated in version 2.1).
      Please use the "-I" option instead.
    * Added meaningful exit status codes (issue #30).
    * Other minor fixes

.. versionadded:: 2.1.1
    2010-02-26 Andrew McNabb <amcnabb at mcnabbs.org>

    * Fixed a problem causing PSSH to crash with Python 2.4.

.. versionadded:: 2.1
    2010-02-24 Andrew McNabb <amcnabb at mcnabbs.org>

    * Added support for Python 3.0 and 3.1.  Although PSSH has only
      been lightly tested with Python 3, anything that doesn't work
      in Python 3 is officially a bug.
    * Added a "-H" option for specifying hosts one-by-one instead of
      or in addition to a hosts file.
    * Added "-x" and "-X" options for passing extra command-line
      arguments to ssh and rsync.  Also added a "-S" option to prsync
      for the special case of passing extra arguments to ssh
      (issue #2).
    * Added a "-I" option for specifying that pssh should read from
      standard input, and added a deprecation warning when standard
      input is used without this option (issue #12).
    * Made the command argument optional when the "-I" option is
      given, so a script can be passed to pssh on standard input
      (issue #5).
    * If a username or port is given, these are now included in the
      output filename, which allows different connections to be
      distinguished from each other (issue #7).
    * Added the pssh-askpass wrapper as a standalone script because
      setup.py was removing the executable bit from askpass.py.  This
      fixes a "permission denied" error when using the -A option
      (issue #8).
    * Fixed a problem where pssh was unnecessarily specifying a
      username (issue #14).
    * Fixed a delay due to a lost SIGCHLD signal.
    * Removed extra spaces between output chunks in outdir files
      (issue #6).  Thanks to knutsen for the fix.
    * Fixed a bug where pscp passed the wrong option for sending scp
      a custom port.  Thanks to Jan Rafaj for the patch.
    * Fixed prsync to send the port as an option to ssh (issue #1).
      Thanks to Ryan Brothers for the fix.

.. versionadded:: 2.0
    2009-10-20 Andrew McNabb <amcnabb at mcnabbs.org>

    * Rewrote communication code to be more efficient.  PSSH now
      operates with only one or two threads.
    * Added the ability to interrupt PSSH (with CTRL-c).
    * Added an option to prompt for a password.
    * Refactored code into a distinct library (psshlib).

.. versionadded:: 1.4.3
    2008-10-12 Brent N. Chun <bnc at theether.org>

    * Fixed bug in select_wrap.  If timeout is None (e.g., the
      default for prsync, etc.), then never time out.  Bug reported
      by Carlo Marcelo Arenas Belon (carenas at sajinet.com.pe).
    * Catch getopt exceptions and print usage as well as getopt
      exception string.  Contribution from Carlo Marcelo Arenas
      Belon (carenas at sajinet.com.pe).
    * Added contribution from Bas van der Vlies (basv at sara.nl)
      to allow comments in hosts file.  Comments must begin with
      (#) character (leading whitespace is also allowed).
    * Restore file status bugs after reading stdin in pssh.
    * Fixed typo bug in pslurp when using options and in non-recursive mode.
    * Removed conflicts with built-in names.

.. versionadded:: 1.4.2
    2008-09-01 Brent N. Chun <bnc at theether.org>

    * Fixed minor bug: select returns select.error on an error, not OSError.

.. versionadded:: 1.4.1
    2008-08-27 Brent N. Chun <bnc at theether.org>

    * Removed broken SIGCHLD handler.
    * Refining subprocess _cleanup dynamically to an empty lambda
      function since subprocess is not thread-safe and we already
      call wait on child processes ourselves anyway.
    * Adding missing verbose flag to rest of bin/* programs.

.. versionadded:: 1.4.0
    2008-08-24  Brent N. Chun <bnc at theether.org>

    * Fixed 64-bit bug in pslurp, pscp, prsync.  Previously, the
      default select timeout was sys.maxint, but this is a 64-bit
      value on 64-machines. Now using None when calling select when
      there is no timeout.  Bug reported by (buixor at gmail.com).
    * Catching EINTR and ignoring it for select, read, write in
      BaseThread class.
    * Fixed longopts for pnuke, prsync, pscp, pslurp, pssh (bug
      reported a Debian user via Andrew Pollock (apollock at
      debian.org)). Reference: "bug #481901: pssh: options mis-specified"
    * Added missing environment variables for options for pnuke,
      prsync, pscp, pslurp, pssh.

.. versionadded:: 1.3.2
    2008-06-04  Brent N. Chun <bnc at theether.org>

    * Added shortopts bug fix from Lev Givon
      (lev at columbia.edu) in bin/pssh.

.. versionadded:: 1.3.1
    2007-04-11  Brent N. Chun <bnc at theether.org>

    * Reverted I/O back to 1.2.2. style pssh I/O.

.. versionadded:: 1.3.0
    2007-04-10  Brent N. Chun <bnc at theether.org>

    * Switched to BSD license.
    * Added contributions from Deepak Giridharagopal (deepak at brownman.org)

        * Added ANSI color to pssh, pscp, etc. output.
        * Each status message now includes a timestamp.
        * Failures now indicate the cause (e.g., timeout, etc.)
        * Intermediate directories are created as needed for output.
        * Removed use of setsid in shell exec.
        * Using Exception objects rather than raw strings.
        * Added support for piping stdin to each ssh process.
        * Added -i option to pssh for "inlining" output to stdout.
        * Added Python setup.py file for a standard install.

.. versionadded:: 1.2.2
    2006-06-18  Brent N. Chun <bnc at theether.org>

    * Added patch from Dan Silverstein (dans at pch.net) to fix
      parsecmdline bug.

.. versionadded:: 1.2.1
    2005-12-31  Brent N. Chun <bnc at theether.org>

    * Changed sys.path so pssh can run without RPM install.
    * Changed RPM library files to install in /usr/local/lib/python
    * make install and make uninstall now work as
      expected for installations from source.

    2004-11-10  Brent N. Chun <bnc at intel-research.net>

    * Added patch from Dave Barr <barr at google.com>
    * Adds -a, -z flags to prsync

.. versionadded:: 1.1.1
    2004-10-05  Brent N. Chun <bnc at intel-research.net>

    * Default user is now current user in all programs (on
      suggestion from Jim Wight <j.k.wight at newcastle.ac.uk>).
    * Fixed path typo on prsync from 1.1.0 release

.. versionadded:: 1.1.0
    2004-10-04  Brent N. Chun <bnc at intel-research.net>

    * Added patch from Dave Barr <barr at google.com>

        * Adds an ssh options flag (-O) to prsync

    * Added patch from Chad Yoshikawa <chadyoshikawa at gmail.com>

        * Adds a print to stdout flag (-P) to pssh

.. versionadded:: 1.0.0
    2004-08-21  Brent N. Chun <bnc at intel-research.net>

    * All cmds now take -o, -e for stdout, stderr
    * Checking return values for all cmds
    * Factored common thread structure out of all cmds
    * Changed pslurp's dir for local to -L, rather than -o (stdout)

    2003-11-20  Brent N. Chun <bnc at intel-research.net>

    * Added handler for SIGCHLD
    * Wait for all threads before returning to main thread
    * Kill all straggler processes when done

.. versionadded:: 0.2.3
    2003-11-18  Brent N. Chun <bnc at intel-research.net>

    * Added pslurp (scp from remote nodes), updated to 0.2.3

    2003-11-12  Brent N. Chun <bnc at intel-research.net>

    * Fixed read bug, so all output is obtained.
    * Added timeout option (defaults to None for pscp/prsync)
    * Added verbose option for pssh/pnuke (this is -q or not)
    * Added environment variables for options
    * Fixed usage for pnuke

    2003-09-06  Brent N. Chun <bnc at intel-research.net>

    * Added -O for pssh, pscp, and pnuke for passing SSH options
    * Changed order of options in usage (required, optional)

    2003-09-06  Brent N. Chun <bnc at intel-research.net>

    * Added parallel rsync (prsync)
    * Added support for "host[:port] user" lines in hosts files
    * Factored a bit of code out into lib/python/psshutil.py

.. versionadded:: 0.1.0
    2003-08-16  Brent N. Chun <bnc at intel-research.net>

    * Initial version (0.1.0)

"""
