import tempfile

from selfdiffusion.pipelines import person_pipeline
from selfdiffusion.utils import image_loader, image_saver

from selfdiffusion import __identifier__

from tests.utils import file_count

def test_every_image_processed():
    """ Test that every image is processed. """
    # get an image loader from the src
    images = image_loader("tests/data/portrait")

    # process the images with a pipeline
    persons = person_pipeline(images, (512, 512))

    processed_count = 0
    with tempfile.TemporaryDirectory(prefix=f'{__identifier__}-', suffix="-test") as tmpdir:
        # save the images to the target
        image_saver(persons, tmpdir)
        processed_count = file_count(tmpdir)

    input_count = file_count("tests/data/portrait")
    assert processed_count == input_count
