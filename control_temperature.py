

from lcd1602 import LCD1602
from dht20 import DHT20
from machine import I2C, Pin, ADC, PWM
import time

i2c = I2C(1, scl=Pin(7), sda=Pin(6), freq=100_000)
i2c0 = I2C(0, scl=Pin(9), sda=Pin(8), freq=100_000)
d = LCD1602(i2c, 2, 16)
dht = DHT20(i2c0)
pot = ADC(0)
led = machine.Pin(16,machine.Pin.OUT)
buzzer = PWM(Pin(27))



def pot_temp(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
def POTVAL():
    val_pot = pot.read_u16()
    return pot_temp(val_pot, 144, 65535, 15, 35)
      

timeview = time.ticks_ms() 
timeled = time.ticks_ms() # moment initial
timealarme = time.ticks_ms()
timedefil = time.ticks_ms()
state = 0
clignot_LED = 1000
i = 0

while True:
    max =(dht.dht20_temperature() - POTVAL())
    now = time.ticks_ms() #"temps actuel
    if max < 3:
        buzzer.duty_u16(0)
        d.setCursor(0, 0); d.print("set:"  + str(round((POTVAL()),1)))
        if time.ticks_diff(now, timeview) >= 1000:  # 1 s
            temp = dht.dht20_temperature() # lecture du capteur
            timeview = now # met à jour le dernier instant
            d.clear()
            d.setCursor(0, 0); d.print("set:"  + str(round((POTVAL()),1)))
            d.setCursor(0, 1); d.print("Ambient:" + str(round(temp, 1)))
    
    
    if POTVAL() < dht.dht20_temperature()  : 
        if max > 3 :
            
            buzzer.duty_u16(2000)
            buzzer.freq(1000)
            d.clear()
            d.setCursor(0, 1); d.print ("overflow:" +str(round(max,1)))
            if time.ticks_diff(now, timealarme) >= 500:
                #fais deffiler le mot
                d.setCursor (i-8, 0); d.print("ALARME:")
                i -= 1
                timealarme = now
                if i < -6 :
                    i = 23
   
        if time.ticks_diff(now,timeled) >= 0:#clognotement de la led
            state= not state
            led.value(state)
            print (state)
            if max < 3: #clignotement normal
                timeled = time.ticks_add(timeled,clignot_LED)
                
            else:#clignotement acceleré
                timeled = time.ticks_add(timeled,clignot_LED - int((max)) * 100) # acceleration du clignotement plus l'ecart est grand
                 
    else:
        led.value(0)   

        


    


