from PIL import Image
from aia_utils.logs_cfg import config_logger
import logging
config_logger()
logger = logging.getLogger(__name__)

class ImageTransformer:
    def __init__(self) -> None:
        logger.info("ImageTransformer initialized")

    def fileToRGB(self, file: str) -> Image:
        logger.info(f"file -> [RGB] {file}")
        return self.toRGB(Image.open(file))

    def toRGB(self, image: Image) -> Image:
        #rgbImg = Image.new("RGB", png.size, (255, 255, 255))
        return image.convert('RGB')
    
    def resizeProportional(self, image: Image, max_w: int = 480, max_h: int = 320) -> Image:
        #png = Image.open("foo.png")
        width, height = image.size
        logger.debug(f"image size: {width}x{height}")
        if (height > width):
            logger.debug("rotate image 90ª")
            image = image.rotate(90) 
            width, height = image.size
        im_w = width
        im_h = height
        if im_w > max_w:
            im_h = (max_w*height)//width
            im_w = max_w

        if im_h > max_h:
            im_h = max_h
            im_w = (width*im_h)//height

        im = image.resize((im_w, im_h))
        #im.save('xd.png', 'PNG', quality=80)        
        return im


#png = Image.open("aia.png")
#png.load() # required for png.split()

#background = Image.new("RGB", png.size, (255, 255, 255))
#background.paste(png, mask=png.split()[3]) # 3 is the alpha channel

#background.save('foo.png', 'PNG', quality=80)