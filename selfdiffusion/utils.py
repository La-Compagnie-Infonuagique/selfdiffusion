import PIL.Image
import functools

from typing import Iterator, Tuple
from pathlib import Path


def create_target(func):
    """ Decorator that creates a target folder if it does not exist before 
    running the function. """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # get the target parameter value
        target_param = kwargs.get('target')
        
        # create a Path object from the target parameter
        target_path = Path(target_param)
        
        # check if the folder already exists
        if not target_path.is_dir():
            # create the folder recursively
            target_path.mkdir(parents=True)
        
        # call the original function
        return func(*args, **kwargs)
    return wrapper


def image_loader(src: str) -> Iterator[Tuple[Path,PIL.Image.Image]]:
    """ Iterator for images found in src."""

    # Get all paths that are files inside the path.
    image_paths = [file_path for file_path in Path(src).iterdir() if file_path.is_file()]

    for image_path in image_paths:
        yield image_path.name, PIL.Image.open(image_path)

def image_saver(images: Iterator[Tuple[Path,PIL.Image.Image]], target: Path) -> None:
    """ Saves images to target folder. """

    # create a Path object from the target parameter
    target_path = Path(target)

    for path, image in images:
        # save the image to the target folder
        image.save(target_path / path)
    return
