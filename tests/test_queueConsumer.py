from aia_utils.Queue import QueueConsumer, QueueProducer
import os
import logging
from aia_utils.logs_cfg import config_logger
config_logger()
logger = logging.getLogger(__name__)
currentPath = os.getcwd()

from aia_device.deviceSvc import DeviceService


#poetry run pytest tests/test_queueConsumer.py::test_consume -s
def test_consume():
    logger.debug("Test consume message to queue:")
    deviceSvc = DeviceService(os.environ['CLOUDKAFKA_TOPIC_TEST'], "test01")
    queueConsumer = QueueConsumer(os.environ['CLOUDKAFKA_TOPIC_TEST'])
    queueConsumer.listen(deviceSvc.processImage, False)
