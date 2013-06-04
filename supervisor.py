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
    script='/home/slodha/sql2es.py',
    port=9288
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

tornado.options.define('workers_count', 4, int)
tornado.options.define('logfile_template', None, str)
tornado.options.define('pidfile_template', None, str)
tornado.options.define('start_check_timeout', 3, int)


import os.path
import os


def is_alive(port):
    try:
        path = options.pidfile_template % dict(port=port)
        pid = int(file(path).read())
        if os.path.exists("/proc/{0}".format(pid)):
            return True
        return False
    except Exception:
        return False


def is_running(port):
    try:
        urllib2.urlopen('http://localhost:%s/status/' % (port))
        return True
    except urllib2.URLError:
        return False
    except urllib2.HTTPError:
        return False

def start_worker(script, port):
    if is_alive(port):
        logging.warn("another process already started on %s", port)
        sys.exit(1)
    logging.debug('start worker %s', port)

    args = [script,
            '--port=%s' % (port,),
            '--pidfile=%s' % (options.pidfile_template % dict(port=port),)]

    if options.logfile_template:
        args.append('--logfile=%s' % (options.logfile_template % dict(port=port),))

    return subprocess.Popen(args)

def stop_worker(port):
    logging.debug('stop worker %s', port)
    path = options.pidfile_template % dict(port=port)
    if not os.path.exists(path):
        logging.warning('pidfile %s does not exist. dont know how to stop', path)
    try:
        pid = int(file(path).read())
        os.kill(pid, signal.SIGTERM)
    except OSError:
        pass
    except IOError:
        pass
    except ValueError:
        pass

def rm_pidfile(port):
    pid_path = options.pidfile_template % dict(port=port)
    if os.path.exists(pid_path):
        try:
            os.remove(pid_path)
        except :
            logging.warning('failed to rm  %s', pid_path)

def stop():
    if any(map_workers(is_running)):
        logging.warning('some of the workers are running; trying to kill')

    for i in xrange(int(options.stop_timeout) + 1):
        map_workers(stop_worker)
        time.sleep(1)
        if not any(map_workers(is_alive)):
            map_workers(rm_pidfile)
            break
    else:
        logging.warning('failed to stop workers')
        sys.exit(1)

def start(script, port):
    start_worker(script, port)
    time.sleep(options.start_check_timeout)

def status(expect=None):
    res = map_workers(is_running)

    if all(res):
        if expect == 'stopped':
            logging.error('all workers are running')
            return 1
        else:
            logging.info('all workers are running')
            return 0
    elif any(res):
        logging.warn('some workers are running!')
        return 1
    else:
        if expect == 'started':
            logging.error('all workers are stopped')
            return 1
        else:
            logging.info('all workers are stopped')
            return 0

def supervisor(script, port):
    (cmd,) = tornado.options.parse_command_line()

    logging.getLogger().setLevel(logging.DEBUG)
    tornado.options.enable_pretty_logging()

    if cmd == 'start':
        start(script, port)
        sys.exit(status(expect='started'))

    if cmd == 'restart':
        stop()
        start(script, port)
        sys.exit(status(expect='started'))

    elif cmd == 'stop':
        stop()
        sys.exit(status(expect='stopped'))

    elif cmd == 'status':
        status()

    else:
        logging.error('either --start, --stop, --restart or --status should be present')
        sys.exit(1)
