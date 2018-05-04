=====
dumpy
=====

Dumpy is a Python database backup script that uses configuration files to
specify databases to backup and options.  Backup scripts are classes which
define a `backup` method.

Each `BackupBase` subclass returns a `NamedTemporaryFile` object.  It's up to
any post processors to use this object in any way (e.g. copy it to another
location on the file system).

Post processors can be chained and all take the form::

	MyPostProcessor().process(file)

If the post process doesn't alter the file passed in it should return it
unchanged.

Example configuration file
==========================

The following is an idea of what the configuration file, located at
`~/.dumpy.cfg` might look like.  This is very likely to change::

	[database db1]
	type = mysql
	name = dbname1
	user = db1
	password = db1
	postprocessing = S3CheckExistingFile, TimestampRename, PrependDatabaseName, Bzip, FileSystemCopy, S3Copy, S3Rotating, Monitoring
	
	[database db2]
	type = postgresql
	name = dbname2
	user = db2
	password = db2
	postprocessing = TimestampRename, PrependDatabaseName, Bzip, FileSystemCopy, RotateFiles
	
	[mysqldump options]
	path = /opt/local/lib/mysql5/bin/mysqldump
	flags = -Q --opt --compact
	
	[pg_dump options]
	path = /opt/local/lib/postgresql83/bin/pg_dump

	[TimestampRename options]
	format = %%Y%%m%%d

	[Bzip options]
	path = /usr/bin/bzip2

	[S3 options]
	access_key = access_key
	secret_key = secret_key
	bucket = bucket
	prefix = path/to/directory

	[S3Copy options]
	db_name_dir = True or False

	[S3Rotating options]
	number = 5

	[FileSystemCopy options]
	directory = /path/to/directory/
	
	[RotateFiles options]
	directory = /path/to/directory/
	number = 5

	[prometheus]
	host = <prometheus push gateway host with port. Eg: localhost:9091>
	job_name = <value for label job>

    [S3CheckExistingFile]
    pattern = <can be a time format or a string>


Status
======

Beta.  This is working and being used as a backup on a few systems but likely
has bugs.

Motivation
==========

I've written my last database dump and backup script that I want to.  My hope
is that this will be a general and feature rich backup script that's easily
extendable and will work across multiple databases and backup schemes.

Installation
============

Download dumpy and put the dumpy module on your Python path.  A way to quickly
test dumpy might be::

	$ git clone git://github.com/robhudson/dumpy.git
	$ cd dumpy
	$ export PYTHONPATH=$PYTHONPATH:`pwd`

Create a config file like the one above in your home directory named `.dumpy.cfg`.

To run the `dumper.py` command::

	$ python /path/to/dumper.py

The `dumper.py` command takes the following options:

    -h, --help            Display help information
    -D DATABASE, --database=DATABASE
                          Dump only the specified database with matching config
                          name
    -v, --verbose         Display logging output
    -a, --all-databases   Dump all databases in the configuration file

TODO LIST
=========

- [x] Docker container
- [x] Unify S3 configs
- [ ] Update boto to version 3
- [ ] Update to python3
- [ ] Path to config file in options. Fallback to `~/.dumpy.cfg`
- [x] Add a way to monitoring the dump