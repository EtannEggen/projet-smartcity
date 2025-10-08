import machine
import utime
led = machine.Pin(16,machine.Pin.OUT)
BP = machine.Pin(18,machine.Pin.IN)
compt = 0



def  interuption_BP(Pin)  :
    global compt
    compt += 1
    print(compt)
    
BP.irq(trigger=machine.Pin.IRQ_RISING,handler = interuption_BP)
while True:
    if compt == 1:
        led.value(1)
        utime.sleep_ms(1000)
        led.value(0)
        utime.sleep_ms(1000)
        
        
        
    if compt ==2:
        led.value(1)
        utime.sleep_ms(500)
        led.value(0)
        utime.sleep_ms(500)
        
         
    if compt ==3:
        led.value(0)
        
    if compt>=4:
        compt=1
            
                
   
    
    
    
