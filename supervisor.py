#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

'''
This is module for creating of init.d scripts for tornado-based
services

It implements following commands:
* start
* stop
* restart
* status

Sample usage:

=== /etc/init.d/sql2es ===
#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

from sql2es.supervisor import supervisor

supervisor(
    script='sql2es.py'
)
'''
import signal

import sys
import urllib2
import httplib
import logging
import subprocess
import time

from functools import partial

import tornado.options
import tornado_util.server
from tornado.options import options

tornado.options.define('port', 9288, int)
tornado.options.define('workers_count', 4, int)
tornado.options.define('logfile', '/var/log/SQL2ESCommand.log', str)
tornado.options.define('pidfile', '/var/run/SQL2ESCommand.pid', str)
tornado.options.define('start_check_timeout', 3, int)

import os
import os.path


def is_alive():
    try:
        path = options.pidfile
        pid = int(file(path).read())
        if os.path.exists("/proc/{0}".format(pid)):
            return True
        return False
    except Exception:
        return False


def is_running():
    try:
        urllib2.urlopen('http://localhost:%s/status/' % (options.port))
        return True
    except urllib2.URLError:
        return False
    except urllib2.HTTPError:
        return False    

def stop_process():
    logging.debug('Stopping SQL2ES Process')
    path = options.pidfile
    if not os.path.exists(path):
        logging.warning('pidfile %s does not exist. Do not know how to stop', path)
    try:
        pid = int(file(path).read())
        os.kill(pid, signal.SIGTERM)
    except OSError:
        pass
    except IOError:
        pass
    except ValueError:
        pass

def rm_pidfile():
    pid_path = options.pidfile
    if os.path.exists(pid_path):
        try:
            os.remove(pid_path)
        except :
            logging.warning('failed to remove  %s', pid_path)

def stop():
    if (is_running):
        logging.warning('Process is running; Trying to kill')

    for i in xrange(int(options.stop_timeout) + 1):
        stop_process()
        time.sleep(1)
        if not is_alive():
            rm_pidfile()
            break
    else:
        logging.warning('failed to stop Process')
        sys.exit(1)

def start(script):
    if is_alive():
        logging.warn("another process already started on %s", port)
        sys.exit(1)
    logging.debug('started SQL2ES on port: %s', options.port)

    args = [script,
            '--port=%s' % (options.port,),
            '--pidfile=%s' % (options.pidfile)]

    if options.logfile:
        args.append('--logfile=%s' % (options.logfile))

    subprocess.Popen(args)
    time.sleep(options.start_check_timeout)

def status(expect=None):
    if is_running():
        if expect == 'stopped':
            logging.error('SQL2ES is running.')
            return 1
        else:
            logging.info('SQL2ES is running.')
            return 0
    else:
        if expect == 'started':
            logging.error('SQL2ES is stopped')
            return 1
        else:
            logging.info('SQL2ES is stopped')
            return 0

def supervisor(script):
    (cmd,) = tornado.options.parse_command_line()

    logging.getLogger().setLevel(logging.DEBUG)
    tornado.options.enable_pretty_logging()

    if cmd == 'start':
        start(script)
        sys.exit(status(expect='started'))

    if cmd == 'restart':
        stop()
        start(script)
        sys.exit(status(expect='started'))

    elif cmd == 'stop':
        stop()
        sys.exit(status(expect='stopped'))

    elif cmd == 'status':
        status()

    else:
        logging.error('either --start, --stop, --restart or --status should be present')
        sys.exit(1)
