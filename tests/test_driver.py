import imageio
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from skimage.draw import line_aa
from aia_utils.logs_cfg import config_logger
import logging
from aia_device.deviceSvc import DeviceService
config_logger()
logger = logging.getLogger(__name__)
import os
from dotenv import load_dotenv
load_dotenv()

def getSize(txt, font):
    testImg = Image.new('RGB', (1, 1))
    testDraw = ImageDraw.Draw(testImg)
    return testDraw.textsize(txt, font)

#poetry run pytest tests/test_driver.py::test_line -s
def test_line():
    logger.debug("Test line")
    img = np.zeros((320, 480), dtype=np.uint8)
    rr, cc, val = line_aa(1, 1, 100, 100)
    img[rr, cc] = val * 255
    imageio.imwrite("target/out.png", img)

#poetry run pytest tests/test_driver.py::test_line2 -s
def test_line2():
    logger.debug("Test line")
    fontname = "Arial.ttf"
    fontsize = 11   
    text = "example@gmail.com"
    
    colorText = "black"
    colorOutline = "red"
    colorBackground = "white"


    font = ImageFont.truetype(fontname, fontsize)
    width, height = 480, 320
    img = Image.new('RGB', (width+4, height+4), colorBackground)
    d = ImageDraw.Draw(img)
    d.text((2, height/2), text, fill=colorText, font=font)
    d.rectangle((0, 0, width+3, height+3), outline=colorOutline)
    
    img.save("target/image_txt.png")    

#poetry run pytest tests/test_driver.py::test_ip -s
def test_ip():
    import socket

    #print(socket.gethostbyname('localhost'))

    localip = DeviceService(os.environ['CLOUDKAFKA_TOPIC_TEST'], "test01").get_local_ip()
    assert localip is not None