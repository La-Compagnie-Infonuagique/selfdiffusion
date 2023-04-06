class ImageResolutionError(Exception):
    """ Exception raised when an image is smaller then the output resolution. """
    pass

class NonUniqueFaceError(Exception):
    """ Exception raised when no unique face is detected in the image. """
    pass

class NonUniquePersonError(Exception):
    """ Exception raised when no unique person is detected in the image. """
    pass

