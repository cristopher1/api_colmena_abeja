class FileCopyError(Exception):
    def __init__(self, message, errors):
        super(Exception, self).__init__(message)
        self.errors = errors


class AudioLoadError(Exception):
    def __init__(self, message, errors):
        super(Exception, self).__init__(message)
        self.errors = errors

class AudioSizeError(Exception):
    def __init__(self, message, errors):
        super(Exception, self).__init__(message)
        self.errors = errors
