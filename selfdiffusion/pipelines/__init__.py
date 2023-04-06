import PIL.Image
from typing import Iterator, Tuple

from selfdiffusion.log import logger
from selfdiffusion.transforms.transforms import extract_person

def person_pipeline(images: Iterator[PIL.Image.Image], resolution: Tuple[int,int]) -> Iterator[PIL.Image.Image]:
    """ processes images in sequence and puts into a stream cropped images of person"""

    for path, image in images:
        # try to process the images one by one.
        try:
            # convert to RGB
            image = image.convert('RGB')
            # extract person
            image = extract_person(image, resolution)
            yield path, image
        except Exception as e:
            logger.warning(f"Could not process image {path} due to {e}.")
    return 