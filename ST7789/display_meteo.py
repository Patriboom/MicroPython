import st7789 as st7789orig
from st7789  import ST7789 as st7789
from utime   import sleep_ms as tsleep_ms
from math    import log      as mlog
import math
import gc
from time import sleep, sleep_ms

class meteo (st7789):
    def __init__(self, spi, width, height, reset, dc, cs=None, backlight=None, xstart=0, ystart=0, rotation=0) -> None :
        super().__init__(spi, width, height, reset, dc, cs, backlight, xstart, ystart, rotation)
        self.ct = st7789orig.color565(150, 0, 255)   # ct: couleur du contour
        self.cm = st7789orig.color565(255, 0, 0)   # cm: couleur du mercure
        self.x = 0         # x: abcisse du coin supérieur gauche
        self.y = 10        # y: ordonnée du coin supérieur droit
        self.temp = 0      # temp: température à afficher
        self.sx = 1        # sx: étirement horizontal
        self.sy = 1        # sy: étirement vertical
        self.tempMax = 50  # tempMax: température maximale affichée
        self.tempMin = -50 # tempMin: température minimale affichée
        self.tempPre = 0   #température précédente
        self.nbGr = 5      # nbGr: nombre de graduations sur l'échelle

    def thermometre (self, font1, x:int=0, y:int=10, temp:int=0, sx:int=1, sy:int=1, tempMax:int=50, tempMin:int=-50, nbGr:int=5):
        self.x = x
        self.y = y
        self.temp = temp
        self.sx = sx
        self.sy = sy
        self.tempMax = tempMax
        self.tempMin = tempMin
        self.tempPrec = temp
        ct = self.ct
 
        self.circle(x+23, y+121, 18*sx, ct, 1 )
        self.circle(x+24, y+0,   11*sx, ct, 1)
        super().vline (x+14, y+0,   108*sy, ct)
        super().vline (x+34, y+0,   108*sy, ct)
        for l in range(6):
            super().hline (x+0,  (4 + ((l+1)*20))*sy,   8*sx, ct)
            super().text(font1, str(int(tempMax - (l * ((tempMax-tempMin)/5)))), (x+37)*sx, ((l+1)*20)*sy, ct)
        super().fill_rect  (x+15, y+1, 18*sx, 20*sy, st7789orig.color565(0,0,0))
        super().fill_rect  (x+15, y+100, 18*sx, 20*sy, st7789orig.color565(0,0,0))
        self.circle(self.x+24, self.y+121, 11*self.sx, self.cm, 0)
        print (" temp = " + str(temp))
        print (" tempMax = " + str(self.tempMax))
        print (" tempMin = " + str(self.tempMin))
        print (" Écart total : " + str(self.tempMax-self.tempMin))
        print (" sx = " + str(self.sx))
        self.temperature (temp)

    def temperature (self, temp):
        if (temp < self.tempPrec):
            super().fill_rect  (self.x+19, self.y,  12*self.sx, 104, st7789orig.color565(0,0,0))
        tempRel = int(((self.tempMax+temp)/(self.tempMax-self.tempMin)) * 104*self.sy)
        if tempRel > 104*self.sy:
            tempRel = 104*self.sy
        super().fill_rect  (self.x+19, self.y+104-tempRel,  12*self.sx, 14+tempRel, self.cm)
        self.tempPrec = temp

    def circle(self, x:int, y:int, r:int, c:int, w:int=1) -> None:
        #To fill the circle, set w = 0
        verif = [999 for i in range(0, 240)]
        for xx in range(r+1):
            yy = int(math.sqrt(abs((r * r) - (xx * xx))))
            verif[yy] = yy
            if w == 0:
                for ww in range(xx):
                    super().pixel(x-ww, y+yy, c)
                    super().pixel(x-ww, y-yy, c)
                    super().pixel(x+ww, y-yy, c)
                    super().pixel(x+ww, y+yy, c)
                    
                    super().pixel(x-yy, y+ww, c)
                    super().pixel(x-yy, y-ww, c)
                    super().pixel(x+yy, y-ww, c)
                    super().pixel(x+yy, y+ww, c)
            else:
                for ww in range(w):
                    for www in range(w):
                        super().pixel(x-xx-ww, y+yy-www, c)
                        super().pixel(x-xx-ww, y-yy-www, c)
                        super().pixel(x+xx-ww, y+yy-www, c)
                        super().pixel(x+xx-ww, y-yy-www, c)
                        
                        super().pixel(x-yy-ww, y+xx-www, c)
                        super().pixel(x-yy-ww, y-xx-www, c)
                        super().pixel(x+yy-ww, y+xx-www, c)
                        super().pixel(x+yy-ww, y-xx-www, c)
            if w == 0:
                q = int(math.sqrt((r/2 * r/2) + (r/2 * r/2)))
                super().fill_rect(int(x-q), int(y-q), 2*q, 2*q, c)

        def horloge(self, t:str="13h45:52", font=font1, x:int=200, y:int=30, r:int=15, c:int=st7789orig.color565(127, 127, 127)) -> None:
            self.circle(x, y, r, c, 3)
            super().line(x+r, y+0, x1+r-3, y1+0, c)
            super().line(x+r, y+1, x1+r-3, y1+1, c)
            super().line(x+r, y+1, x1+r-3, y1-1, c)

            super().line(x-r, y+0, x1-r+3, y1+0, c)
            super().line(x-r, y+1, x1-r+3, y1+1, c)
            super().line(x-r, y+1, x1-r+3, y1-1, c)
            
            super().line(x-0, y-r, x1-0, y1-r+3, c)
            super().line(x+1, y-r, x1+1, y1-r+3, c)
            super().line(x-1, y-r, x1-1, y1-r+3, c)
            
            super().line(x-0, y+r, x1+0, y1+r-3, c)
            super().line(x+1, y+r, x1+1, y1+r-3, c)
            super().line(x-1, y+r, x1-1, y1+r-3, c)
            
            h = int(t[:2])
            m = int(t[4:5])
            #Aiguille minutes
            r = r * 0.80
            posiX = m
            posiY = m
            while (posiX > 15):
                posiX = posiX-15:
            x1 = x + int(r * (15/posiX))
            if m > 30:
                x1 = x - int(r * (15/posiX))
            if m = 0 or m = 30 or m = 60:
                x1 = x
            y1 = y - int(r * (15/posiY))
            if m > 15 and m < 45:
                y1 = y +  int(r * (15/posiY))
            if m = 15 or m = 45:
                y1 = y
            if m = 0 or m = 60:
                y1 = y - r
            if m = 30:
                y1 = y - r
            super().line(x, y, x1, y1, st7789orig.color565(127, 127, 127))
            #Aiguille heures
            r = r * 0.80
            posiX = h
            posiY = h
            while (posiX > 15):
                posiX = posiX-15:
            x1 = x + int(r * (15/posiX))
            if m > 30:
                x1 = x - int(r * (15/posiX))
            if m = 0 or m = 30 or m = 60:
                x1 = x
            y1 = y - int(r * (15/posiY))
            if m > 15 and m < 45:
                y1 = y +  int(r * (15/posiY))
            if m = 15 or m = 45:
                y1 = y
            if m = 0 or m = 60:
                y1 = y - r
            if m = 30:
                y1 = y - r
            super().line(x, y, x1, y1, st7789orig.color565(177, 177, 177))
