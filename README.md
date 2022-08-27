

# esp32 + Python 打造个性化桌面时钟

## 一、显示效果

按下按键三种模式切换

1. ![](https://upload-images.jianshu.io/upload_images/17840362-95acb6fd183eec96.png?imageMogr2/auto-orient/strip|imageView2/2/w/331/format/webp)
2. ![](https://github.com/LC044/network-clock/blob/main/image/%E5%BE%AE%E4%BF%A1%E5%9B%BE%E7%89%87_20220827131449(1)(1).jpg)
3. ![](https://github.com/LC044/network-clock/blob/main/image/%E5%BE%AE%E4%BF%A1%E5%9B%BE%E7%89%87_20220827131446(1)(1).jpg)

## 二、硬件准备

### 硬件清单：

|      |             名称             | 数量 |
| :--: | :--------------------------: | :--: |
|  1   |     30引脚esp32-s开发板      |  1   |
|  2   |           1kΩ电阻            |  1   |
|  3   |           按键开关           |  1   |
|  4   | 240*240tft屏幕（st7789驱动） |  1   |
|  5   |            杜邦线            | 若干 |

### 线路连接：

![接线](https://github.com/LC044/network-clock/blob/main/image/image-20220827115830898.png)

## 三、开源地址

GitHub：https://github.com/LC044/network-clock

Gitee：https://gitee.com/shuaikang-zhou/network-clock

## 四、原理分析

### （一）st7789py.py驱动修改

```python
'''
导入字体
'''
from package import GBfont
from package import font_gb_16x16 as font_gb
from package import VGAfont
GB16 = GBfont.gb2312(16)
GB24 = GBfont.gb2312(24)
GB32 = font_gb.Font32(32)
vga32 = VGAfont.VGAFONT(32)
vga16 = VGAfont.VGAFONT(16)
vga24 = VGAfont.VGAFONT(24)
vga40 = VGAfont.VGAFONT(40)
vga48 = VGAfont.VGAFONT(48)
```

新增PWM背光调节亮度：

```python
'''初始化'''
if backlight is not None:
    from machine import PWM
    self.bl = PWM(self.backlight,freq=1000,duty=128)
def brightness(self,value):
    '''
    调节屏幕亮度
    value: int 0-1023
    '''
    self.bl.duty(value)
```

支持更多字号字体，中英文字体，不同字号字体合并：

```python
def text(self,size, text, x0, y0, color=WHITE, background=BLACK):
        char = text[0].encode('utf-8')
        if len(char) == 1:
            if size == 0:
                pass
            elif size == 24:
                font_gb = vga24.str(text)
            elif size == 16:
                font_gb = vga16.str(text)
            elif size == 32:
                font_gb = vga32.str(text)
            elif size == 40:
                font_gb = vga40.str(text)
            elif size == 48:
                font_gb = vga48.str(text)
        else:
            if size == 16:
                font_gb = GB16.str(text)
            elif size == 24:
                font_gb = GB24.str(text)
            elif size == 32:
                font_gb = GB32
            elif size == 48:
                font_gb = GB48
        self._text(font_gb,size, text, x0, y0, color, background)
```

提高显示速度，修复颜色bug：

```python
def _text(self,font,size, text, x0, y0, color=WHITE, background=BLACK):
        self.k = 0
        self.num = 4
        for char in text:
            if (x0+font.WIDTH <= self.width and y0+font.HEIGHT <= self.height):
                for line in range(self.num):  # 分两次显示，先显示上半边后显示下半边
                        idx = line * (font.SIZE//self.num)
                        buffer = b''
                        for x in range(0,(font.SIZE//self.num),1):
                            buffer += struct.pack('>8H',
                                color if font.FONT[char][idx+x] & _BIT7 else background,
                                color if font.FONT[char][idx+x] & _BIT6 else background,
                                color if font.FONT[char][idx+x] & _BIT5 else background,
                                color if font.FONT[char][idx+x] & _BIT4 else background,
                                color if font.FONT[char][idx+x] & _BIT3 else background,
                                color if font.FONT[char][idx+x] & _BIT2 else background,
                                color if font.FONT[char][idx+x] & _BIT1 else background,
                                color if font.FONT[char][idx+x] & _BIT0 else background,
                                )
                        self.blit_buffer(buffer, x0, y0+(font.HEIGHT//self.num)*line, font.WIDTH, font.HEIGHT//self.num)
                x0 += font.WIDTH  # 显示下一个字的时候x坐标增加字体宽度
```

### （二）连接WiFi，同步时钟（WiFi.py）

```python
import ntptime
import network,time
from machine import RTC,Pin
rtc = RTC()
ssid = 'CU_1316'       # WiFi 账号
password = 'zhou1316'  # WiFi 密码
# 联WIFI
def WIFI_Connect():
    wlan = network.WLAN(network.STA_IF) #STA模式
    wlan.active(True)                   #激活接口
    start_time=time.time()              #记录时间做超时判断
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(ssid, password) #输入WIFI账号密码
        while not wlan.isconnected():
            if time.time()-start_time > 15 :
                print('WIFI Connected Timeout!')
                break
    if wlan.isconnected():
        print('connected!')
        print('network information:', wlan.ifconfig())

# 同步时间
def sync_ntp():
     ntptime.NTP_DELTA = 3155644800
     ntptime.host = 'ntp1.aliyun.com'
     try:
         ntptime.settime()
     except:
         print('同步失败')

if __name__ == '__main__':
    WIFI_Connect()
    sync_ntp()
    print(rtc.datetime())
    print("同步后本地时间：%s" %str(time.localtime()))
```

### （三）获取网络天气、诗词（weather.py）

天气API：心知天气

```python
def now_weather(self,city):
    #34.40:114.96
    url = "https://api.seniverse.com/v3/weather/now.json?key={}&location={}&language=zh-Hans&unit=c".format(self.password,city)
    result1=urequests.get(url)
    j1=ujson.loads(result1.text)
    _city = j1['results'][0]['location']['name']
    weather = j1['results'][0]['now']['text']
    tem = j1['results'][0]['now']['temperature']
    code = j1['results'][0]['now']['code']
    print(j1['results'][0]['location']['name'],end=' ')
    print(j1['results'][0]['now']['text'],end=' ')
    print(j1['results'][0]['now']['temperature'],end='℃ ')
    print(j1['results'][0]['last_update'])
    print('天气代码：',code)
    return {
        'city':_city,
        'weather':weather,
        'tem':tem,
        'code':code,
        'height':int(self.img_size(code)[3:]),
        'width':int(self.img_size(code)[0:2])
    }
def poet(self):
    # 获取句子
    url = 'https://api.a632079.me/?max_length=11'
    res=urequests.get(url)
    dic=ujson.loads(res.text)
    print(len(dic['hitokoto']),dic['hitokoto'])
    return dic['hitokoto'][:dic['length']]
def jinrishici(self):
    # 获取诗词
    url = 'https://v2.jinrishici.com/sentence'
    headers = {
        'X-User-Token':'EsnWc/+lex+Lgs7/m0clRHToBy/Eejy7'
    }
    res=urequests.get(url,headers=headers)
    dic=ujson.loads(res.text)
    if dic['status'] == 'success':
        return dic['data']
```

### （四）天气时钟界面(clock.py)

```python
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
```

### （五）诗词界面(poet.py)

```python
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
```

### （六）日历界面（calendar.py）

```python
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
                week_num += 1
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
```

### （七）main.py

```python
from machine import Pin, SPI, RTC
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
                self.tft.brightness(128)
                self.clock.clock()
            elif self.mod == _VERSE:
                self.tft.brightness(256)
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
```

