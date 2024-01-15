from aia_utils.Queue import QueueConsumer, QueueProducer
from aia_utils.logs_cfg import config_logger
from aia_device.transform import ImageTransformer
import logging
from aia_device.driver.driver_svc import DriverController
config_logger()
logger = logging.getLogger(__name__)

class DeviceService:

    def __init__(self, topic_consumer, version):
        self.topic_consumer = topic_consumer
        self.version = version
        self.driver = DriverController()

    def kafkaListener(self):
        queueConsumer = QueueConsumer(self.topic_consumer)
        self._beforeCallback()
        queueConsumer.listen(self.callback)

    def _beforeCallback(self):
        self._sendImg("resources/images/aia.png")

    def _sendImg(self, imgName: str):
        imgTrx = ImageTransformer()
        imgResult = imgTrx.fileToRGB(imgName)
        imgResult = imgTrx.resizeProportional(imgResult)
        self.driver.sendImageToDevice(imgResult)

    def callback(self, aiaDevice: any):
        text = "Llegó un mensaje!"
        logger.debug(text)
        logger.debug(aiaDevice)
        if "type" in aiaDevice and "origin" in aiaDevice and "name" in aiaDevice:
            if aiaDevice["type"] == "image_resources":
                try:
                    self._sendImg(f"{aiaDevice['origin']}/{aiaDevice['name']}")
                    #imgTrx = ImageTransformer()
                    #imgResult = imgTrx.fileToRGB(f"{aiaDevice['origin']}/{aiaDevice['name']}")
                    #imgResult = imgTrx.resizeProportional(imgResult)
                    #self.driver.sendImageToDevice(imgResult)
                except Exception as e:
                    logger.error(e)
                    logger.error(">> Error al enviar la imagen al dispositivo")
                    #self._beforeCallback()
                    self._sendImg("resources/images/error.png")
