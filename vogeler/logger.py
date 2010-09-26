import logging
import logging.handlers

DEFAULT_LOG_FMT     = '[%(asctime)s: %(levelname)s] %(name)s (%(module)s) - %(message)s'
DEFAULT_LOG_LEVEL   = logging.WARN
DEFAULT_LOG_FILE    = None

log = logging.getLogger()

class LogWrapper():
    """
    Wrapper class for logging

    >>> import logger
    >>> log = logger.LogWrapper().logger()
    >>> log.warn("foo")
    [2010-09-24 14:10:50,611: WARNING] MainProcess - foo
    >>> log = logger.LogWrapper(level="DEBUG")
    >>>

    """

    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

    def __init__(self, name='vogeler', logfile=None, **kwargs):

        self._name = name
        self._logfile = logfile

        if kwargs.has_key("config"):
            """Do some config magic by reading the logging config"""

        if kwargs.has_key("level"):
            self._level = getattr(logging, kwargs["level"])
        else:
            self._level = DEFAULT_LOG_LEVEL

        #: handler assignment
        if kwargs.has_key("handler"):
            self._handler = kwargs["handler"]
        else:
            self._handler = "Stream"

        #: format assignment
        if kwargs.has_key("format"):
            self._format = format
        else:
            self._format = DEFAULT_LOG_FMT


    def _setup(self, **kwargs):

        #: set the handler
        if self._logfile is not None and self._handler == 'File':
            self._ch = logging.FileHandler(self._logfile)
        elif self._logfile is not None and self._handler == 'SysLog':
            self._ch = logging.handlers.SysLogHandler(self._logfile)
        else:
            self._ch = eval("logging.%sHandler()" % self._handler)

        self._ch.setFormatter(logging.Formatter(self._format))


        self._logger = logging.getLogger(self._name)
        self._logger.setLevel(self._level)
        self._logger.addHandler(self._ch)
        #: return the logger
        return self._logger

    def logger(self, **kwargs):
        return self._setup(**kwargs)
