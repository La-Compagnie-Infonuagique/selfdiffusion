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

@main.command()
def signup():
    """ Initiates the browser based signup process for selfdiffusion"""

    from selfdiffusion.users import signup
    signup()

@main.command()
@click.argument('email')
def login(email):

    from selfdiffusion.users import login
    import questionary
    password = questionary.password("Password:").ask()
    result = login(email, password)
    print(result)


@main.command()
@click.argument('folder')
def review(folder):

    from selfdiffusion.data import review
    review(folder)

@main.command()
def connect():
    """ Spins up a GPU runtime for the user """

    # 1. CLI calls an API endpoint to spin up a GPU runtime.
    # 2. Checks if the user has a GPU runtime already running.
    # 3. If not, spins up a GPU runtime.
    # 4. returns temporary IAM credentials via identity pool ? to let user run code.
    # 5. CLI setups a SSH tunnel to the instance with AWS SSM.
    # 6. All traffic is routed through the tunnel (e.g: what goes through 127.0.0.1:8888 goes to the instance)

    sd_client = selfdiffusion_client()
    (credentials, instance_id) = sd_client.connect()

    aws_client = boto3.client('ssm')
    aws_client.set_credentials(credentials)

    aws_client.start_session(Target=instance_id, ssm_document_name='AWS-PortForwarding', args=['8888:localhost:8888'])

    return

@main.command()
@click.argument('prompt')
@click.option('--model', help='id of the model from hugging face model hub', required=True)
@click.option('--resolution', help='output images resolution', type=(int,int), default=(512,512))
@click.option('--inference-steps', help='Number of inference step', type=int, default=50)
@click.option('--guidance-scale', help='classifier-free guidane parameter', type=float, default=7.5)
@click.option('--negative-prompt', help='things that should not be in your generated samples', type=int, default=50)
@click.option('--samples', help='Number of samples to generate for the prompt', type=int, default=1)
def generate(prompt, model, resolution, inference_steps, guidance_scale, negative_prompt, samples):
    """ runs remote inference and stream the result back to the user"""

    ## PRESUPPOSITIONS
    # 1. User has a GPU runtime running. (invoked connect command)

    ## STEPS
    # 

