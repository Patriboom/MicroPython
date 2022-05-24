#Read/Write a DS3231-RTC via I2C
#and write output to terminal
#Autor:   Joern Weise
#License: GNU GPl 3.0
#Created: 03. Nov 2021
#Update: 11. Nov 2021

#https://www.az-delivery.de/en/blogs/azdelivery-blog-fur-arduino-und-raspberry-pi/raspberry-pi-pico-als-analoge-uhr
from machine import Pin, I2C
import binascii
import DS3231 as HorlogeLib

NowTime = b'\x00\x45\x13\x02\x24\x05\x21'
address = 0x68
start_reg = 0x00
alarm1_reg = 0x07
control_reg = 0x0e
status_reg = 0x0f

arrayDay = ["Jour de semaine", "Dimanche", "Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi"]
Horloge = HorlogeLib.ds3231(0,5,4)             #Initialisastion de l'horloge

#Création de la constante de date actuelle
#.............................  sc mn hr wd ms jr an
now_time = binascii.unhexlify(("54 32 07 03 05 23 22").replace(' ',''))
Horloge.bus.writeto_mem(int(address),int(start_reg),now_time)


lastSecond = -1
while True:                   #Boucle de test infinie:  afficher l'heure
    t = Horloge.read_time()   #Obtenir l'heure actuelle
    if lastSecond != t[6]:    #Restreindre l'affichage aux seuls moments où les secondes ont changé
        print ("Heure actuelle : " + str(t))
        print ("Année = " + str(Horloge.year()))
        print('-----------------')
        print('Date: ' + f'{t[2]:02d}' + '/' + f'{t[1]:02d}' + '/' + f'{t[0]:02d}')
        print('Jour: ' + arrayDay[t[3]])
        print('Heure: ' + f'{t[4]:02d}'+':'+f'{t[5]:02d}'+':'+f'{t[6]:02d}')
        lastSecond = int(t[6])
