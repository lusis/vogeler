import logging
import logging.handlers

DEFAULT_LOG_FMT     = '[%(asctime)s: %(levelname)s] %(processName)s - %(message)s'
DEFAULT_LOG_LEVEL   =  'WARN'
DEFAULT_LOG_FILE    = None

def get_logger(logLevel=None, name=None):
    """
    Get an instance of :class:`logging.Logger`

    :param logLevel: Log level to use
    :param name: Name of this logger

    :returns: isntance of :class:`logging.Logger`
    """
    logger = logging.getLogger(name or "vogeler")
    if logLevel is not None:
        logger.setLevel(logLevel)
    return logger

def setup_logger(logLevel=DEFAULT_LOG_LEVEL, logFile=None,
                logFormat=DEFAULT_LOG_FMT, name='vogeler'):
    """
    Sets up a logger instance for logging

    :param logLevel: Log level to use.
    :param logFile: Log file to write.
    :param logFormat: Format of log messages
    :param name: Name of this logger

    :returns: instance of :class:`logging.Logger`
    """
    logger = get_logger(logLevel, name)

    if logFile is not None:
        ch = logging.FileHandler(logFile)
    else:
        ch = logging.StreamHandler()

    ch.setFormatter(logging.Formatter(logFormat))
    logger.addHandler(ch)
    return logger

# vim: set ts=4 et sw=4 sts=4 sta filetype=python :
