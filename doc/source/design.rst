Design
======

.. raw:: html

        <div class="mxgraph" style="position:relative;overflow:hidden;width:1006px;height:496px;"><div style="width:1px;height:1px;overflow:hidden;">zVrBkqM2EP0aVyWHnTLGxp7jzmazuaQqVXNIckrJoDGqAUSEWHv267cF3ViswMMMGO/J0IBQP73u12q88D+lpy+K5fGfMuLJYrWMTgv/t8Vq5XnBPfwYy0ttCbxdbTgoEeFNZ8Oj+MbRuERrKSJetG7UUiZa5G1jKLOMh7ple5JJ+xU5O9DwZ8NjyBLX+reIdPyjE+bCH1wcYnzPbhXUFwr9QmNE/ImVif5QmeCauZwyGgu9Oi1xAL8+f8Fzb41P5CxrTemblGnLoHhxxgrdFTgtfMleqoirlikR2bONm/8Z1k5JCQ+ao/T0iSdm/Whp6sd+77nawKV41np13wNrdPcrS0qcu4Mfz6KPSskjnIUJKwoRLvwHfhL6H7AATNXxv+b4bmPOMq1ezCWPTuiaMzecbiFLFeLLNrh+mqkDx9sCnCSPWmRBj75wmXJ4S7UECdPia3sRGMJ7aO474wEHCEk3PBuctAVPmIiFIZl/YuDfL5WDxi0pMv2rg90xFpo/5qxy7wgBCc8cFOcZjsuV5hSZPfi4buID98EWuYpreY9BcbQihXgWW0ESoG0UMpg0LGQKWDNtYZMrGfKiuDKffiDF6wTD52yC1aSbgU8BRtelcDsoWea99MCsyvZ0O67lcNqs1zgU0Wa1dmiz7qINpN0JeIPxbSHQx5MiZrk55CeYwEMky9pnQwOAKIu4GdKcdQWZgU6AjnxMxMEk7r3U2iRsiD5WT/i14KvXyoVxFphcnhylen5KIGqGpJi9eazHow7He7lCaopUWc2YYFaY3CwINCtAKx2aaCWfm+oAnHkg4qQnWOw8vjOwhTEkp7sU6gDxIZJhmVaoWGwYB5QXBJSQECvP25HFgmuHaXPydOyi1YRVk5BTlkG5pN7IoHeGCTFo24ZlTgpt8F22eivONFSvb9OkWodQlRoZauTK1iQ8/YsrAfOtij305KJQEeNspUKTLVR1UMwhVDhpCzp+4mE5JXaOnk+IHcXDbcDDMSzwWBQBcLBRssLx/5JTjHWjGQmWygwGbdCsIOuujjqYGLEiRpGcjIE1sHOA6Jbes5dKO6yMqFKiOVnJa3Xfkbw8f4LsRbseWwClqqY+aaVUSWBvwTRIAipYLlZK14PJRSmRzOyyR9RJRL3h8r9p19Q+1k1zqFyAJLWln6licp3vWeSmALoZADs33c6eKbx1syGl+o9aK/Z+YbOhu1pxQFXhGBS2brFzBRRqrPthWDYOUs50UfA3Xblgjc+NCgV3cxntf7ZsWS/UxWx5RYTcyiRv9bPycj+si9WdOhsWDt9iLtFXJMzG7UZcL3W6u6a07pePAuSdBMAnSBRvgMfOrfpnzCHtxkpXoqT5jfGRujP2ppCFMSxds+YF1Fnmu8SYTkPEAARWwMWLuaKFC6H/euwgN+47OgzEg6m5sXUbvtfgRmUbIrN2cUnITc2VrVtaXcHnGtnL5fPVPHQbjUYxlyLNE256ZLCpk/ixwnJ6sE5KsApt6AqSNk42q7W4EUpuzkCdGNOLZFnJkv9kzlUN8lskpAeMpgxrl6Iocy0JwVFtqPwpylB3P1ZVGD8pUFRo3QApf0DBPtmnsv7WWpcC2T0gyhB2E4g0dP4PsmsXNOjoRmAxQ5wlvMxBgC82115rVTb9tPoStLEtSAd+auz6lo22G0DnihkWPtCW7O4rvR+u1TvgoobXTeCC0/O/Lqpr1t9n/M/fAQ==</div></div>
        <script type="text/javascript" src="https://www.draw.io/embed.js?s=flowchart"></script>


Key Design Aspects
------------------

Leverage plugin pattern to provide implementations for Tasks and Database. All plugins are registered as entry points within
python setup for the project.


Tasks
^^^^^

:class:`seedbox.tasks.base.BaseTask` provides the base implementation for a Task. All Tasks must implement the following methods

        * is_actionable
                if the result is True then the Task will be executed
                else skip executing the Task.
        * execute
                provides the Task specific implementation; all exceptions are handled by the BaseTask to guarantee consistent
                error handling.

The BaseTask provides the ability to include additional media files for processing, and captures telemetry (execution time)
for each Task execution.


Database
^^^^^^^^

:class:`seedbox.db.base.Connection` provides the abstract definition for the interacting with a specific database implementation.
The base capabilities include

        * connection / session creation
        * create
        * update
        * delete
        * read
        * wipe data
        * backup data
        * upgrade model/schema


.. seealso::

        * `Dynamic Code Patterns Extending Your Applications with Plugins`_
        * `SQLAlchemy`_



.. _Dynamic Code Patterns Extending Your Applications with Plugins: http://stevedore.readthedocs.org/en/latest/essays/pycon2013.html
.. _SQLAlchemy: http://www.sqlalchemy.org/
