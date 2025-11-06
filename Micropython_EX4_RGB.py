from machine import Pin, ADC
from neopixel import NeoPixel
import time, math, utime
import random   # version MicroPython de random

# --- configuration ---
Mic = ADC(1)
led = NeoPixel(Pin(18), 1)  # Pin 18, 1 LED WS2812

ambient = 0
dernier_beat = 0
bpm = 0
one = False
next_ok = 0
dontloop= 0
ON_SEUIL  = ambient + 500   # déclenchement
OFF_SEUIL = ambient + 300   # réarmement (plus bas que ON_SEUIL)
DELTA = 8000          # montée minimale entre deux tours 
last_noise = Mic.read_u16() # point de départ réaliste



# --- fonction couleur aléatoire ---
def random_colors():
    R = random.randrange (1,255)
    G = random.randrange(1,255)
    B = random.randrange(1,255)
    return (R, G, B)
def UpLed():
    led[0] = random_colors()     # applique la couleur sur la LED
    led.write()                  # envoie la donnée à la LED
    
#---filtre de bruit---

ambient = 24000 # fixer en fonxtion du composant et du son ambient
print("Calibrage du filtre")
print(f"valeur ambiente :{ambient}")
# --- boucle principale ---
while True:
    
    now = time.ticks_ms()
    noise = Mic.read_u16() 
    if ( noise < last_noise + DELTA ) and ( noise > last_noise) and (time.ticks_diff(now, dontloop) >= 0):#pas de variation de couleur si le bruit est continue
        dontloop = time.ticks_add(time.ticks_ms(),10)
        
    elif (not one) and (noise > ambient+500) and (noise > last_noise + DELTA ) and time.ticks_diff(now, next_ok) >= 0:# change de couleur quant le son augmente
        UpLed()
        print(noise)
        
        next_ok = time.ticks_add(time.ticks_ms(),100)  # 100 ms anti-rebond
        one = True
        last_noise = noise
    elif  one and (noise < last_noise ):
        one = False   
        
    elif (noise > 8000)and(noise < ambient + 300 ) :# puis que  
        led[0] = (0,0,0)
        led.write()
        last_noise = noise
        

    



    if noise > ambient+200:
        nowbpm = utime.ticks_ms()
        intervalle = utime.ticks_diff(nowbpm, dernier_beat)
        if 250 < intervalle < 1500:  # on élimine les bruits trop rapprochés
            bpm = 60000 / intervalle
            print("BPM:", int(bpm))
        dernier_beat = nowbpm
        utime.sleep_ms(200)  # anti-rebond
#---------------------------------------------------------------------------------------------------------------------------


