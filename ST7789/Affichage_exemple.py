"""
Raspberry Pi Pico/MicroPython exercise
240x240 ST7789 SPI LCD
using MicroPython library:
https://github.com/russhughes/st7789py_mpy
Le code ci-bas vient de https://laptrinhx.com/news/raspberry-pi-pico-micropython-st7789-spi-ips-lcd-6xjB3MD/#
"""

import uos
import machine
from machine import Pin
import st7789 as st7789orig
from display_meteo import *
from fonts import vga2_8x8 as font1
from fonts import vga1_16x16 as font3
from fonts import vga1_16x32 as font2
import random
from time import sleep

spi1_sck=18
spi1_mosi=19
spi1_miso=21 #not use
st7789_res = 20
st7789_dc = 17
st7789_bl = 16
disp_width = 240
disp_height = 240
CENTER_Y = int(disp_width/2)
CENTER_X = int(disp_height/2)
led_pin = Pin(25, Pin.OUT)


#st7789_bl(1)
print ("--------  Infos UOS ------------")
print(uos.uname())
spi1 = machine.SPI(0, sck=Pin(18, Pin.OUT), mosi=Pin(19, Pin.OUT), baudrate=62_500_000, polarity=1)
print ("--------  À propos de SPI ------------")
print(spi1)
print ("--------  Définition de l`objet display ------------")
#display = st7789.ST7789(spi1, disp_width, disp_width,
# reset=machine.Pin(st7789_res, machine.Pin.OUT),
# dc=machine.Pin(st7789_dc, machine.Pin.OUT),
# backlight=machine.Pin(st7789_bl, machine.Pin.OUT),
# xstart=0, ystart=0, rotation=0)

display = meteo(spi1, disp_width, disp_width,
 reset=machine.Pin(st7789_res, machine.Pin.OUT),
 dc=machine.Pin(st7789_dc, machine.Pin.OUT),
 backlight=machine.Pin(st7789_bl, machine.Pin.OUT),
 xstart=0, ystart=0, rotation=0)


print ("Premiers graphiques: un thermomètre et autre détails")
display.thermometre(font1, 15, 25, 42)

for x in range(0, 5):
    led_pin(1)
    sleep(0.2)
    led_pin(0)
    display.temperature(x*9)
    sleep(0.7)

display.temperature(-25)

sleep(3)
print ("---- Emplir l`écran de rouge-----")
for r in range(0, 255, 25):
    display.fill(st7789orig.color565(r, 0, 0))
#    sleep(0.1)
 
r_width = disp_width-20
r_height = disp_height-20
print ("---- Emplir un rectangle-----")
for g in range(0, 255, 30):
    display.fill_rect(10, 10, r_width, r_height, st7789orig.color565(0, g, 0))
#    sleep(0.05)
 
r_width = disp_width-40
r_height = disp_height-40
print("----Emplir un rectangle bleu----")
for b in range(0, 255, 25):
    display.fill_rect(20, 20, r_width, r_height, st7789orig.color565(0, 0, b))

sleep(1)
print ("----Éteindre progressivement ---")
for i in range(255, 0, -21):
    display.fill(st7789orig.color565(i, i, i))

print ("Écran noir")
display.fill(st7789orig.color565(0, 0, 0))
print ("Textes")
display.text(font2, "Hello!", 10, 10)
display.text(font2, "RPi Pico", 10, 40)
display.text(font2, "MicroPython", 10, 70)
display.text(font1, "ST7789 SPI 240*240 IPS", 10, 100)
display.text(font1, "https://github.com/", 10, 110)
display.text(font1, "russhughes/st7789py_mpy", 10, 120)

print ("Des pixels aléatoires")
for i in range(1000):
    display.pixel(random.randint(0, disp_width),
    random.randint(0, disp_height),
    st7789orig.color565(random.getrandbits(8),random.getrandbits(8),random.getrandbits(8)))

display.fill(st7789orig.color565(0, 0, 0))

print ("---- Dessinons des cerlces----")
display.circle(CENTER_X, CENTER_Y, 125, st7789orig.color565(155, 0, 255), 1)
display.circle(CENTER_X, CENTER_Y, 100, st7789orig.color565(255, 0, 155), 1)
display.circle(CENTER_X, CENTER_Y, 75,  st7789orig.color565(255, 0, 0), 1)
display.circle(CENTER_X, CENTER_Y, 55,  st7789orig.color565(255, 175, 0), 1)
display.circle(CENTER_X, CENTER_Y, 15,  st7789orig.color565(255, 255, 0), 0)
sleep(3)

print ("Noircir l`écran puis rallumer progressivement - progression rapide")
display.fill(st7789orig.color565(0, 0, 0))
for i in range(0, 255, 21):
    display.fill(st7789orig.color565(i, i, i))

for i in range(255, 0, -21):
    display.fill(st7789orig.color565(i, i, i))

print ("Textes finaux")
display.text(font2, "Baboom!", 10, 10, st7789orig.color565(255, 255, 255), st7789orig.color565(0, 140, 0))
display.text(font2, "Fini", 10, 50, st7789orig.color565(175, 0, 255))
display.text(font1, "Petite police", 110, 220)
display.thermometre(font1, CENTER_X, 25, 12)

sleep(3)
print ("Ecran noir")
display.fill(st7789orig.color565(0, 0, 0))
sleep(3)
print ("Éteignons l`arrière-plan")
display.backlight.value(0)
print("- Tout éteint, tout fini.-")