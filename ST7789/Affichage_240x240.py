#Merci à https://forums.raspberrypi.com/viewtopic.php?t=315927&hilit=st7789+pico
from display import *
from machine import SPI, Pin
from time import sleep

led_pin = Pin(25, Pin.OUT)

#_> Init Display
d = meteo(
    spi     = SPI(0, sck=Pin(18, Pin.OUT), mosi=Pin(19, Pin.OUT)),
    bl      = Pin(16, Pin.OUT),
    dc      = Pin(17, Pin.OUT),
    rst     = Pin(20, Pin.OUT),
    baud    = 62_500_000,
    rot     = 0,
    width   = 240,
    height  = 240)

RED   = d.rgb565(0xFF0000)
GREEN = d.rgb565(0x00FF00)
BLUE  = d.rgb565(0x0000FF)
NOIR  = d.rgb565(0x000000)
    
d.clear()

d.vline(RED  , 120, 0, 120)
d.hline(GREEN, 0, 120, 120)
d.rect (BLUE , 110, 110, 20, 20)
sleep(2)
d.rect (NOIR , 110, 110, 20, 20)
d.vline(RED  , 120, 0, 120)
d.hline(GREEN, 0, 120, 120)
d.rect (BLUE , 0, 110, 20, 20)

d.circle(d.rgb565(0xCC00FF), 145, 50, 45, 0)

sleep(2)
d.clear()
for x in range(1, 111):
    #d.clear()
    d.rect (NOIR , (x-1), 110, 20, 20)
    d.rect (BLUE , x, 110, 20, 20)
    d.hline(d.rgb565(0xFFFF00), 0, 110, x)
    sleep(0.01)

sleep(2)
d.clear()
d.backlight(125)
for y in range(110, 0, -1):
    d.rect (NOIR , 110, (y+1), 20, 20)
    d.rect (BLUE , 110, y, 20, 20)
    d.vline(d.rgb565(0xFFFF00), 110, y, (111-y))
    sleep(0.02)

sleep(2)
d.clear()
d.backlight(200)
d.rect (NOIR , 110, (y), 20, 20)
d.vline(d.rgb565(0xCC00FF), 110, y+1, (111-y))

d.line(RED, 5, 5, 219, 222, 13)
d.circle(d.rgb565(0xCC00FF), 120, 170, 45, 3)

sleep(2)
d.clear()
d.backlight(255)
d.thermometre(15, 25, 42)
d.temperature(12)

for x in range(0, 5):
    led_pin(1)
    sleep(0.2)
    led_pin(0)
    d.temperature(x*9)
    sleep(0.7)

