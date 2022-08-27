class Font:
    def __init__(self,size):
        self.WIDTH = size
        self.HEIGHT = size
        self.SIZE = size * (size // 8)
        self.FONT = {}
    
class gb2312(object):
    __slots__ = 'WIDTH', 'HEIGHT', 'SIZE' , 'FONT'
    def __init__(self,size):
        self.f = open('./package/gb{0}x{0}.ttf'.format(size), 'rb')
        self.height = size
        self.size = size * (size // 8) + 3
        self.num = 21791 if size==16 else 7445
    def b2i(self, byte):
        r = 0
        for i in range(len(byte)):
            r = (r << 8) | byte[i]
        return r

    def i2b(self, num):
        #num = int(num, 16)
        return num.to_bytes(3, 'big')

    def one_char(self, char):
        utf_byte = char.encode('utf-8')
        return self.B_S(0, self.num, self.b2i(utf_byte))
    
    def str(self,st):
        font = Font(self.height)
        for s in st:
            data = self.one_char(s) 
            font.FONT[s] = data if data else b'\x00'*self.size
        return font
    def B_S(self, low, high, m):
        while low <= high:
            mid = (low + high) // 2
            self.f.seek(mid * self.size)
            utf = self.b2i(self.f.read(3))
            if utf < m:
                low = mid + 1
            elif utf > m:
                high = mid - 1
            else:
                #return mid
                return self.f.read(self.size-3)
                #return data[3:]
    def __del__(self):
        self.f.close()

if __name__ == '__main__':
    F = gb2312(24)
    char = F.one_char('你')
    print(char)
    '''
    import utime
    #char = F.one_char('a')
    #print(char,len(char))
    ts = utime.ticks_ms()
    t = F.str('风急天高猿啸哀，渚清沙白鸟飞回。')
    te = utime.ticks_ms()
    tc = te - ts
    print(tc/16)
    #print(t.HEIGHT,t.FONT)'''
        