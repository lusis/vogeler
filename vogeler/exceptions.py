class VogelerException(Exception):
    """Base class for all exceptions"""

class VogelerPersistenceException(VogelerException):
    """Exception for an error in the persistence engine"""

class VogelerServerException(VogelerException):
    """Exception for an error in the server component"""

class VogelerClientException(VogelerException):
    """Exception for an error in the client component"""

class VogelerRunnerException(VogelerException):
    """Exception for an error in the runner component"""

class VogelerMessagingException(VogelerException):
    """Exception for an error in the messaging component"""

class VogelerPluginException(VogelerException):
    """Exception for an error in the plugin component"""

class VogelerEncryptionException(VogelerException):
    """Exception for an error in the encryption component"""

# vim: set ts=4 et sw=4 sts=4 sta filetype=python :
