#!/usr/bin/python
# -*- coding: utf-8 -*-
from machine import Pin, I2C
import binascii


class ds3231(object):
#            13:45:00 Mon 24 May 2021
#  the register value is the binary-coded decimal (BCD) format
#               sec min hour week day month year
    NowTime = b'\x00\x45\x13\x02\x24\x05\x21'
    #w  = ["Days of weel", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
    #lesMois = ["Months - long","January", "February", "Marsh", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    #lesMs = ["Months - short","Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    w  = ["Jours de semaine", "Dimanche","Lundi","Mardi","Mercredi","Jeudi","Vendredi","Samedi"];
    lesMois = ["Les mois","janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"]
    lesMs = ["Les mois brefs","jan.", "fév.", "mars", "avr.", "mai", "juin", "juil.", "août", "sep.", "oct.", "nov.", "déc."]
    address = 0x68
    start_reg = 0x00
    alarm1_reg = 0x07
    control_reg = 0x0e
    status_reg = 0x0f
    
    def __init__(self,i2c_port,i2c_scl,i2c_sda):
        self.bus = I2C(i2c_port,scl=Pin(i2c_scl),sda=Pin(i2c_sda))

    def set_time(self,new_time):
        #new_time (array) format expected, in a singular binary string  : scmnhrwdmsjryr  (what is "sc mn hr wd ms jr yr" with no space)
        #Format attendu du tableau new_tim, en une chaîne binaire       : scmnhrjsmsjran  (clairement:  "sc mn hr wd ms jr yr" sans espace)
        hour = new_time[0] + new_time[1]
        minute = new_time[3] + new_time[4]
        second = new_time[6] + new_time[7]
        week = "0" + str(self.w.index(new_time.split(",",2)[1])+1)
        year = new_time.split(",",2)[2][2] + new_time.split(",",2)[2][3]
        month = new_time.split(",",2)[2][5] + new_time.split(",",2)[2][6]
        day = new_time.split(",",2)[2][8] + new_time.split(",",2)[2][9]
        now_time = binascii.unhexlify((second + " " + minute + " " + hour + " " + week + " " + day + " " + month + " " + year).replace(' ',''))
        self.bus.writeto_mem(int(self.address),int(self.start_reg),now_time)
    
    def read_time(self):
        t = self.bus.readfrom_mem(int(self.address),int(self.start_reg),7)
        a = t[0]&0x7F  #secondes / second
        b = t[1]&0x7F  #minute / minute
        c = t[2]&0x3F  #heure / hour
        d = t[3]&0x07  #jour de semaine / week
        e = t[4]&0x3F  #jour / day
        f = t[5]&0x1F  #mois / month
        r = ["","","","","","","",""]
        r[0] = int("20%x" %(t[6])) # Année  /Year
        r[1] = int("%02x" %(f)) # Mois  / Month
        r[2] = int("%02x" %(e)) # Jour  / Day
        r[3] = int("%02x" %(d)) # Jour de semaine en chiffre  /  Day of week (num)
        r[4] = int("%02x" %(c)) # heures  / hour
        r[5] = int("%02x" %(b)) # minutes /minut
        r[6] = int("%02x" %(a)) # secondes /seconds
        r[7] = self.w[int(r[3])] # Jour de semaine en lettres / Day of week (txt)
        return r
        
    def sec(self):
        lu = self.read_time()
        return lu[6]
    
    def minute(self):
        lu = self.read_time()
        return lu[5]
    
    def hour(self):
        lu = self.read_time()
        return lu[4]
    
    def week(self):
        lu = self.read_time()
        return lu[3]
    
    def day(self):
        lu = self.read_time()
        return lu[2]
    
    def month(self):
        lu = self.read_time()
        return lu[1]
    
    def year(self):
        lu = self.read_time()
        return lu[0]
        
    def laDate(self):
        lu = self.read_time()
        return (str(lu[0]) + "/" + str(lu[1]) + "/" + str(lu[2]))

    def laDateTexte(self):
        lu = self.read_time()
        #return (lu[7] + ", the " + self.lesMois[lu[2]] + " " + str(int(lu[4])) + "th " + str(lu[0]))
        return (lu[7] + " " + str(int(lu[4])) + " " + self.lesMois[lu[2]] + " " + str(lu[0]))
        
    def laDateTexteS(self):
        lu = self.read_time()
        #return (lu[7][:3] + "., the " + self.lesMs[lu[2]] + " " + str(int(lu[4])) + "th " + str(lu[0]))
        return (lu[7][:3] + ". " + str(int(lu[4])) + " " + self.lesMs[lu[2]] + " " + str(lu[0]))
        
    def lHeure(self):
        lu = self.read_time()
        return (str(lu[4]) + "h" + str(lu[5]) + ":" + str(lu[6]))
    
    def day_name(self):
        lu = self.read_time()
        return (lu[7] )

    def month_name(self):
        lu = self.read_time()
        return (self.lesMois[lu[2]])
    
    def month_nameS(self):
        lu = self.read_time()
        return (self.lesMs[lu[2]])
    
    def set_alarm_time(self,alarm_time):
        #    init the alarm pin
        self.alarm_pin = Pin(ALARM_PIN,Pin.IN,Pin.PULL_UP)
        #    set alarm irq
        self.alarm_pin.irq(lambda pin: print("alarm1 time is up"), Pin.IRQ_FALLING)
        #    enable the alarm1 reg
        self.bus.writeto_mem(int(self.address),int(self.control_reg),b'\x05')
        #    convert to the BCD format
        hour = alarm_time[0] + alarm_time[1]
        minute = alarm_time[3] + alarm_time[4]
        second = alarm_time[6] + alarm_time[7]
        date = alarm_time.split(",",2)[2][8] + alarm_time.split(",",2)[2][9]
        now_time = binascii.unhexlify((second + " " + minute + " " + hour +  " " + date).replace(' ',''))
        #    write alarm time to alarm1 reg
        self.bus.writeto_mem(int(self.address),int(self.alarm1_reg),now_time)
        
    def temperature(self):
        t = self.bus.readfrom_mem(int(self.address),int(self.start_reg),19)
        whole = t[17]&0xFF        
        decimal = ((t[18]& 192)/64) *0.25
        temp = whole + decimal
        if (t[17]&0xFF) > 127:
            temp = temp * -1
        return temp
