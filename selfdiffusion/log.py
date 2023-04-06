import logging

from selfdiffusion import __identifier__ 

LOGGER_NAME = __identifier__
GLOBAL_LOG_LEVEL = logging.INFO

# Create a logger
logger = logging.getLogger(LOGGER_NAME)

# Set the logging level
logger.setLevel(GLOBAL_LOG_LEVEL)

# Create a handler for writing log messages to the console
console_handler = logging.StreamHandler()
console_handler.setLevel(GLOBAL_LOG_LEVEL)  # Change this to the desired logging level for the console

# Create a formatter for log messages
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Set the formatter for both handlers
console_handler.setFormatter(formatter)

# Add the handlers to your logger
logger.addHandler(console_handler)
