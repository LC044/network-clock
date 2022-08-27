import urequests
import ujson
from package import WiFi
import uzlib as zlib
FTEXT    = 1
FHCRC    = 2
FEXTRA   = 4
FNAME    = 8
FCOMMENT = 16
class Weather():
    def __init__(self):
        WiFi.WIFI_Connect()
        WiFi.sync_ntp()
        self.ssid = 'P_083oXK8ImwN8XJl'
        self.password ='SpsL1FI3kR56iaePC'
    def img_size(self,code):
        size = ['48x48','48x48','48x48','48x48',
                '58x38','58x41','58x48','58x41',
                '58x48','58x38','58x57','58x58',
                '58x58','58x57','58x57','58x58',
                '58x58','61x61','61x61','58x58',
                '58x57','58x58','58x55','58x55',
                '58x55','58x58','58x49','58x49',
                '58x34','58x34','56x51','58x51',
                '58x46','58x46','58x58','58x58',
                '58x57','50x58','48x48'
                ]
        return size[int(code)]
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
        #print(j1)
        return {
            'city':_city,
            'weather':weather,
            'tem':tem,
            'code':code,
            'height':int(self.img_size(code)[3:]),
            'width':int(self.img_size(code)[0:2])
            }
    def decompress(self,data):
        assert data[0] == 0x1f and data[1] == 0x8b
        assert data[2] == 8
        flg = data[3]
        assert flg & 0xe0 == 0
        i = 10
        if flg & FEXTRA:
            i += data[11] << 8 + data[10] + 2
        if flg & FNAME:
            while data[i]:
                i += 1
            i += 1
        if flg & FCOMMENT:
            while data[i]:
                i += 1
            i += 1
        if flg & FHCRC:
            i += 2
        return zlib.decompress(memoryview(data)[i:], -15)
    def air(self,location):
        url = 'https://devapi.qweather.com/v7/air/now?key=57f8af25a47443a79c41a1d6f771efc3&location={}'.format(location)
        res=urequests.get(url)
        data=self.decompress(res.content).decode()
        dic=ujson.loads(data)
        if dic['code'] == '200':
            aqi = dic['now']['aqi']
            category = dic['now']['category']
            return aqi,category
        return None
    def HF_weather(self,location):
        url = 'https://devapi.qweather.com/v7/weather/now?location=101010100&key=57f8af25a47443a79c41a1d6f771efc3&location={}'.format(location)
        res=urequests.get(url)
        data=self.decompress(res.content).decode()
        dic=ujson.loads(data)
        if dic['code'] == '200':
            humidity = dic['now']['humidity']
            return humidity
        return None
    def poet(self):
        url = 'https://api.a632079.me/?max_length=11'
        res=urequests.get(url)
        dic=ujson.loads(res.text)
        print(len(dic['hitokoto']),dic['hitokoto'])
        return dic['hitokoto'][:dic['length']]
    def jinrishici(self):
        url = 'https://v2.jinrishici.com/sentence'
        headers = {
                'X-User-Token':'EsnWc/+lex+Lgs7/m0clRHToBy/Eejy7'
            }
        res=urequests.get(url,headers=headers)
        dic=ujson.loads(res.text)
        if dic['status'] == 'success':
            return dic['data']
if __name__=='__main__':
    W = Weather()
    W.jinrishici()
