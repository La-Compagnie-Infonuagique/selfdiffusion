import PIL.Image

from typing import Tuple
from selfdiffusion.transforms.exceptions import ImageResolutionError

def smallest_resize(image: PIL.Image.Image, resolution: Tuple[int,int]) -> Tuple[int,PIL.Image.Image]:
    """ Perform the smallest resize so that one of the dimensions is equal to 
    the output resolution. """

    # do not resize if one of the image dimension is already equal to one of 
    # output dimension
    if image.size[0] == resolution[0] or image.size[1] == resolution[1]:
        return image

    # ensure dimensions are larger then the output resolution
    valid_image_resolution = image.size[0] >= resolution[0] and image.size[1] >= resolution[1]
    assert valid_image_resolution, ImageResolutionError('Input image is smaller then the output resolution.')

    # compute the resize ratios
    scaling_along_x = image.size[0] / resolution[0]
    scaling_along_y = image.size[1] / resolution[1]

    def scale(image, ration):
        image_new_width = int(image.size[0] / ration)
        image_new_height = int(image.size[1] / ration)

        image = image.resize((image_new_width, image_new_height), resample=PIL.Image.LANCZOS)

        return image

    if scaling_along_x > scaling_along_y:
        # then we resize along y to have the smallest resize
        image = scale(image, scaling_along_y)
        return (1, image)
    else:
        # then we scale along the x axis
        image = scale(image, scaling_along_x)
        return (0, image)

def xywh2trbl(bbox: Tuple[int,int,int,int]) -> Tuple[int,int,int,int]:
    """ Convert a bbox from xywh to trbl format. """
    x, y, w, h = bbox
    top = y
    right = x + w
    bottom = y + h
    left = x

    return (top, right, bottom, left)
    


