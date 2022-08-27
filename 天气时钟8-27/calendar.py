from package import weather
import time
from package import st7789py as st
_CLOCK = 0
_VERSE = 1
class Calendar(object):
    days = [31,28,31,30,31,30,31,31,30,31,30,31]      
    def __init__(self,tft,year=2022):#初始化默认2017年
        self.year = year
        if self.yearDays(year) == 366:
            self.days[1] = 29
        self.totalDays = 0
        for i in range(1, self.year):
            self.totalDays += self.yearDays(i)
        self.tft = tft
        self.init_color()
        self.mod = 2
        self.t = time.localtime(time.time())
        
    #判断每年的天数
    def yearDays(self,year):
        return 366 if (year % 4 == 0 and year % 100 != 0) or year % 400 == 0 else 365
    # 查看某个月的日历
    def months(self,month):
        totalDays = self.totalDays
        for i in range(1,month):
            totalDays+=self.days[i-1]
        #计算确定月份的第一天为周几
        self.week = (totalDays+1) % 7
        self.show(month)
    #查看全年日历
    def wholeYear(self):
        # 计算确定年份的一月一日为周几
        self.week = (self.totalDays+1) % 7
        for i in range(1,13):
            self.show(i)
    def header(self):
        y = 35+10
        size = 16
        self.tft.text(32, '{}'.format(self.t[0]), 0, 0 , self.WHITE, self.BLACK)
        self.tft.text(32, '年', 16*4, 0 , self.WHITE, self.BLACK)
        self.tft.text(32, '{}'.format(self.t[1]), 64+32, 0 , self.WHITE, self.BLACK)
        self.tft.text(32, '月', 96+16, 0 , self.WHITE, self.BLACK)
        self.tft.text(size, '日', 10, y , self.WHITE, self.BLACK)
        self.tft.text(size, '一', 44, y , self.WHITE, self.BLACK)
        self.tft.text(size, '二', 78, y , self.WHITE, self.BLACK)
        self.tft.text(size, '三', 112, y , self.WHITE, self.BLACK)
        self.tft.text(size, '四', 146, y , self.WHITE, self.BLACK)
        self.tft.text(size, '五', 180, y , self.WHITE, self.BLACK)
        self.tft.text(size, '六', 214, y , self.WHITE, self.BLACK)
    def init_color(self):
        self.WHITE = st.color565(255, 255, 255)#RGB
        self.BLACK = st.color565(0, 0, 0)
        self.RED = st.color565(255, 0, 0)
        self.GRAY = st.color565(180, 180, 180)
        self.bg = st.color565(80, 80, 80)
    def show(self,month):
        begin = 1
        y = 35 + 16 + 4+5+10
        dx = 34
        x = self.week
        week_num = 1
        while begin <= self.days[month - 1]:
            begin += 1
            self.week = (self.week + 1) % 7
            if self.week % 7 == 0:
                week_num+=1
        begin = 1
        self.week = x
        print(week_num)
        size = 16 if week_num == 6 else 24
        while begin <= self.days[month - 1]:
            color = self.RED if begin == self.t[2] else self.WHITE
            bg = self.WHITE if begin == self.t[2] else self.BLACK
            offest_x = 6 if begin<10 else 0
            self.tft.text(size, '{}'.format(begin), 5+dx*x+offest_x, y , color, bg)
            begin += 1
            x+=1
            self.week = (self.week + 1) % 7
            #print('%4d' % begin,end=',')
            if self.week % 7 == 0:
                x=0
                y+=30
    def display(self):
        self.tft.fill(0)
        self.header()
        #self.layout()
        self.months(self.t[1])
        while True:
            if self.mod != 2:
                return
            else:
                time.sleep(0.5)
                pass
        pass
if __name__=='__main__':
    from machine import Pin, SPI, RTC
    tft = st.ST7789(SPI(2, 10000000), 240, 240, reset=Pin(17), dc=Pin(2), cs=Pin(5), backlight=Pin(22), rotation=0)
    p = Calendar(tft)
    start = time.time()
    p.display()
    end = time.time()
    print(end-start)
