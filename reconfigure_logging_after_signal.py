"""Reload logging configuration from file after sending a SIGUSR1 to the program.

$ kill -SIGUSR1 $PID

https://docs.python.org/3/library/logging.config.html#logging-config-fileformat

Example log.conf

[loggers]
keys=root,other

[handlers]
keys=stdoutHandler,stdoutHandler2

[formatters]
keys=simpleFormatter,simpleFormatter2

[logger_root]
level=DEBUG
handlers=stdoutHandler

[logger_other]
level=WARNING
handlers=stdoutHandler2
qualname=__main__.my_module
propagate=0

[handler_stdoutHandler]
class=StreamHandler
level=DEBUG
formatter=simpleFormatter
args=(sys.stdout, )

[formatter_simpleFormatter]
format=%(name)s - %(levelname)s - %(message)s - %(asctime)s

[handler_stdoutHandler2]
class=StreamHandler
level=DEBUG
formatter=simpleFormatter2
args=(sys.stdout, )

[formatter_simpleFormatter2]
format=My other formatter: %(name)s - %(levelname)s - %(message)s

"""

import io
import logging
import logging.config
import os
import signal
import time

LOGGING_CONF = 'log.conf'

def read_log_config():
    logging.warning('Updating logging config')
    if os.path.exists(LOGGING_CONF):
        log_conf = LOGGING_CONF
    else:
        # Default format if log.conf is missing
        log_conf = io.StringIO('''
        [loggers]
        keys=root

        [handlers]
        keys=stdoutHandler

        [formatters]
        keys=simpleFormatter

        [logger_root]
        level=WARNING
        handlers=stdoutHandler

        [handler_stdoutHandler]
        class=StreamHandler
        level=DEBUG
        formatter=simpleFormatter
        args=(sys.stdout, )

        [formatter_simpleFormatter]
        format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
        ''')

    logging.config.fileConfig(log_conf, disable_existing_loggers=False)

def main():
    signal.signal(signal.SIGUSR1, lambda _signal, _frame: read_log_config())

    read_log_config()
    logger = logging.getLogger(__name__)
    logger2 = logging.getLogger(__name__ + '.my_module')

    while True:
        logger.debug('my first debug')
        logger.warning('my first warning')
        logger.error('my first error')

        logger2.debug('my second debug')
        logger2.warning('my second warning')
        logger2.error('my second error')

        time.sleep(2)


if __name__ == '__main__':
    print('PID:', os.getpid())
    main()
