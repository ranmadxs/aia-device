from aia_utils.logs_cfg import config_logger
import logging
#config_logger()
logger = logging.getLogger(__name__)
from PIL import Image
import platform

class DriverController:

    def __init__(self):
        logger.debug("DriverIli9486")
        if platform.system() == "Linux":
            from aia_device.driver.ILI9486.lcd import LCDILI9486
            self.lcd = LCDILI9486()

    def sendImageToDevice(self, img: Image):
        logger.debug("sendImageToDevice")
        if platform.system() == "Linux":
            self.lcd.display(img)
            logger.debug("Linux")
        else:
            logger.warning("Not Linux compatible")
            img.save('target/sample.png', 'PNG', quality=100)
            
