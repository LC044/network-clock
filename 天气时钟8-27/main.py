from machine import Pin, SPI, RTC
#from package import st7789
from package import st7789py as st
from package import weather
import gc
import time
import clock
import poet
import calendar
_CLOCK = 0
_VERSE = 1
_CALENDAR = 2
class Display():
    def __init__(self):
        self.tft = st.ST7789(SPI(2, 10000000), 240, 240, reset=Pin(5), dc=Pin(17), cs=Pin(16), backlight=Pin(4), rotation=0)
        self.bt = Pin(34, Pin.IN,Pin.PULL_DOWN)
        self.bt.irq(trigger=Pin.IRQ_FALLING, handler=self.model)
        self.mod = 0
        self.weather = weather.Weather()
        self.clock = clock.CLOCK(self.tft,self.weather)
        self.poem = poet.POET(self.tft,self.weather)
        self.calendar = calendar.Calendar(self.tft)
    def model(self,*argc):
        self.mod=(self.mod+1)%4
        self.clock.mod = self.mod
        self.poem.mod = self.mod
        self.calendar.mod = self.mod
    def run(self):
        while True:
            print(self.mod)
            if self.mod == _CLOCK:
                self.tft.brightness(10)
                self.clock.clock()
            elif self.mod == _VERSE:
                self.tft.brightness(512)
                self.tft.fill(0)
                self.poem.show()
            elif self.mod == _CALENDAR:
                self.tft.brightness(256)
                self.calendar.display()
            time.sleep(0.5)
            gc.collect()
    def __del__(self):
        pass
D = Display()
D.run()



