from aia_utils.Queue import QueueConsumer, QueueProducer
from aia_utils.logs_cfg import config_logger
from aia_device.transform import ImageTransformer
import logging
from aia_device.driver.driver_svc import DriverController
import base64
import datetime
import json
import socket

class DeviceService:

    def __init__(self, topic_consumer, version):
        self.topic_consumer = topic_consumer
        self.version = version
        config_logger()
        self.logger = logging.getLogger(__name__)
        self.driver = DriverController()

    def get_local_ip(self) -> str:
        try:
            with open('target/local_ip.txt') as f:
                loc_ip = f.read().strip()
                self.logger.debug(loc_ip)
                return loc_ip
        except Exception as e:
            self.logger.error(e)
            self.logger.error(">> Error al obtener la IP local")
            return None

    def kafkaListener(self):
        queueConsumer = QueueConsumer(self.topic_consumer)
        self._beforeCallback()
        queueConsumer.listen(self.callback, False)

    def _beforeCallback(self):
        self._sendImg("resources/images/aia.png", self.get_local_ip())

    def _sendImg(self, imgName: str, text: str = None):
        imgTrx = ImageTransformer()
        imgResult = imgTrx.fileToRGB(imgName)
        imgResult = imgTrx.resizeProportional(imgResult)
        if text is not None:
            imgResult = imgTrx.text2img(imgResult, text)
        self.driver.sendImageToDevice(imgResult)

    def processImage(self, img_data: str, name: str = None):
        text = "Llegó una img!"
        self.logger.debug(text)
        #logger.debug(img_data)
        folder_base = "target/"
        img_name = name
        if name is None:
            time_str = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            img_name = f"snapshot_{time_str}.png"
        
        file_full_path = f"{folder_base}{img_name}"
        with open(file_full_path, "wb") as fh:
            fh.write(base64.decodebytes(img_data))
        self.logger.debug(f"File saved: {file_full_path}")
        self._sendImg(file_full_path)

    def callback(self, msgin: any):
        text = "Llegó un mensaje!"
        self.logger.debug(text)
        #self.logger.debug(msgin)
        try:
            #json.loads(msgValue)
            aiaDevice = msgin.decode('utf-8').replace("'", '"')
            #self.logger.debug(type(aiaDevice))

            has_type = aiaDevice.find("type")
            if has_type > 0:
                self.logger.debug(aiaDevice)
                self.logger.debug("Process Image Json")
                aiaDevice = json.loads(aiaDevice)
                if "type" in aiaDevice and "origin" in aiaDevice:
                    if aiaDevice["type"] == "image_base64" and "name" in aiaDevice:
                        self.processImage(aiaDevice['image_data'], aiaDevice['name'])
                    if aiaDevice["type"] == "image_stream":
                        self.logger.debug(aiaDevice["files"])
                        for file in aiaDevice["files"]: 
                            self._sendImg(f"{aiaDevice['origin']}/{file}")                
                    if aiaDevice["type"] == "image_resources" and "name" in aiaDevice:
                        self._sendImg(f"{aiaDevice['origin']}/{aiaDevice['name']}")
                        #imgTrx = ImageTransformer()
                        #imgResult = imgTrx.fileToRGB(f"{aiaDevice['origin']}/{aiaDevice['name']}")
                        #imgResult = imgTrx.resizeProportional(imgResult)
                        #self.driver.sendImageToDevice(imgResult)
                else:
                    self.logger.error(">> Error al recibir el mensaje  no contiene type, origin o name")
                    self._sendImg("resources/images/error.png")
            else: #default imagebas64 in message content
                self.logger.debug("Process Image NO Json")
                self.processImage(msgin)
        except Exception as e:
            self.logger.error(e)
            self.logger.error(">> Error al procesar/enviar la imagen al dispositivo")
            #self._beforeCallback()
            self._sendImg("resources/images/error.png")
