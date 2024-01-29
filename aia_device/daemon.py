import os
from dotenv import load_dotenv
load_dotenv()
from aia_device.transform import ImageTransformer
from aia_device.deviceSvc import DeviceService
from aia_utils.logs_cfg import config_logger
import logging
config_logger()
logger = logging.getLogger(__name__)
from aia_utils.toml_utils import getVersion

def run():
    version = getVersion()
    logger.info(f"Running Device daemon v{version}")
    deviceSvc = DeviceService(os.environ['CLOUDKAFKA_TOPIC_CONSUMER'], version)
    deviceSvc.kafkaListener()

