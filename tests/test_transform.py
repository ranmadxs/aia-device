from transform import ImageTransformer
from aia_utils.logs_cfg import config_logger
import logging
#config_logger()
logger = logging.getLogger(__name__)


#poetry run pytest tests/test_transform.py::test_fileToRGB -s
def test_fileToRGB():
    print("test_fileToRGB")
    imgT = ImageTransformer()
    imgResult = imgT.fileToRGB("resources/aia.png")
    imgResult = imgT.resizeProportional(imgResult)
    assert imgResult.size == (465, 320)