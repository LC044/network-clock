import time
from micropython import const
import ustruct as struct

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
# commands
ST7789_NOP = const(0x00)
ST7789_SWRESET = const(0x01)
ST7789_RDDID = const(0x04)
ST7789_RDDST = const(0x09)

ST7789_SLPIN = const(0x10)
ST7789_SLPOUT = const(0x11)
ST7789_PTLON = const(0x12)
ST7789_NORON = const(0x13)

ST7789_INVOFF = const(0x20)
ST7789_INVON = const(0x21)
ST7789_DISPOFF = const(0x28)
ST7789_DISPON = const(0x29)
ST7789_CASET = const(0x2A)
ST7789_RASET = const(0x2B)
ST7789_RAMWR = const(0x2C)
ST7789_RAMRD = const(0x2E)

ST7789_PTLAR = const(0x30)
ST7789_VSCRDEF = const(0x33)
ST7789_COLMOD = const(0x3A)
ST7789_MADCTL = const(0x36)
ST7789_VSCSAD = const(0x37)

ST7789_MADCTL_MY = const(0x80)
ST7789_MADCTL_MX = const(0x40)
ST7789_MADCTL_MV = const(0x20)
ST7789_MADCTL_ML = const(0x10)
ST7789_MADCTL_BGR = const(0x08)
ST7789_MADCTL_MH = const(0x04)
ST7789_MADCTL_RGB = const(0x00)

ST7789_RDID1 = const(0xDA)
ST7789_RDID2 = const(0xDB)
ST7789_RDID3 = const(0xDC)
ST7789_RDID4 = const(0xDD)

COLOR_MODE_65K = const(0x50)
COLOR_MODE_262K = const(0x60)
COLOR_MODE_12BIT = const(0x03)
COLOR_MODE_16BIT = const(0x05)
COLOR_MODE_18BIT = const(0x06)
COLOR_MODE_16M = const(0x07)

# Color definitions
BLACK = const(0x0000)
BLUE = const(0x001F)
RED = const(0xF800)
GREEN = const(0x07E0)
CYAN = const(0x07FF)
MAGENTA = const(0xF81F)
YELLOW = const(0xFFE0)
WHITE = const(0xFFFF)

_ENCODE_PIXEL = ">H"
_ENCODE_POS = ">HH"
_DECODE_PIXEL = ">BBB"

_BUFFER_SIZE = const(256)

_BIT7 = const(0x80)
_BIT6 = const(0x40)
_BIT5 = const(0x20)
_BIT4 = const(0x10)
_BIT3 = const(0x08)
_BIT2 = const(0x04)
_BIT1 = const(0x02)
_BIT0 = const(0x01)
_BIT = [_BIT0, _BIT1, _BIT2, _BIT3, _BIT4,_BIT5, _BIT6, _BIT7]
# Rotation tables (width, height, xstart, ystart)[rotation % 4]

WIDTH_320 = [(240, 320,  0,  0),
             (320, 240,  0,  0),
             (240, 320,  0,  0),
             (320, 240,  0,  0)]

WIDTH_240 = [(240, 240,  0,  0),
             (240, 240,  0,  0),
             (240, 240,  0, 80),
             (240, 240, 80,  0)]

WIDTH_135 = [(135, 240, 52, 40),
             (240, 135, 40, 53),
             (135, 240, 53, 40),
             (240, 135, 40, 52)]

# MADCTL ROTATIONS[rotation % 4]
ROTATIONS = [0x00, 0x60, 0xc0, 0xa0]


def color565(red, green=0, blue=0):
    """
    Convert red, green and blue values (0-255) into a 16-bit 565 encoding.
    """
    try:
        red, green, blue = red  # see if the first var is a tuple/list
    except TypeError:
        pass
    return (red & 0xf8) << 8 | (green & 0xfc) << 3 | blue >> 3


def _encode_pos(x, y):
    """Encode a postion into bytes."""
    return struct.pack(_ENCODE_POS, x, y)


def _encode_pixel(color):
    """Encode a pixel color into bytes."""
    return struct.pack(_ENCODE_PIXEL, color)


class ST7789():
    def __init__(self, spi, width, height, reset=None, dc=None,
                 cs=None, backlight=None, rotation=0):
        self.num = 4
        """
        Initialize display.
        """
        if height != 240 or width not in [320, 240, 135]:
            raise ValueError(
                "Unsupported display. 320x240, 240x240 and 135x240 are supported."
            )

        if dc is None:
            raise ValueError("dc pin is required.")

        self._display_width = self.width = width
        self._display_height = self.height = height
        self.xstart = 0
        self.ystart = 0
        self.spi = spi
        self.reset = reset
        self.dc = dc
        self.cs = cs
        self.backlight = backlight
        self._rotation = rotation % 4
        self.cs.init(self.cs.OUT, value=1)
        self.dc.init(self.dc.OUT, value=0)
        self.reset.init(self.reset.OUT, value=1)
        self.sleep_mode(False)

        self._set_color_mode(COLOR_MODE_65K | COLOR_MODE_16BIT)
        time.sleep_ms(50)
        self.rotation(self._rotation)
        self.inversion_mode(True)
        time.sleep_ms(10)
        self._write(ST7789_NORON)
        time.sleep_ms(10)
        if backlight is not None:
            from machine import Pin,PWM
            self.bl = PWM(self.backlight,freq=1000,duty=128)
        self.fill(0)
        self._write(ST7789_DISPON)
        time.sleep_ms(500)
    def brightness(self,value):
        '''
        调节背光亮度
        value: int 0-1023  建议值 <256
        '''
        self.bl.duty(value)
    def _write(self, command=None, data=None):
        """SPI write to the device: commands and data."""
        if self.cs:
            self.cs.off()

        if command is not None:
            self.dc.off()
            self.spi.write(bytes([command]))
        if data is not None:
            self.dc.on()
            self.spi.write(data)
            if self.cs:
                self.cs.on()

    def sleep_mode(self, value):
        if value:
            self._write(ST7789_SLPIN)
        else:
            self._write(ST7789_SLPOUT)

    def inversion_mode(self, value):
        if value:
            self._write(ST7789_INVON)
        else:
            self._write(ST7789_INVOFF)

    def _set_color_mode(self, mode):
        self._write(ST7789_COLMOD, bytes([mode & 0x77]))

    def rotation(self, rotation):
        rotation %= 4
        self._rotation = rotation
        madctl = ROTATIONS[rotation]

        if self._display_width == 320:
            table = WIDTH_320
        elif self._display_width == 240:
            table = WIDTH_240
        elif self._display_width == 135:
            table = WIDTH_135
        else:
            raise ValueError(
                "Unsupported display. 320x240, 240x240 and 135x240 are supported."
            )

        self.width, self.height, self.xstart, self.ystart = table[rotation]
        self._write(ST7789_MADCTL, bytes([madctl]))

    def _set_columns(self, start, end):
        if start <= end <= self.width:
            self._write(ST7789_CASET, _encode_pos(
                start+self.xstart, end + self.xstart))

    def _set_rows(self, start, end):
        if start <= end <= self.height:
            self._write(ST7789_RASET, _encode_pos(
                start+self.ystart, end+self.ystart))

    def _set_window(self, x0, y0, x1, y1):
        self._set_columns(x0, x1)
        self._set_rows(y0, y1)
        self._write(ST7789_RAMWR)

    def vline(self, x, y, length, color):
        self.fill_rect(x, y, 1, length, color)

    def hline(self, x, y, length, color):
        self.fill_rect(x, y, length, 1, color)

    def pixel(self, x, y, color):
        self._set_window(x, y, x, y)
        self._write(None, _encode_pixel(color))

    def blit_buffer(self, buffer, x, y, width, height):
        self._set_window(x, y, x + width - 1, y + height - 1)
        self._write(None, buffer)

    def rect(self, x, y, w, h, color):
        self.hline(x, y, w, color)
        self.vline(x, y, h, color)
        self.vline(x + w - 1, y, h, color)
        self.hline(x, y + h - 1, w, color)

    def fill_rect(self, x, y, width, height, color):
        self._set_window(x, y, x + width - 1, y + height - 1)
        chunks, rest = divmod(width * height, _BUFFER_SIZE)
        pixel = _encode_pixel(color)
        self.dc.on()
        if chunks:
            data = pixel * _BUFFER_SIZE
            for _ in range(chunks):
                self._write(None, data)
        if rest:
            self._write(None, pixel * rest)

    def fill(self, color):
        self.fill_rect(0, 0, self.width, self.height, color)

    def line(self, x0, y0, x1, y1, color):
        steep = abs(y1 - y0) > abs(x1 - x0)
        if steep:
            x0, y0 = y0, x0
            x1, y1 = y1, x1
        if x0 > x1:
            x0, x1 = x1, x0
            y0, y1 = y1, y0
        dx = x1 - x0
        dy = abs(y1 - y0)
        err = dx // 2
        ystep = 1 if y0 < y1 else -1
        while x0 <= x1:
            if steep:
                self.pixel(y0, x0, color)
            else:
                self.pixel(x0, y0, color)
            err -= dy
            if err < 0:
                y0 += ystep
                err += dx
            x0 += 1

    def vscrdef(self, tfa, vsa, bfa):
        struct.pack(">HHH", tfa, vsa, bfa)
        self._write(ST7789_VSCRDEF, struct.pack(">HHH", tfa, vsa, bfa))

    def vscsad(self, vssa):
        self._write(ST7789_VSCSAD, struct.pack(">H", vssa))
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
    def _text(self,font,size, text, x0, y0, color=WHITE, background=BLACK):
        self.k = 0
        self.num = 1
        passes, rest = divmod(font.SIZE,16)
        for char in text:
            if (x0+font.WIDTH <= self.width and y0+font.HEIGHT <= self.height):
                buffer = b''
                for line in range(passes):
                    idx = line * 16
                    x = 0
                    buffer += struct.pack('>128H',
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
                        color if font.FONT[char][idx+x+4] & _BIT7 else background,
                        color if font.FONT[char][idx+x+4] & _BIT6 else background,
                        color if font.FONT[char][idx+x+4] & _BIT5 else background,
                        color if font.FONT[char][idx+x+4] & _BIT4 else background,
                        color if font.FONT[char][idx+x+4] & _BIT3 else background,
                        color if font.FONT[char][idx+x+4] & _BIT2 else background,
                        color if font.FONT[char][idx+x+4] & _BIT1 else background,
                        color if font.FONT[char][idx+x+4] & _BIT0 else background,
                        color if font.FONT[char][idx+x+5] & _BIT7 else background,
                        color if font.FONT[char][idx+x+5] & _BIT6 else background,
                        color if font.FONT[char][idx+x+5] & _BIT5 else background,
                        color if font.FONT[char][idx+x+5] & _BIT4 else background,
                        color if font.FONT[char][idx+x+5] & _BIT3 else background,
                        color if font.FONT[char][idx+x+5] & _BIT2 else background,
                        color if font.FONT[char][idx+x+5] & _BIT1 else background,
                        color if font.FONT[char][idx+x+5] & _BIT0 else background,
                        color if font.FONT[char][idx+x+6] & _BIT7 else background,
                        color if font.FONT[char][idx+x+6] & _BIT6 else background,
                        color if font.FONT[char][idx+x+6] & _BIT5 else background,
                        color if font.FONT[char][idx+x+6] & _BIT4 else background,
                        color if font.FONT[char][idx+x+6] & _BIT3 else background,
                        color if font.FONT[char][idx+x+6] & _BIT2 else background,
                        color if font.FONT[char][idx+x+6] & _BIT1 else background,
                        color if font.FONT[char][idx+x+6] & _BIT0 else background,
                        color if font.FONT[char][idx+x+7] & _BIT7 else background,
                        color if font.FONT[char][idx+x+7] & _BIT6 else background,
                        color if font.FONT[char][idx+x+7] & _BIT5 else background,
                        color if font.FONT[char][idx+x+7] & _BIT4 else background,
                        color if font.FONT[char][idx+x+7] & _BIT3 else background,
                        color if font.FONT[char][idx+x+7] & _BIT2 else background,
                        color if font.FONT[char][idx+x+7] & _BIT1 else background,
                        color if font.FONT[char][idx+x+7] & _BIT0 else background,
                        color if font.FONT[char][idx+x+8] & _BIT7 else background,
                        color if font.FONT[char][idx+x+8] & _BIT6 else background,
                        color if font.FONT[char][idx+x+8] & _BIT5 else background,
                        color if font.FONT[char][idx+x+8] & _BIT4 else background,
                        color if font.FONT[char][idx+x+8] & _BIT3 else background,
                        color if font.FONT[char][idx+x+8] & _BIT2 else background,
                        color if font.FONT[char][idx+x+8] & _BIT1 else background,
                        color if font.FONT[char][idx+x+8] & _BIT0 else background,
                        color if font.FONT[char][idx+x+9] & _BIT7 else background,
                        color if font.FONT[char][idx+x+9] & _BIT6 else background,
                        color if font.FONT[char][idx+x+9] & _BIT5 else background,
                        color if font.FONT[char][idx+x+9] & _BIT4 else background,
                        color if font.FONT[char][idx+x+9] & _BIT3 else background,
                        color if font.FONT[char][idx+x+9] & _BIT2 else background,
                        color if font.FONT[char][idx+x+9] & _BIT1 else background,
                        color if font.FONT[char][idx+x+9] & _BIT0 else background,
                        color if font.FONT[char][idx+x+10] & _BIT7 else background,
                        color if font.FONT[char][idx+x+10] & _BIT6 else background,
                        color if font.FONT[char][idx+x+10] & _BIT5 else background,
                        color if font.FONT[char][idx+x+10] & _BIT4 else background,
                        color if font.FONT[char][idx+x+10] & _BIT3 else background,
                        color if font.FONT[char][idx+x+10] & _BIT2 else background,
                        color if font.FONT[char][idx+x+10] & _BIT1 else background,
                        color if font.FONT[char][idx+x+10] & _BIT0 else background,
                        color if font.FONT[char][idx+x+11] & _BIT7 else background,
                        color if font.FONT[char][idx+x+11] & _BIT6 else background,
                        color if font.FONT[char][idx+x+11] & _BIT5 else background,
                        color if font.FONT[char][idx+x+11] & _BIT4 else background,
                        color if font.FONT[char][idx+x+11] & _BIT3 else background,
                        color if font.FONT[char][idx+x+11] & _BIT2 else background,
                        color if font.FONT[char][idx+x+11] & _BIT1 else background,
                        color if font.FONT[char][idx+x+11] & _BIT0 else background,
                        color if font.FONT[char][idx+x+12] & _BIT7 else background,
                        color if font.FONT[char][idx+x+12] & _BIT6 else background,
                        color if font.FONT[char][idx+x+12] & _BIT5 else background,
                        color if font.FONT[char][idx+x+12] & _BIT4 else background,
                        color if font.FONT[char][idx+x+12] & _BIT3 else background,
                        color if font.FONT[char][idx+x+12] & _BIT2 else background,
                        color if font.FONT[char][idx+x+12] & _BIT1 else background,
                        color if font.FONT[char][idx+x+12] & _BIT0 else background,
                        color if font.FONT[char][idx+x+13] & _BIT7 else background,
                        color if font.FONT[char][idx+x+13] & _BIT6 else background,
                        color if font.FONT[char][idx+x+13] & _BIT5 else background,
                        color if font.FONT[char][idx+x+13] & _BIT4 else background,
                        color if font.FONT[char][idx+x+13] & _BIT3 else background,
                        color if font.FONT[char][idx+x+13] & _BIT2 else background,
                        color if font.FONT[char][idx+x+13] & _BIT1 else background,
                        color if font.FONT[char][idx+x+13] & _BIT0 else background,
                        color if font.FONT[char][idx+x+14] & _BIT7 else background,
                        color if font.FONT[char][idx+x+14] & _BIT6 else background,
                        color if font.FONT[char][idx+x+14] & _BIT5 else background,
                        color if font.FONT[char][idx+x+14] & _BIT4 else background,
                        color if font.FONT[char][idx+x+14] & _BIT3 else background,
                        color if font.FONT[char][idx+x+14] & _BIT2 else background,
                        color if font.FONT[char][idx+x+14] & _BIT1 else background,
                        color if font.FONT[char][idx+x+14] & _BIT0 else background,
                        color if font.FONT[char][idx+x+15] & _BIT7 else background,
                        color if font.FONT[char][idx+x+15] & _BIT6 else background,
                        color if font.FONT[char][idx+x+15] & _BIT5 else background,
                        color if font.FONT[char][idx+x+15] & _BIT4 else background,
                        color if font.FONT[char][idx+x+15] & _BIT3 else background,
                        color if font.FONT[char][idx+x+15] & _BIT2 else background,
                        color if font.FONT[char][idx+x+15] & _BIT1 else background,
                        color if font.FONT[char][idx+x+15] & _BIT0 else background,
                        )
                if rest:
                    for i in range(rest//4):
                        idx = i * 4 + font.SIZE - rest
                        buffer += struct.pack(
                            '>32H',
                            color if font.FONT[char][idx] & _BIT7 else background,
                            color if font.FONT[char][idx] & _BIT6 else background,
                            color if font.FONT[char][idx] & _BIT5 else background,
                            color if font.FONT[char][idx] & _BIT4 else background,
                            color if font.FONT[char][idx] & _BIT3 else background,
                            color if font.FONT[char][idx] & _BIT2 else background,
                            color if font.FONT[char][idx] & _BIT1 else background,
                            color if font.FONT[char][idx] & _BIT0 else background,
                            color if font.FONT[char][idx+1] & _BIT7 else background,
                            color if font.FONT[char][idx+1] & _BIT6 else background,
                            color if font.FONT[char][idx+1] & _BIT5 else background,
                            color if font.FONT[char][idx+1] & _BIT4 else background,
                            color if font.FONT[char][idx+1] & _BIT3 else background,
                            color if font.FONT[char][idx+1] & _BIT2 else background,
                            color if font.FONT[char][idx+1] & _BIT1 else background,
                            color if font.FONT[char][idx+1] & _BIT0 else background,
                            color if font.FONT[char][idx+2] & _BIT7 else background,
                            color if font.FONT[char][idx+2] & _BIT6 else background,
                            color if font.FONT[char][idx+2] & _BIT5 else background,
                            color if font.FONT[char][idx+2] & _BIT4 else background,
                            color if font.FONT[char][idx+2] & _BIT3 else background,
                            color if font.FONT[char][idx+2] & _BIT2 else background,
                            color if font.FONT[char][idx+2] & _BIT1 else background,
                            color if font.FONT[char][idx+2] & _BIT0 else background,
                            color if font.FONT[char][idx+3] & _BIT7 else background,
                            color if font.FONT[char][idx+3] & _BIT6 else background,
                            color if font.FONT[char][idx+3] & _BIT5 else background,
                            color if font.FONT[char][idx+3] & _BIT4 else background,
                            color if font.FONT[char][idx+3] & _BIT3 else background,
                            color if font.FONT[char][idx+3] & _BIT2 else background,
                            color if font.FONT[char][idx+3] & _BIT1 else background,
                            color if font.FONT[char][idx+3] & _BIT0 else background,
                            )
                self.blit_buffer(buffer, x0, y0, font.WIDTH, font.HEIGHT)
                x0 += font.WIDTH  # 显示下一个字的时候x坐标增加字体宽度
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

    def bitmap(self, bitmap, x, y, index=0):
        bitmap_size = bitmap.HEIGHT * bitmap.WIDTH
        buffer_len = bitmap_size * 2
        buffer = bytearray(buffer_len)
        bs_bit = bitmap.BPP * bitmap_size * index if index > 0 else 0

        for i in range(0, buffer_len, 2):
            color_index = 0
            for _ in range(bitmap.BPP):
                color_index <<= 1
                color_index |= (bitmap.BITMAP[bs_bit // 8]
                                & 1 << (7 - (bs_bit % 8))) > 0
                bs_bit += 1

            color = bitmap.PALETTE[color_index]
            buffer[i] = color & 0xff00 >> 8
            buffer[i + 1] = color_index & 0xff

        to_col = x + bitmap.WIDTH - 1
        to_row = y + bitmap.HEIGHT - 1
        if self.width > to_col and self.height > to_row:
            self._set_window(x, y, to_col, to_row)
            self._write(None, buffer)

    # @micropython.native
    def write(self, font, string, x, y, fg=WHITE, bg=BLACK):
        buffer_len = font.HEIGHT * font.MAX_WIDTH * 2
        buffer = bytearray(buffer_len)
        fg_hi = (fg & 0xff00) >> 8
        fg_lo = fg & 0xff

        bg_hi = (bg & 0xff00) >> 8
        bg_lo = bg & 0xff

        for character in string:
            try:
                char_index = font.MAP.index(character)
                offset = char_index * font.OFFSET_WIDTH
                bs_bit = font.OFFSETS[offset]
                if font.OFFSET_WIDTH > 1:
                    bs_bit = (bs_bit << 8) + font.OFFSETS[offset + 1]

                if font.OFFSET_WIDTH > 2:
                    bs_bit = (bs_bit << 8) + font.OFFSETS[offset + 2]

                char_width = font.WIDTHS[char_index]
                buffer_needed = char_width * font.HEIGHT * 2

                for i in range(0, buffer_needed, 2):
                    if font.BITMAPS[bs_bit // 8] & 1 << (7 - (bs_bit % 8)) > 0:
                        buffer[i] = fg_hi
                        buffer[i + 1] = fg_lo
                    else:
                        buffer[i] = bg_hi
                        buffer[i + 1] = bg_lo

                    bs_bit += 1

                to_col = x + char_width - 1
                to_row = y + font.HEIGHT - 1
                if self.width > to_col and self.height > to_row:
                    self._set_window(x, y, to_col, to_row)
                    self._write(None, buffer[:buffer_needed])

                x += char_width

            except ValueError:
                pass

    def write_width(self, font, string):
        width = 0
        for character in string:
            try:
                char_index = font.MAP.index(character)
                width += font.WIDTHS[char_index]

            except ValueError:
                pass

        return width
