import os
from dotenv import load_dotenv
load_dotenv()
from aia_device.transform import ImageTransformer
from aia_device.deviceSvc import DeviceService
from . import __version__
from aia_utils.logs_cfg import config_logger
import logging
config_logger()
logger = logging.getLogger(__name__)

def run():
    logger.info("Running Device daemon")
    deviceSvc = DeviceService(os.environ['CLOUDKAFKA_TOPIC_CONSUMER'], __version__)
    deviceSvc.kafkaListener()

