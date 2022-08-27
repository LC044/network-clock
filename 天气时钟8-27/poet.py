import utime
from package import st7789py as st
from micropython import const
_CLOCK = const(0)
_VERSE = const(1)
class POET():
    def __init__(self,tft,weather):
        self.tft = tft
        self.Weather = weather
        self.init_color()
        self.mod = 1
    def init_color(self):
        self.WHITE = st.color565(255, 255, 255)
        self.BLACK = st.color565(0, 0, 0)
        self.RED = st.color565(255,0, 0)
    def show(self):
        try:
            poet_data = self.Weather.jinrishici()
            author = poet_data['origin']['author']
            dynasty = poet_data['origin']['dynasty']
            title = poet_data['origin']['title']
            poet = poet_data['origin']['content']
        except:
            pass
        poem = []
        for i in range(len(poet)):
            if len(poet[i])>15:
                if '。' in poet[i]:
                    se = poet[i].split('。')
                elif '？' in poet[i]:
                    se = poet[i].split('？')
                elif '！' in poet[i]:
                    se = poet[i].split('！')
                else:
                    se = poet[i].split('，')
                for s in range(len(se)-1):
                    if len(se[s]) > 15:
                        p = se[s].split('，')
                        for pm in p:
                            poem.append(pm)
                    else:
                        poem.append(se[s])
            else:
                poem.append(poet[i])
        y = 50
        del poet
        self.tft.fill(self.WHITE)
        offest = (240-24*len(title))//2
        self.tft.text(24, title, offest, 0, self.BLACK, self.WHITE)
        offest = 24*len(author)
        self.tft.text(24, '{}'.format(author), 240-offest-24, 30, self.BLACK, self.WHITE)
        for p in poem:
            y = y + 20
            offest = (240-16*len(p))//2
            self.tft.text(16, p, offest, y, self.BLACK, self.WHITE)
        while True:
            if self.mod != 1:
                return
            else:
                utime.sleep(0.5)
                pass
if __name__=='__main__':
    from machine import Pin, SPI, RTC
    from package import weather
    tft = st.ST7789(SPI(2, 10000000), 240, 240, reset=Pin(5), dc=Pin(17), cs=Pin(16), backlight=Pin(4), rotation=0)
    p = POET(tft,weather.Weather())
    ts = utime.ticks_ms()
    p.show()
    te = utime.ticks_ms()
    tc = te - ts
    print(tc)