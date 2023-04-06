import click

from selfdiffusion.sources.bing import Bing
from selfdiffusion.utils import create_target
from selfdiffusion.utils import image_loader
from selfdiffusion.utils import image_saver
from selfdiffusion.log import logger
from halo import Halo
from pathlib import Path

@click.group()
def main():
    pass

@main.command()
@click.argument('query')
@click.option('--limit', default=10, help='Number of images to download')
@click.option('--target', default='.', help='Output directory')
@click.option('--filter-adult', default=False, help='Filter adult content')
@click.option('--timeout', default=60, help='Timeout for requests')
@create_target
def bing(query, limit, target, filter_adult, timeout):
    """ Download images from Bing """

    # create target directory if it does not exist
    target_path = Path(target)

    spinner = Halo(text='Downloading images', spinner='arc')
    spinner.start()

    if  not filter_adult:
        adult = 'off'
    else:
        adult = 'on'

    bing = Bing(query, limit, target_path.absolute(), adult, timeout, "photo", verbose=False)
    count = bing.run()

    spinner.succeed(f'Downloaded {count} images in {str(target)}')
    return

@main.command()
@click.argument('src')
@click.argument('target')
@click.option('--resolution', help='output images resolution', type=(int,int), default=(512,512))
@create_target
def person(src, target, resolution):
    """ Create a dataset by extracting people from images and resizing to a
    chosen output resolution. Uses a simple heuristic to appropriately crop the
    face of the person to make the dataset more suitable for fine-tuning
    intended for avatar creation."""

    spinner = Halo(text='Loading machine learning models', spinner='dots')
    spinner.start()

    from selfdiffusion.pipelines import person_pipeline

    spinner.succeed('Loaded machine learning models')

    # get an image loader from the src
    images = image_loader(src)

    # process the images with a pipeline
    persons = person_pipeline(images, resolution)

    # save the images to the target
    image_saver(persons, target)
    logger.info('Done processing images')

    return 

if __name__ == '__main__':
    main()