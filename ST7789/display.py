from machine import Pin, SPI, PWM
from utime   import sleep_ms as tsleep_ms
from math    import log      as mlog
import math
import gc

_SWRST   = b'\x01'
_SLPIN   = b'\x10'
_SLPOUT  = b'\x11'
_NORON   = b'\x13'
_COLMOD  = b'\x3A'
_MADCTL  = b'\x36'
_INVON   = b'\x21'
_DISPOFF = b'\x28'
_DISPON  = b'\x29'
_CASET   = b'\x2A'
_RASET   = b'\x2B'
_RAMWR   = b'\x2C'
_TEOFF   = b'\x34'
_TEON    = b'\x35'

class ST7789(object):
    def __init__(self, spi:SPI, dc:Pin, cs:Pin=None, rst:Pin=None, bl:Pin=None, baud:int=31_250_000, bright:int=0xFF, rot:int=0, width:int=240, height:int=240) -> None:
       
        spi.init(baudrate=baud, phase=0, polarity=(1 if cs is None else 0))
        
        self.__spi    = spi
        self.__cs     = cs
        self.__dc     = dc
        self._width   = width
        self._height  = height
        
        self.__rst = rst
        self.reset()   #reset display if a reset pin is defined
        
        self.__bl  = None
        if isinstance(bl, Pin):
            if bright > 0:
                self.__bl = PWM(bl)
                self.backlight(bright)
            else:
                self.__bl = bl
                self.__bl.value(1)

        self._command(_SWRST), tsleep_ms(150)  #software reset
        self.sleep_en(False)                    #sleep mode off
        
        #16 bits per pixel RGB565
        self._command(_COLMOD, b'\x05'), tsleep_ms(10)   
        
        self.rotation(rot)      #config memory address
        
        self._command(_INVON), tsleep_ms(10)   #inversion on
        self._command(_NORON), tsleep_ms(10)   #normal on
        self.display_en()                       #display on
        
    def _command(self, cmd, data=None, n:int=0) -> None:
        #_> convert cmd to bytes if int
        cmd = cmd if not isinstance(cmd, int) else cmd.to_bytes(1, 'big')
        #_> convert data to bytes if int
        if isinstance(data, int):
            n    = n if n else (1 if not data else int(mlog(data, 256)) + 1)
            data = data.to_bytes(n, 'big')
         
        #_> write cmd and data
        cs = isinstance(self.__cs, Pin)
        if cs: self.__cs.value(0)
            
        self.__dc.value(0), self.__spi.write(cmd)
        if data: self.__dc.value(1), self.__spi.write(data)
            
        if cs: self.__cs.value(1)
        
    def _set_win_addr(self, x:int, y:int, w:int, h:int) -> None:
        self._command(_CASET, (self.__startx + x) << 16 | (self.__startx + x + w - 1), 4)
        self._command(_RASET, (self.__starty + y) << 16 | (self.__starty + y + h - 1), 4)
    
    def display_en(self, enable:bool=True) -> None:
        self._command(_DISPON if enable else _DISPOFF), tsleep_ms(10)
    
    def sleep_en(self, enable:bool=True) -> None:
        self._command(_SLPIN if enable else _SLPOUT), tsleep_ms(10)
    
    def rotation(self, rot:int) -> None:
        cmd, self.__startx, self.__starty = ((0x00,0,0),(0xA0,320-self._width,0),(0xC0,0,320-self._height),(0x60,0,0))[(rot+360)//90%4]
        self._command(_MADCTL, cmd, 1)
    
    def reset(self, wait:int=10) -> None:
        if isinstance(self.__rst, Pin):
            for n in (1, 0, 1): self.__rst.value(n), tsleep_ms(wait)
        
    def backlight(self, bright:int=255) -> None:
        if isinstance(self.__bl, PWM):
            self.__bl.duty_u16(int(((min(bright, 255) / 255) ** 2.8) * 65534))
            
    def draw_buff(self, buff:memoryview, x:int, y:int, w:int, h:int) -> None:
        self._set_win_addr(x, y, w, h)
        self._command(_RAMWR, buff)
        
    #__> DIRECT DRAW ROUTINES
    def rgb565(self, c:int) -> int: 
        return int.from_bytes((((((c >> 16) & 248) >> 3) << 11) | ((((c >> 8 ) & 252) >> 2) << 5) | ((c & 248) >> 3)).to_bytes(2, 'big'), 'big')
    
    def rect(self, col:int, x:int, y:int, w:int, h:int, d:int=4) -> None:
        c = col.to_bytes(2, 'big')
        d = min(d, h)
        b = memoryview(bytearray(c*(w*d)))
        for yy in range(h//d):
            self.draw_buff(b, x, y+(yy*d), w, h)
            
    def clear(self, d:int=8) -> None:
        gc.collect()
        self.rect(0, 0, 0, self._width, self._height, d)
    
    def hline(self, col:int, x:int, y:int, L:int) -> None:
        self.rect(col, x, y, L, 1)
        
    def vline(self, col:int, x:int, y:int, L:int) -> None:
        self.rect(col, x, y, 1, L)
        
    def line(self, col:int, inix:int, iniy:int, endx:int, endy:int, w:int=1) -> None:
        c = col.to_bytes(2, 'big')
        if inix > endx:
            vals = endx
            endx = inix
            inix = valx
        if iniy > endy:
            valy = endy
            endy = iniy
            iniy = valy
        dx = endx - inix
        dy = endy - iniy
        if w == 0:
            w = 1

        if dx > dy:
            if endx == 240 and w > 1:
                endx = endx - w
            for xx in range(inix, endx, 1):
                yy = int( ((xx-inix) / dx) * dy )
                for ww in range(w):
                    self.draw_buff(c, xx, yy+ww, 1, 1)
        else:
            if endy == 240 and w > 1:
                endy = endy - w
            for yy in range(iniy, endy, 1):
                xx = int( ((yy-iniy) / dy) * dx )
                for ww in range(w):
                    self.draw_buff(c, xx+ww, yy, 1, 1)
        
    def circle(self, c:int, x:int, y:int, r:int, w:int=1) -> None:
        #To fill the circle, set w = 0
        verif = [999 for i in range(0, 240)]
        for xx in range(r+1):
            yy = int(math.sqrt(abs((r * r) - (xx * xx))))
            verif[yy] = yy
            if w == 0:
                for ww in range(xx):
                    self.draw_buff(c, x-ww, y+yy, 1, 1)
                    self.draw_buff(c, x-ww, y-yy, 1, 1)
                    self.draw_buff(c, x+ww, y-yy, 1, 1)
                    self.draw_buff(c, x+ww, y+yy, 1, 1)
                    
                    self.draw_buff(c, x-yy, y+ww, 1, 1)
                    self.draw_buff(c, x-yy, y-ww, 1, 1)
                    self.draw_buff(c, x+yy, y-ww, 1, 1)
                    self.draw_buff(c, x+yy, y+ww, 1, 1)
            else:
                for ww in range(w):
                    for www in range(w):
                        self.draw_buff(c, x-xx-ww, y+yy-www, 1, 1)
                        self.draw_buff(c, x-xx-ww, y-yy-www, 1, 1)
                        self.draw_buff(c, x+xx-ww, y+yy-www, 1, 1)
                        self.draw_buff(c, x+xx-ww, y-yy-www, 1, 1)
                        
                        self.draw_buff(c, x-yy-ww, y+xx-www, 1, 1)
                        self.draw_buff(c, x-yy-ww, y-xx-www, 1, 1)
                        self.draw_buff(c, x+yy-ww, y+xx-www, 1, 1)
                        self.draw_buff(c, x+yy-ww, y-xx-www, 1, 1)
            if w == 0:
                q = int(math.sqrt((r/2 * r/2) + (r/2 * r/2)))
                self.rect(c, int(x-q), int(y-q), 2*q, 2*q)

    def lozange (self, c:int, x:int, y:int, d:int, w:int=1) -> None:
        if w == 0:
            for yy in range (d+1):
                for xx in range(x-yy, x+yy):
                    self.rect(c, x+xx, y-d+yy, 1, 1)
                    self.rect(c, x+xx, y+d-yy, 1, 1)
        else:
            for yy in range (d):
                for ww in range (w):
                    self.rect(c, int((x+d)/2)-yy+ww, y+yy, 1, 1)
                    self.rect(c, int((x+d)/2)+yy+ww, y+yy, 1, 1)
                    self.rect(c, int((x+d)/2)-yy+ww, y+d+d-yy, 1, 1)
                    self.rect(c, int((x+d)/2)+yy+ww, y+d+d-yy, 1, 1)
                
    def sablier (self, c:int, x:int, y:int, d:int, w:int=1) -> None:
        if w == 0:
            for yy in range (d+1):
                for xx in range(x-yy, x+yy):
                    self.rect(c, x+xx, y+yy, 1, 1)
                    self.rect(c, x+xx, y-yy, 1, 1)
        else:
            for yy in range (d):
                for ww in range (w):
                    self.rect(c, int((x+d)/2)-yy-ww, y+yy, 1, 1)
                    self.rect(c, int((x+d)/2)+yy+ww, y+yy, 1, 1)
                    self.rect(c, int((x+d)/2)-yy-ww, y-yy, 1, 1)
                    self.rect(c, int((x+d)/2)+yy+ww, y-yy, 1, 1)
            for xx in range(2*d):
                for ww in range(w):
                    self.rect(c, x-d-d+xx, y-d+ww, 1, 1)
                    self.rect(c, x-d-d+xx, y+d+ww, 1, 1)
        
    def triangleH (self, c:int, x:int, y:int, d:int, w:int=1) -> None:
        if w == 0:
            for yy in range (d+1):
                for xx in range(x-yy, x+yy):
                    self.rect(c, x+xx, y+yy, 1, 1)
        else:
            for yy in range (d):
                for ww in range (w):
                    self.rect(c, int((x+d)/2)-yy-ww, y+yy, 1, 1)
                    self.rect(c, int((x+d)/2)+yy+ww, y+yy, 1, 1)
            for xx in range(2*d):
                for ww in range(w):
                    self.rect(c, x-d-d+xx, y+d+ww, 1, 1)
        
    def triangleB (self, c:int, x:int, y:int, d:int, w:int=1) -> None:
        if w == 0:
            for yy in range (d+1):
                for xx in range(x-yy, x+yy):
                    self.rect(c, x+xx, y-yy, 1, 1)
        else:
            for yy in range (d):
                for ww in range (w):
                    self.rect(c, int((x+d)/2)-yy-ww, y-yy, 1, 1)
                    self.rect(c, int((x+d)/2)+yy+ww, y-yy, 1, 1)
            for xx in range(2*d):
                for ww in range(w):
                    self.rect(c, x-d-d+xx, y-d+ww, 1, 1)
    def thermometre (self, ct, cm, x:int=0, y:int=10, temp:int=0, sx:int=1, sy:int=1, tempMax:int=50, tempMin:int=-50, nbGr:int=5):
        # ct: couleur du contour
        # cm: couleur du mercure
        # x: abcisse du coin supérieur gauche
        # y: ordonnée du coin supérieur droit
        # temp: température à afficher
        # sx: étirement horizontal
        # sy: étirement vertical
        # tempMax: température maximale affichée
        # tempMin: température minimale affichée
        # nbGr: nombre de graduations sur l'échelle

        self.circle(ct, x+23, y+121, 18*sx, 1)
        self.circle(ct, x+24, y+0,   11*sx, 1)
        self.vline (ct, x+14, y+0,   108*sy)
        self.vline (ct, x+34, y+0,   108*sy)
        self.hline (ct, x+0,  y+4,   8*sx)
        self.hline (ct, x+0,  y+24,  8*sx)
        self.hline (ct, x+0,  y+44,  8*sx)
        self.hline (ct, x+0,  y+64,  8*sx)
        self.hline (ct, x+0,  y+84,  8*sx)
        self.hline (ct, x+0,  y+105, 8*sx)
        self.rect  (self.rgb565(0x000000), x+15, y+1, 18*sx, 20*sy, 1)
        self.rect  (self.rgb565(0x000000), x+15, y+100, 18*sx, 20*sy, 1)
        self.circle(cm, x+24, y+121, 11*sx, 0)
        print (" temp = " + str(temp))
        print (" tempMax = " + str(tempMax))
        print (" tempMin = " + str(tempMin))
        print (" Écart total : " + str(tempMax-tempMin))
        print (" sx = " + str(sx))

    def temperature(self, cm, x:int=0, y:int=10, temp:int=0, sx:int=1, sy:int=1, tempMax:int=50, tempMin:int=-50, nbGr:int=5):
        self.rect  (self.rgb565(0x000000), x+19, y,  12*sx, 104, 1)
        tempRel = int(((tempMax+temp)/(tempMax-tempMin)) * 104*sy)
        if tempRel > 104*sy:
            tempRel = 104*sy

        self.rect  (cm, x+19, y+104-tempRel,  12*sx, 14+tempRel, 1)
