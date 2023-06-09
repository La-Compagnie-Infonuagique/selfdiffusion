import click

from selfdiffusion.sources.bing import Bing
from selfdiffusion.utils import create_target
from selfdiffusion.utils import image_loader
from selfdiffusion.utils import image_saver
from selfdiffusion.log import logger
from selfdiffusion.api import SelfDiffusionClient
from halo import Halo
from pathlib import Path
import questionary

sd_client = SelfDiffusionClient("https://api.dev.selfdiffusion.net")

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

@main.command()
def signup():
    """ Initiates the browser based signup process for selfdiffusion"""


    # ask for email, password, phone number
    email = questionary.text("What is your email address?:").ask()
    password = questionary.password("Choose a password:").ask()
    phone = questionary.text("What is your phone number?:").ask()

    _ = sd_client.init_signup(email, password, phone)

    # ask for verification code
    code = questionary.text("What is the verification code?:").ask()
    sd_client.confirm_signup(email, code)

    # user is signed up ..
    print('you are now signed up and ready to use selfdiffusion')
    print('to conitnue, you need to login selfdiffusion login your-email-address@example.com')
    return

@main.command()
@click.argument('email')
@click.option('--code', help='verification code', required=True)
def confirm(email, code):
    """ Confirms the email address of the user """

    sd_client.confirm_signup(email, code)

    return


@main.command()
@click.argument('email')
def login(email):

    password = questionary.password("Password:").ask()
    sd_client.login(email, password)

@main.command()
def balance():
    """ returns the balance in the user account """

    balance = sd_client.balance()
    print(balance)


@main.command()
@click.argument('folder')
def review(folder):

    from selfdiffusion.data import review
    review(folder)

@main.command()
def allocate():
    """ allocates a GPU runtime for the user """

    print(sd_client._allocate_gpu_runtime())


@main.command()
#@click.argument('prompt')
#@click.option('--model', help='id of the model from hugging face model hub', required=True)
#@click.option('--resolution', help='output images resolution', type=(int,int), default=(512,512))
#@click.option('--inference-steps', help='Number of inference step', type=int, default=50)
#@click.option('--guidance-scale', help='classifier-free guidane parameter', type=float, default=7.5)
#@click.option('--negative-prompt', help='things that should not be in your generated samples', type=int, default=50)
#@click.option('--samples', help='Number of samples to generate for the prompt', type=int, default=1)
def generate():
    """ runs remote inference and stream the result back to the user"""

    return print(sd_client.generate())

@main.command()
def result():
    """ returns the result of the last inference run """

    return print(sd_client.result())

@main.command()
def generatedev():
    """ runs remote inference and stream the result back to the user"""

    prompt = "a close up portrait photo of 26 y.o woman in wastelander clothes, long haircut, pale skin, slim body, background is city ruins, (high detailed skin:1.2), 8k uhd, dslr, soft lighting, high quality, film grain, Fujifilm XT3"
    samples = 1
    return print(sd_client.generatedev(prompt, samples))
