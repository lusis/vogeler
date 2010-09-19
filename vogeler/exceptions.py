class VogelerException(Exception):
    """Base class for all exceptions"""

class VogelerPersistenceException(VogelerException):
    """Exception for an error in the persistence engine"""

class VogelerServerException(VogelerException):
    """Exception for an error in the server component"""

class VogelerClientException(VogelerException):
    """Exception for an error in the client component"""
    pass

class VogelerClientConnectionException(VogelerClientException):
    """Exception for an error attempting to connect to the message queue"""

class VogelerClientPluginException(VogelerClientException):
    """Exception for an error in the client component"""
    pass

class VogelerRunnerException(VogelerException):
    """Exception for an error in the runner component"""

class VogelerMessagingException(VogelerException):
    """Exception for an error in the messaging component"""

class VogelerPluginException(VogelerException):
    """Exception for an error in the plugin component"""
    pass

class VogelerPluginExecutionException(VogelerPluginException):
    """Exception for an error executing a plugin"""
    pass

class VogelerPluginAuthorizationException(VogelerPluginException):
    """Exception for an unauthorized plugin"""
    pass

class VogelerPluginRegistrationException(VogelerPluginException):
    """Exception for failed plugin registration"""
    pass

class VogelerPluginParsingException(VogelerPluginException):
    """Exception for plugin parsing."""
    pass

class VogelerPluginCompiledParsingException(VogelerPluginException):
    """Exception for compiled plugin parsing. Fatal error"""
    pass

class VogelerPluginCompilationException(VogelerPluginException):
    """Exception for plugin compilation. Fatal error"""

class VogelerEncryptionException(VogelerException):
    """Exception for an error in the encryption component"""

# vim: set ts=4 et sw=4 sts=4 sta filetype=python :
