class VogelerMessaging(object):
    """
    Defines a generic interface to a queue
    """
    def __init__(self, *args, **kwargs):
        pass

    def setup_messaging(self, *args, **kwargs):
        pass

    def setup_server(self, *args, **kwargs):
        pass

    def setup_client(self, *args, **kwargs):
        pass

    def message(self, *args, **kwargs):
        pass

    def monitor(self, *args, **kwargs):
        pass

    def close(self, *args, **kwargs):
        pass
# vim: set ts=4 et sw=4 sts=4 sta filetype=python :
