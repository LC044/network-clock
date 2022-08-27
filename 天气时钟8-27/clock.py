from package import weather
from micropython import const
import time
from package import st7789py as st
import gc
_CLOCK = const(0)
_VERSE = const(1)
_CALENDAR = const(2)
class CLOCK():
    __slots__ = 'last_hour', 'last_minute', 'last_month' , 'last_second' , 'last_year', 'last_last_day', 'colck_x', 'clock_y' ,'data','poet','WHITE','BLACK','RED'
    def __init__(self,tft,weather):
        self.tft = tft
        self.init_color()
        # 初始化参数
        self.mod = 0
        self.last_hour = 13
        self.last_minute = 14
        self.last_second = 0
        self.last_year = 0
        self.last_month = 0
        self.last_day = 0
        self.clock_x = 20+24*2-12
        self.clock_y = 90
        self.boot_animation()
        self.Weather = weather
        self.city = '34.40:114.96' # 当地经纬度，格式: 纬度:经度
        self.data = self.Weather.now_weather(self.city) 
        self.t = time.localtime(time.time())
        self.poet = self.Weather.poet()
    def model(self,*argc):
        self.mod=(self.mod+1)%4
    def init_color(self):
        self.WHITE = st.color565(255, 255, 255)#BRG
        self.BLACK = st.color565(0, 0, 0)
        self.RED = st.color565(0, 255, 0)
    def init_show(self):
        '''
        初始化显示画面
        '''
        self.tft.fill(0)
        self.tft.text(48, ':', self.clock_x + 24*2, self.clock_y, self.WHITE, self.BLACK)
        self.tft.text(24, '周', self.clock_x + 24+12, self.clock_y+48+8, self.WHITE, self.BLACK)
        self.tft.text(32, '/', self.clock_x + 24+24, self.clock_y+48+8+24, self.WHITE, self.BLACK)
    def init_time(self):
        t = time.localtime(time.time())
        '''
        第一次显示时间
        '''
        hour = t[3]
        minute = t[4]
        second = t[5]
        self.tft.text(48, '{:0>2d}'.format(hour), self.clock_x, self.clock_y, self.WHITE, self.BLACK)
        self.last_hour = hour
        self.tft.text(48, '{:0>2d}'.format(minute), self.clock_x + 24*3, self.clock_y, self.WHITE, self.BLACK)
        self.last_minute = minute
        year = t[0]
        month = t[1]
        day = t[2]
        # 清空原有内容
        self.tft.fill_rect(self.clock_x + 16,self.clock_y+48+8+24,32,32,self.BLACK)
        offest_x = 16 if month>9 else 32
        self.tft.text(32, '{}'.format(month), self.clock_x + offest_x, self.clock_y+48+8+24, self.WHITE, self.BLACK)
        self.last_month = month
        self.tft.fill_rect(self.clock_x+24+24+16,self.clock_y+48+8+24,32,32,self.BLACK)
        self.tft.text(32, '{}'.format(day), self.clock_x+24+24+16, self.clock_y+48+8+24, self.WHITE, self.BLACK)
        e_w, z_w = self.week(t)
        self.tft.text(24, z_w, self.clock_x + +24+12+24, self.clock_y+48+8, self.WHITE, self.BLACK)
        self.last_day = day
        self.show_poet() # 显示诗词
    def boot_animation(self):
        '''
        开机动画
        '''
        txt = 'Prepare for a career in tech by joining GitHub Global Campus. Global Campus will help you get the practical industry knowledge you need by giving you access to industry tools, events, learning resources and a growing student community.'
        #for t in txt:
        self.tft.text(16, txt[:20], 0, 0, self.WHITE, self.BLACK)
        self.tft.text(16, txt[20:50], 0, 20, self.WHITE, self.BLACK)
        self.tft.text(16, txt[50:60], 0, 40, self.WHITE, self.BLACK)
        self.tft.text(16, txt[60:80], 0, 60, self.WHITE, self.BLACK)
        self.tft.text(16, txt[80:85], 0, 80, self.WHITE, self.BLACK)
        self.tft.text(16, txt[85:110], 0, 100, self.WHITE, self.BLACK)
        self.tft.text(16, txt[110:125], 0, 120, self.WHITE, self.BLACK)
        self.tft.text(16, txt[125:150], 0, 140, self.WHITE, self.BLACK)
    def show_city(self,city):
        '''
        显示城市
        '''
        self.tft.text(16, city, 61+10+32, 16+10, self.WHITE, self.BLACK)
    def show_tem(self,temp):
        '''
        显示温度
        '''
        self.tft.text(32, temp, 61+5, 10, self.WHITE, self.BLACK)
        self.tft.text(16,'℃' , 61+5+32, 10, self.WHITE, self.BLACK)
    def clear(self):
        '''
        清空天气显示画面
        '''
        self.tft.fill_rect(170-24-8,0,24,24*2,self.BLACK)
        self.tft.fill_rect(0, 0,61,61,self.BLACK)
    def show_weather(self,data):
        self.clear()
        self.show_tem(data['tem'])
        weather = data['weather']
        code = data['code']
        height = data['height']
        width = data['width']
        for i in range(len(weather)):
            self.tft.text(24, weather[i], 170-24-8, i*24, self.RED, self.BLACK)
        f = open('./picture/{}@1x.dat'.format(code),'rb')
        # 显示天气图标
        for i in range(10,height,10):
            data = f.read(width*10*2)
            self.tft._set_window(0,i-10,width-1,i)
            self.tft._write(None,data)
        data = f.read(width*(height%10)*2)
        self.tft._set_window(0,(height//10)*10,width-1,height)
        self.tft._write(None,data)
        f.close()
        # 释放内存
        del data
        gc.collect()
    

    def week(self,t):
        # 获取星期
        week = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
        week0 = ['一','二','三','四','五','六','日']
        return week[t[6]],week0[t[6]]
    def astronaut(self):
        file = [open("./astronaut/img{}.dat".format(i), "rb") for i in range(1, 13)]
        while True:
            for f in file:
                f.seek(0)
                for row in range(0, 80, 20):
                    buffer = f.read(4000)
                    self.tft._set_window(140,row,239,row+19)
                    self.tft._write(None,buffer)
    def show_time(self,t):
        t = time.localtime(time.time())
        '''
        显示时间
        '''
        hour = t[3]
        minute = t[4]
        second = t[5]
        ti = "{:0>2d}:{:0>2d}:{:0>2d}".format(hour,minute,second)
        #print(ti)
        if hour != self.last_hour:
            self.tft.text(48, '{:0>2d}'.format(hour), self.clock_x, self.clock_y, self.WHITE, self.BLACK)
            self.last_hour = hour
            self.poet = self.Weather.poet()
            self.show_poet()
        if minute != self.last_minute:
            self.tft.text(48, '{:0>2d}'.format(minute), self.clock_x + 24*3, self.clock_y, self.WHITE, self.BLACK)
            self.last_minute = minute
        self.calendar(t)
    def show_poet(self):
        self.tft.fill_rect(0,61,16*11,16,self.BLACK)
        self.tft.text(16, self.poet, 0, 61, self.WHITE, self.BLACK)
    def calendar(self,t):
        year = t[0]
        month = t[1]
        day = t[2]
        if month != self.last_month:
            # 先清空再显示
            self.tft.fill_rect(self.clock_x + 16,self.clock_y+48+8+24,32,32,self.BLACK)
            offest_x = 16 if month>9 else 32
            self.tft.text(32, '{}'.format(month), self.clock_x + offest_x, self.clock_y+48+8+24, self.WHITE, self.BLACK)
            self.last_month = month
        if day != self.last_day:
            # 先清空再显示
            self.tft.fill_rect(self.clock_x+24+24+16,self.clock_y+48+8+24,32,32,self.BLACK)
            self.tft.text(32, '{}'.format(day), self.clock_x+24+24+16, self.clock_y+48+8+24, self.WHITE, self.BLACK)
            e_w, z_w = self.week(t)
            self.tft.text(24, z_w, self.clock_x + +24+12+24, self.clock_y+48+8, self.WHITE, self.BLACK)
            self.last_day = day
        
    def clock(self):
        file = [open("./astronaut/img{}.dat".format(i), "rb") for i in range(1, 14)]
        #self.tft.brightness(64)
        self.init_show()                   # 初始化显示画面
        self.show_city(self.data['city'])  # 显示城市
        self.show_tem(self.data['tem'])    # 显示温度
        self.show_weather(self.data)       # 显示天气信息
        self.init_time()                   # 初始化时间显示
        while True:
            if self.mod != _CLOCK:
                return
            self.t = time.localtime(time.time())
            # 每十分钟天气更新一次
            if self.t[4]%10==0 and 0<self.t[5]<2:
                self.data = self.Weather.now_weather(self.city)
                self.show_city(self.data['city'])
                self.show_weather(self.data)
            self.show_time(self.t)
            # 显示太空人动画
            for f in file:
                f.seek(0)
                for row in range(0, 80, 20):
                    buffer = f.read(2800)
                    self.tft._set_window(170,row,239,row+19)
                    self.tft._write(None,buffer)
                time.sleep(0.1)
    def run(self):
        while True:
            print(self.mod)
            if self.mod == _CLOCK:
                self.clock()
            elif self.mod == _VERSE:
                self.tft.fill(0)
            time.sleep(0.5)
        
    def __del__(self):
        pass




