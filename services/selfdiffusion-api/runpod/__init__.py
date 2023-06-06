""" Allows runpod to be imported as a module. """

from .api_wrapper.ctl_commands import(
    get_gpus, get_gpu,
    create_pod, stop_pod, resume_pod, terminate_pod
)

api_key = None  # pylint: disable=invalid-name
api_url_base = "https://api.runpod.io"  # pylint: disable=invalid-name

