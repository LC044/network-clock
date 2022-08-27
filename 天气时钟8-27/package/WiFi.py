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


