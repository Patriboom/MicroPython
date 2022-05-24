from sys import platform
import max7219
from machine import Pin, SPI, freq
import machine
from time import sleep
import gc
from print_error import print_error  # Optional print of error codes
# Import all implemented classes
from nec import NEC_8, NEC_16
from sony import SONY_12, SONY_15, SONY_20
from philips import RC5_IR, RC6_M0
from mce import MCE

# Define pin according to platform
p = Pin(15, Pin.IN)
valeurLue = "Rien"

class matrix():
    bright = 9
    invert = False
    LECTURE = ""
    VISIBLE = "Bienvenue en l`eglise de St-Joseph de Chisasibi"
    LONG = len(VISIBLE)
    MAX7219_NUM = 3
    MAX7219_INVERT = invert
    MAX7219_SCROLL_DELAY = 0.15

    def __init__(self):
        cs_pin = 5
        spi = SPI(0, baudrate=10000000, polarity=0, phase=0)
        self.display = max7219.Matrix8x8(spi, Pin(5), 4)
        self.display.brightness(self.bright)
    
    def text_scroll(self):
        p = self.MAX7219_NUM * 8
        for x in range(self.MAX7219_NUM * 8, self.LONG * -8 - 1, -1):
            if x < (self.LONG * -8 - 1):
                x = self.MAX7219_NUM * 8
            if self.MAX7219_SCROLL_DELAY == 0.015:
                p = 0
            else:
                p = x
            self.display.fill(self.MAX7219_INVERT)
            self.display.text(self.VISIBLE, p, 0, not self.MAX7219_INVERT)
            self.display.show()
            sleep(self.MAX7219_SCROLL_DELAY)
    def ir_rcv(self, data):
        if data == 'EQ':
            data = ""
            self.LECTURE = ""
            self.VISIBLE = "administration@diocese-amos.org"
            self.LONG = len(self.VISIBLE)
            self.MAX7219_SCROLL_DELAY = 0.077
            self.bright = 9
            self.display.brightness(self.bright)
            self.MAX7219_NUM = 1
        if data == "FIN":
            data = ""
            self.VISIBLE = self.LECTURE
            self.LONG = len(self.VISIBLE)
            self.LECTURE = ""
            if (len(self.VISIBLE) > 4):
                self.MAX7219_SCROLL_DELAY = 0.15
            else :
                self.MAX7219_SCROLL_DELAY = 0.015
            self.bright = 9
            self.MAX7219_NUM = 1
            self.display.brightness(self.bright)
        LesData = data.split("FIN")
        data = LesData[0]
        if data == "Pause":                        #Touche "Pause"
            self.LECTURE = ""
            if self.MAX7219_SCROLL_DELAY <= 0.015:
                self.MAX7219_SCROLL_DELAY = 0.15
            else:
                self.MAX7219_SCROLL_DELAY = 0.015
            data = ""
        if data == "+":                             #Touche "+"
            self.LECTURE = ""
            self.MAX7219_SCROLL_DELAY = self.MAX7219_SCROLL_DELAY * 0.8
        if data == "-":                             #Touche "-"
            self.LECTURE = ""
            self.MAX7219_SCROLL_DELAY = self.MAX7219_SCROLL_DELAY * 1.25
        if data == "OFF":
            if self.bright == 0:
                self.bright = 9
            else:
                self.bright = 0
            self.display.brightness(self.bright)
            machine.reset()
        if data == "USB":                             #Touche "USB"
            if self.invert == True:
                self.invert = False
            else:
                self.invert = True
            self.MAX7219_INVERT = self.invert
        else:
            self.LECTURE = self.LECTURE + data
        data = ""

# User callback
def cb(data, addr, ctrl):
    if data < 0:  # NEC protocol sends repeat codes.
        pass
    else:
        val = str('{:02x}'.format(data))
        switch={
            '16':'0',
            '0c':'1',
            '18':'2',
            '5e':'3',
            '08':'4',
            '1c':'5',
            '5a':'6',
            '42':'7',
            '52':'8',
            '4a':'9',
            '19':'FIN',        #bouton 'Flèches emmêlées' : faire afficher les caractères précédemment appuyés
            '0d':'USB',        #bouton 'USB' pour alterner inverse-vidéo et vidéo-régulier
            '07':'EQ',         #bouton 'EQ'
            '15':'-',          #bouton - décélère l'affichage défilant
            '09':'+',          #bouton + accélère l'affichage défilant
            '44':'Pause',      #bouton 'Pause'  : alterne entre affichage fixe et affichage défilant
            '40':'Debout',     #bouton 'Avance rapide' : Incite les gens à se lever
            '43':'A genoux',   #bouton 'Recule rapide' : Incite les gens à s'agenouiller
            '45':'OFF',        #bouton 'ON/OFF' : Provoque une réinitialisation
            '46':'F: Foule',   #boutun 'Mode'   : Principalement au Vend Saint : inciter la foule à dire sa part durant la lecture de la Passion
            '47':'_'           #bouton 'MUTE'   : Ligne basse qui passe, illusion d'écran noir
            }
        led.ir_rcv(switch.get(val, "Rien"))

#Objects definitions
led = matrix()
classes = (NEC_8, NEC_16, SONY_12, SONY_15, SONY_20, RC5_IR, RC6_M0, MCE)
ir = classes[0](p, cb)  # Instantiate receiver
ir.error_function(print_error)  # Show debug information

try:
    while True:
        gc.collect()
        led.text_scroll()
        if valeurLue != "Rien" and valeurLue != None:
            print(valeurLue)
except KeyboardInterrupt:
    ir.close()
    print("Fin du test")