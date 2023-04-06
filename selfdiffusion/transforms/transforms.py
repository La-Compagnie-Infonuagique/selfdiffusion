import PIL.Image

from typing import Tuple

from selfdiffusion.transforms.utils import smallest_resize
from selfdiffusion.transforms.utils import xywh2trbl 
from selfdiffusion.transforms.ml import faces_location
from selfdiffusion.transforms.ml import persons_location
from selfdiffusion.transforms.exceptions import NonUniqueFaceError
from selfdiffusion.transforms.exceptions import NonUniquePersonError

def extract_person(image: PIL.Image.Image, resolution: Tuple[int,int]) -> PIL.Image.Image:
    """ Extract a person from an image and resize to a chosen output resolution. """

    # resie the image along the smallest dimension
    axis, image = smallest_resize(image, resolution)

    # resized along y direction:
    if axis == 1:

        # find the location of the face in the image
        faces = faces_location(image)

        # to extract a person, we need to have exactly one face
        assert len(faces) == 1, NonUniqueFaceError("The image does not contain exactly one face.")

        # extract the x coordinate of the face
        face_x, _ = faces[0]

         # compute the crop region based on the center of the face location.
        top = 0  # when we scale along y, we can only slide the crop region left - right.
        bottom = resolution[1]

        left =  face_x - resolution[0] // 2
        right = face_x + resolution[0] // 2

        if left < 0:
            left = 0
            right = resolution[0]

        if right > image.size[0]:
            right = image.size[0] 
            left = right - resolution[0]

        # crop the image
        image = image.crop((left, top, right, bottom))
    # resized along the x direction.
    else:
        # get the person from the resized image
        persons = persons_location(image)

        # there must be exactly one person in the image if we are to extract it
        assert len(persons) == 1, NonUniquePersonError("The image does not contain exactly one person.")

        # extract to top limit of the person bbox
        top, _, _, _ = xywh2trbl(persons[0])

        # compte the crop region based on the top limit of the person bbox
        left = 0 # when we scale along x, we can only slide the crop region up - down and so x has to be fixed at 0.
        right = resolution[0]
        bottom = top + resolution[1]

        # Adjust the boundaries if we are outside the image.
        if bottom > image.size[1]:
            bottom = image.size[1]
            top = bottom - resolution[1]

        # crop the image
        image = image.crop((left, top, right, bottom))

    # assert that the image is of the correct size
    assert image.size == resolution
    return image