from PIL import Image
import RPi.GPIO as GPIO
from spidev import SpiDev
import time
import aia_device.driver.ILI9486.driver as LCD
import aia_device.driver.ILI9486.config as config

class LCDILI9486:

    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        spi = SpiDev(config.SPI_BUS, config.SPI_DEVICE)
        spi.mode = 0b10  # [CPOL|CPHA] -> polarity 1, phase 0
        # default value
        # spi.lsbfirst = False  # set to MSB_FIRST / most significant bit first
        spi.max_speed_hz = 64000000
        self.lcd = LCD.ILI9486(dc=config.DC_PIN, rst=config.RST_PIN, spi=spi).begin()
        print("Init display ok")
        #print(f"Initialized display with landscape mode = {self.lcd.is_landscape()} 
        #      and dimensions {self.lcd.dimensions()}")
        #self.lcd.lcd_init()
        #self.lcd.lcd_clear()
        #self.lcd.lcd_display_string("Hello World!", 40, 120, 2, 0xFFFF)

    def display(self, image: Image):
        print('Drawing image')
        self.lcd.clear().display()
        self.lcd.display(image)
