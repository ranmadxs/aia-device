from aia_utils.Queue import QueueConsumer, QueueProducer
from aia_utils.logs_cfg import config_logger
from aia_device.transform import ImageTransformer
import logging
from aia_device.driver.driver_svc import DriverController
import base64
import datetime

class DeviceService:

    def __init__(self, topic_consumer, version):
        self.topic_consumer = topic_consumer
        self.version = version
        config_logger()
        self.logger = logging.getLogger(__name__)
        self.driver = DriverController()

    def kafkaListener(self):
        queueConsumer = QueueConsumer(self.topic_consumer)
        self._beforeCallback()
        queueConsumer.listen(self.processImage, False)

    def _beforeCallback(self):
        self._sendImg("resources/images/aia.png")

    def _sendImg(self, imgName: str):
        imgTrx = ImageTransformer()
        imgResult = imgTrx.fileToRGB(imgName)
        imgResult = imgTrx.resizeProportional(imgResult)
        self.driver.sendImageToDevice(imgResult)

    def processImage(self, img_data: str):
        text = "Llegó una img!"
        self.logger.debug(text)
        #logger.debug(img_data)
        folder_base = "target/"
        time_str = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        img_name = f"snapshot_{time_str}.png"
        file_full_path = f"{folder_base}{img_name}"
        with open(file_full_path, "wb") as fh:
            fh.write(base64.decodebytes(img_data))
        self.logger.debug(f"File saved: {file_full_path}")
        self._sendImg(file_full_path)

    def callback(self, aiaDevice: any):
        text = "Llegó un mensaje!"
        self.logger.debug(text)
        self.logger.debug(aiaDevice)
        if "type" in aiaDevice and "origin" in aiaDevice and "name" in aiaDevice:
            if aiaDevice["type"] == "image_resources":
                try:
                    self._sendImg(f"{aiaDevice['origin']}/{aiaDevice['name']}")
                    #imgTrx = ImageTransformer()
                    #imgResult = imgTrx.fileToRGB(f"{aiaDevice['origin']}/{aiaDevice['name']}")
                    #imgResult = imgTrx.resizeProportional(imgResult)
                    #self.driver.sendImageToDevice(imgResult)
                except Exception as e:
                    self.logger.error(e)
                    self.logger.error(">> Error al enviar la imagen al dispositivo")
                    #self._beforeCallback()
                    self._sendImg("resources/images/error.png")
