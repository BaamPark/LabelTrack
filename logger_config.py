import logging

def setup_logger():
    # Create a logger
    logger = logging.getLogger('my_logger')
    
    #you set log level to INFO
    #only messages with a level equal to or higher than the one you set will be handled, which means debug level will be ignored
    logger.setLevel(logging.INFO)

    # Create a file handler
    handler = logging.FileHandler('application.log')

    # Create a formatter and add it to the handler
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(handler)

    return logger

logger = setup_logger()