import click

from selfdiffusion.sources.bing import Bing
from pathlib import Path
from halo import Halo

@click.group()
def main():
    pass

@main.command()
def hello():
    click.echo('Hello World!')

@main.command()
@click.argument('query')
@click.option('--limit', default=10, help='Number of images to download')
@click.option('--out-dir', default='.', help='Output directory')
@click.option('--filter-adult', default=False, help='Filter adult content')
@click.option('--timeout', default=60, help='Timeout for requests')
def bing(query, limit, out_dir, filter_adult, timeout):

    spinner = Halo(text='Downloading images', spinner='arc')
    spinner.start()

    if  not filter_adult:
        adult = 'off'
    else:
        adult = 'on'

    image_dir = Path(out_dir).absolute()
    # check directory and create if necessary
    try:
        if not Path.is_dir(image_dir):
            Path.mkdir(image_dir, parents=True)

    except Exception as e:
        spinner.fail(f'could not create directory: {out_dir}')
        exit(1)

    bing = Bing(query, limit, image_dir, adult, timeout, "photo", verbose=False)
    count = bing.run()

    spinner.succeed(f'Downloaded {count} images in {image_dir}')
    return



if __name__ == '__main__':
    main()