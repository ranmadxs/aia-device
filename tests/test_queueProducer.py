#https://api.cloudkarafka.com/
import yaml
from aia_utils.Queue import QueueConsumer, QueueProducer
import os
from dotenv import load_dotenv
load_dotenv()
import json
from aia_device import __version__
from aia_utils.logs_cfg import config_logger
import logging
config_logger()
logger = logging.getLogger(__name__)
currentPath = os.getcwd()



#poetry run pytest tests/test_queueProducer.py::test_produce -s
def test_produce():
    logger.debug("Test produce message to queue:")
    topicProducer = os.environ['TEST_CLOUDKAFKA_TOPIC_PRODUCER']
    logger.info("Test Produce queue " + topicProducer)
    queueProducer = QueueProducer(topicProducer, "test001", "aia-utils")
    queueProducer.send({"type": "image_resources", "origin": "resources/images", "name": "Loading01.png"})
    queueProducer.flush()


#poetry run pytest tests/test_queueProducer.py::test_stream -s
def test_stream():
    logger.debug("Test produce message to queue:")
    topicProducer = os.environ['TEST_CLOUDKAFKA_TOPIC_PRODUCER']
    logger.info("Test Produce queue " + topicProducer)
    queueProducer = QueueProducer(topicProducer, "test001", "aia-utils")
    queueProducer.send({"type": "image_stream", "delay": "0", "origin": "resources/images", "files": ["Loading01.png", "Loading02.png", "aia_dev.png"]})
    queueProducer.flush()