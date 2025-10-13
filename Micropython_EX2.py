from machine import Pin, PWM, ADC
from utime import sleep


buzzer = PWM(Pin(27))
pot = ADC(0)
led = machine.Pin(16,machine.Pin.OUT)
BP = machine.Pin(18,machine.Pin.IN)

compt = 0


#compteur d'impultion du bouton
def  interuption_BP(Pin)  :
    global compt
    compt += 1
    if compt > 2:
        compt = 0
    print(compt)
    
BP.irq(trigger=machine.Pin.IRQ_RISING,handler = interuption_BP)
def buzzer_vol():
   
    return pot.read_u16()

def play_note(freq, duration_s):
        led.value(1)# LED ON pendant la note
        buzzer.freq(freq)
        buzzer.duty_u16(buzzer_vol())
        sleep(duration_s)
        buzzer.duty_u16(0)
        led.value(0) 
        sleep(0.03)# coupe le son
                   # LED OFF après la note
#definir les notes
def DO(t):
    play_note(1046, t)
    
def RE(t):
    play_note(1175, t)
    
def MI(t):
    play_note(1318, t)
    
def FA(t):
    play_note(1397, t)
    
def SO(t):
    play_note(1568, t)
    
def LA(t):
    play_note(1760, t)
    
def SI(t):
    play_note(1967, t)

#jouer les notes
while True:
        
    if compt == 1:
        (DO(0.25),DO(0.25),SO(0.25),SO(0.25),LA(0.25),LA(0.25),
        SO(0.5),FA(0.25),FA(0.25),MI(0.25),MI(0.25),RE(0.25),
        RE(0.25),DO(0.5))
    elif compt == 2:
        MI(0.4); FA(0.4); SO(0.6); LA(0.6)
        LA(0.4); SO(0.4); FA(0.6); MI(0.6)
        RE(0.4); RE(0.4); DO(0.8)
        RE(0.4); MI(0.4); FA(0.6); FA(0.4); MI(0.8)

        
        MI(0.4); FA(0.4); SO(0.6); LA(0.6)
        LA(0.4); SO(0.4); FA(0.6); MI(0.6)
        RE(0.4); MI(0.4); FA(0.6); MI(0.4)
        RE(0.4); DO(0.8)

        
        MI(0.4); FA(0.4); SO(0.6); LA(0.6)
        SO(0.4); FA(0.4); MI(0.6); RE(0.6)
        DO(1.0)
        
       
            

    

    
         

        
       
            
        

    

    