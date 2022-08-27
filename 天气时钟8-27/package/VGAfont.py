class Font:
    def __init__(self, size):
        self.WIDTH = size // 2
        self.HEIGHT = size
        self.SIZE = size * size // 16
        self.FONT = {}


class VGAFONT(object):
    def __init__(self, size):
        self.f = open('./package/vga1_{}x{}.ttf'.format(size//2,size), 'rb')
        self.height = size
        self.size = size * (size // 8) // 2

    def one_char(self, char):
        ascii = ord(char) - 0x20
        self.f.seek(ascii*self.size)
        return self.f.read(self.size)


    def str(self, st):
        font = Font(self.height)
        for s in st:
            data = self.one_char(s)
            font.FONT[s] = data if data else b'\x00' * self.size
        #print(font)
        return font



    def __del__(self):
        self.f.close()


if __name__ == '__main__':
    F = VGAFONT(48)
    import utime
    import ustruct as struct
    from micropython import const
    _BIT7 = const(0x80)
    _BIT6 = const(0x40)
    _BIT5 = const(0x20)
    _BIT4 = const(0x10)
    _BIT3 = const(0x08)
    _BIT2 = const(0x04)
    _BIT1 = const(0x02)
    _BIT0 = const(0x01)
    #char = F.one_char('a')
    #print(char,len(char))
    ts = utime.ticks_ms()
    text='abcdefg123'
    font = F.str(text)
    num=2
    color = 0
    background = 0xff
    x0 = 0
    for char in text:
            #if (x0+font.WIDTH <= self.width and y0+font.HEIGHT <= self.height):
                for line in range(num):  # 分两次显示，先显示上半边后显示下半边
                        idx = line * (font.SIZE//num)
                        buffer = b''
                        for x in range(0,(font.SIZE//num),4):
                            buffer += struct.pack('>16H',
                                color if font.FONT[char][idx+x] & _BIT7 else background,
                                color if font.FONT[char][idx+x] & _BIT6 else background,
                                color if font.FONT[char][idx+x] & _BIT5 else background,
                                color if font.FONT[char][idx+x] & _BIT4 else background,
                                color if font.FONT[char][idx+x] & _BIT3 else background,
                                color if font.FONT[char][idx+x] & _BIT2 else background,
                                color if font.FONT[char][idx+x] & _BIT1 else background,
                                color if font.FONT[char][idx+x] & _BIT0 else background,
                                color if font.FONT[char][idx+x+1] & _BIT7 else background,
                                color if font.FONT[char][idx+x+1] & _BIT6 else background,
                                color if font.FONT[char][idx+x+1] & _BIT5 else background,
                                color if font.FONT[char][idx+x+1] & _BIT4 else background,
                                color if font.FONT[char][idx+x+1] & _BIT3 else background,
                                color if font.FONT[char][idx+x+1] & _BIT2 else background,
                                color if font.FONT[char][idx+x+1] & _BIT1 else background,
                                color if font.FONT[char][idx+x+1] & _BIT0 else background,
                                color if font.FONT[char][idx+x+2] & _BIT7 else background,
                                color if font.FONT[char][idx+x+2] & _BIT6 else background,
                                color if font.FONT[char][idx+x+2] & _BIT5 else background,
                                color if font.FONT[char][idx+x+2] & _BIT4 else background,
                                color if font.FONT[char][idx+x+2] & _BIT3 else background,
                                color if font.FONT[char][idx+x+2] & _BIT2 else background,
                                color if font.FONT[char][idx+x+2] & _BIT1 else background,
                                color if font.FONT[char][idx+x+2] & _BIT0 else background,
                                color if font.FONT[char][idx+x+3] & _BIT7 else background,
                                color if font.FONT[char][idx+x+3] & _BIT6 else background,
                                color if font.FONT[char][idx+x+3] & _BIT5 else background,
                                color if font.FONT[char][idx+x+3] & _BIT4 else background,
                                color if font.FONT[char][idx+x+3] & _BIT3 else background,
                                color if font.FONT[char][idx+x+3] & _BIT2 else background,
                                color if font.FONT[char][idx+x+3] & _BIT1 else background,
                                color if font.FONT[char][idx+x+3] & _BIT0 else background,
                                )
                x0 += font.WIDTH  # 显示下一个字的时候x坐标增加字体宽度
    te = utime.ticks_ms()
    tc = te - ts
    print(tc)
    #print(t.HEIGHT, t.FONT)

