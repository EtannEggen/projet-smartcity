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
# --- variables BPM / logging ---
LOG_FILENAME = "bpm_log.txt"    # fichier où sont écrites les moyennes par minute
bpm_values = []                   # liste des BPM détectés pendant la minute
minute_start = utime.ticks_ms()   # début de la fenêtre d'une minute



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

ambient = 22000 # fixer en fonxtion du composant et du son ambient
print("Calibrage du filtre")
print(f"valeur ambiente :{ambient}")

# --- fonction pour écrire la moyenne des BPM par minute ---
def log_minute_average(bpm_list, filename, ts_ms):
    """Ecrit dans le fichier `filename` la moyenne des BPM présents dans bpm_list.
    Format écriture: <timestamp_s>;<avg_bpm>;<count>\n
    ts_ms : timestamp en ms (ticks_ms) utilisé pour repérer la minute.
    """
    try:
        ts_s = ts_ms // 1000
        if bpm_list:
            avg = sum(bpm_list) / len(bpm_list)
            line = "{};{:.1f};{}\n".format(ts_s, avg, len(bpm_list))
        else:
            line = "{};NoBeats;0\n".format(ts_s)
        # ouvrir, écrire, forcer flush et fermer pour minimiser les pertes
        f = open(filename, "a")
        f.write(line)
        f.flush()
        f.close()
        print("Log minute ->", filename, ":", line.strip())
    except Exception as e:
        print("Erreur écriture fichier BPM:", e)
# --- boucle principale ---
while True:
    
    now = time.ticks_ms()
    noise = Mic.read_u16() 
    if ( noise < last_noise + DELTA ) and ( noise > last_noise) and (time.ticks_diff(now, dontloop) >= 0):#pas de variation de couleur si le bruit est continue
        dontloop = time.ticks_add(time.ticks_ms(),10)
        
    elif (not one) and (noise > ambient+500) and (noise > last_noise + DELTA ) and time.ticks_diff(now, next_ok) >= 0:# change de couleur quant le son augmente
        UpLed()
        print(noise)
        
        next_ok = time.ticks_add(time.ticks_ms(),100)  # 100 ms anti-rebond et empeche d'aller trop vite
        one = True
        last_noise = noise
    elif  one and (noise < last_noise ):
        one = False   
        
    elif (noise > 8000)and(noise < ambient + 300 ) :# eteindre la led quant le son redevient bas 
        led[0] = (0,0,0)
        led.write()
        last_noise = noise
        

#--- détection des battements et calcul du BPM ---
    if noise > ambient+200:
        nowbpm = utime.ticks_ms()
        intervalle = utime.ticks_diff(nowbpm, dernier_beat)
        if 250 < intervalle < 1500:  # on élimine les bruits trop rapprochés
            bpm = 60000 / intervalle
            print("BPM:", int(bpm))
            # enregistrer le BPM détecté pour la moyenne par minute
            try:
                bpm_values.append(int(bpm))
            except Exception:
                # en cas d'erreur (par ex. bpm_values non défini), on réinitialise proprement
                bpm_values.clear()
                bpm_values.append(int(bpm))
            # si une minute complète s'est écoulée, calculer la moyenne et écrire dans le fichier
            if utime.ticks_diff(nowbpm, minute_start) >= 60000:
                log_minute_average(bpm_values, LOG_FILENAME, nowbpm)
                bpm_values.clear()
                # redéfinir le début de la fenêtre à maintenant
                minute_start = nowbpm
        dernier_beat = nowbpm
        utime.sleep_ms(200)  # anti-rebond
#---------------------------------------------------------------------------------------------------------------------------


