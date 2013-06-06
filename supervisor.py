#!/usr/bin/python2.7

'''
This is module for creating of init.d scripts for tornado-based
services

It implements following commands:
* start
* stop
* restart
* status
'''
import signal

import sys
import socket
import httplib
import logging
import subprocess
import time

from functools import partial

import tornado.options
from tornado.options import options

tornado.options.define('port', 0, int)
tornado.options.define('logfile', None, str)
tornado.options.define('pidfile', None, str)
tornado.options.define('process_name', None, str)
tornado.options.define('start_check_timeout', 3, int)
tornado.options.define('stop_timeout', 3, int)

import os
import os.path

logger = logging.getLogger('Logger')
logger.setLevel(logging.DEBUG)

#So that it doesn't log to console
logger.propagate = False

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
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect(('127.0.0.1', int(options.port)))
        s.shutdown(2)
        return True
    except:
        return False

def stop_process():
    logger.debug('Stopping %s Process' %options.process_name)
    path = options.pidfile
    if not os.path.exists(path):
        logger.warning('pidfile %s does not exist. Do not know how to stop', path)
    try:
        pid = int(file(path).read())
        os.kill(pid, signal.SIGTERM)
    except OSError:
        raise
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
            logger.warning('failed to remove  %s', pid_path)

def stop():
    if is_running():
        print 'Process is running; Trying to kill'
        logger.warning('Process is running; Trying to kill')

    for i in xrange(int(options.stop_timeout) + 1):
        stop_process()
        time.sleep(1)
        if not is_alive():
            rm_pidfile()
            break
    else:
        logger.warning('failed to stop Process')
        sys.exit(1)

def start(script):
    if is_alive():
        logger.warn("another process already started on %s", port)
        sys.exit(1)
    print 'Attempting to start %s on port: %s' %(options.process_name,options.port)
    logger.debug('Attempting to start %s on port: %s' %(options.process_name,options.port))

    args = [script,
            '--port=%s' % (options.port)]

    d = subprocess.Popen(args)
    #print d.pid
    f = open(options.pidfile,'w')
    f.write('%s' %d.pid)
    f.close()
    time.sleep(options.start_check_timeout)

def status(expect=None):
    if is_running():
        if expect == 'stopped':
            print 'ERROR : % was expected to be stopped, but it is still running.' %options.process_name
            logger.error('%s was expected to be stopped, but it is still running.' %options.process_name)
            return 1
        else:
            print '%s is running.' %options.process_name
            logger.info('%s is running.' %options.process_name)
            return 0
    else:
        if expect == 'started':
            print 'ERROR : % was expected to be started, but it is not running.' %options.process_name
            logger.error('%s was expected to be started, but it is not running.' %options.process_name)
            return 1
        else:
            print '%s is stopped.' %options.process_name
            logger.info('%s is stopped.' %options.process_name)
            return 0

def supervisor(script, config):
    tornado.options.parse_config_file(config)
    (cmd,) = tornado.options.parse_command_line()

    if not options.logfile:
        print 'Log file  must be defined in config file. Exiting.'
        sys.exit(1)
    else:
        #File handler to store logs
        fh = logging.FileHandler(options.logfile)
        fh.setLevel(logging.DEBUG)

        # create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)

        # add the handlers to the logger
        logger.addHandler(fh)

    if options.port == 0:
        logger.error('Port must be defined in config file and be Non zero. Exiting.')
        sys.exit(1)

    if not options.logfile:
        logger.error('Log file  must be defined in config file. Exiting.')
        sys.exit(1)

    if not options.pidfile:
        logger.error('ProcessID storage file must be defined in config file. Exiting')
        sys.exit(1)

    if not options.process_name:
        logger.error('Process Name must be defined in config file. Exiting')
        sys.exit(1)

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
        print 'Attempting to get status for %s. ' %options.process_name 
        status()

    else:
        logger.error('either --start, --stop, --restart or --status should be present')
        sys.exit(1)
