#bibliothèques
from machine import Pin, PWM,
import utime , time
import network
import ntptime
import machine
#--- gestion des E/S ---
servo = PWM(Pin(20))
servo.freq(100) 
BP = machine.Pin(18,machine.Pin.IN)


# --- Paramètres Wi-Fi ---
nom_Wifi = 'Studentstation'       # ← remplace par ton nom de réseau
PASSWORD = 'Studentst@tion'  # ← remplace par ton mot de passe

wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(nom_Wifi, PASSWORD)
print("Connexion Wi-Fi en cours...")
while not wifi.isconnected():
    utime.sleep(0.5)
    print(".", end="")

print("\n✅ Connecté au Wi-Fi !")
print("Adresse IP :", wifi.ifconfig()[0])


# --- Synchronisation NTP ---
try:
    print("Synchronisation avec le serveur NTP...")
    ntptime.settime()
    print("✅ Heure synchronisée avec Internet !")
except:
    print("❌ Impossible de synchroniser l'heure (vérifie la connexion Internet)")

#--- Variables globales ---
last_time_check = utime.ticks_ms()  # pour la mise à jour chaque seconde
TIME_OFFSET = 0  # décalage horaire en heures
is_12h = False  # mode 12h ou 24h
last_bp_ms = 0  # pour la détection du double-clic


# Fonction pour gérer le changement de décalage horaire
def set_horraire():
    global last_bp_ms, TIME_OFFSET
    TIME_OFFSET = (TIME_OFFSET + 1) % 24  # cycle entre 0 et 23 heures
    last_bp_ms = 0

# Convertit l'heure, minute, seconde en angle pour le servo
def convert_temps_to_angle(heure, minute, seconde):
    global is_12h
    if is_12h:
        rotation_seconde = 86400  # 24 heures en secondes
    else:
        rotation_seconde = 43200 # 12 heures en secondes
    total_secondes = heure * 3600 + minute * 60 + seconde
    # Ajustement pour le mode 12/24 heures
    if total_secondes >= rotation_seconde and not is_12h:
        total_secondes -= rotation_seconde  # soustraire 12 heures en secondes

    angle = (total_secondes / rotation_seconde) * 180  # 43200 secondes dans 12 heures
    duty = int(15800 - (angle / 180) * (15800 - 3800))
    return duty

# Gestion du mode 12h/24h via double-clic
def mode_12_24():
    global last_bp_ms, is_12h,TIME_OFFSET
    now = utime.ticks_ms()
    
    # anti-rebond
    if utime.ticks_diff(now, last_bp_ms) < 100:
        return
    
    # si le précédent appui est dans la fenêtre de double clic -> toggle
    if last_bp_ms != 0 and utime.ticks_diff(now, last_bp_ms) <= 400:
        is_12h = not is_12h
        
        # reset pour éviter triple-clic compté
        last_bp_ms = 0

        # affichage léger (éviter prints lourds en IRQ mais ok pour debug court)
        print("Mode basculé :", "24h" if is_12h else "12h")
    else:
        # mémorise le temps du premier appui
        last_bp_ms = now
        
# appliquer l'offset horaire (gestion du rollover 24h)
def horaire(t):
    heure = (t[3] + TIME_OFFSET + 1) % 24  # ajuster l'heure locale(+1 pour heure locale)
    minute = t[4]
    seconde = t[5]
    return heure, minute, seconde

# --- Fonction d'interruption pour le bouton-poussoir ---
def interruption_BP(pin)  :
   mode_12_24()

# --- Interruption pour le bouton-poussoir ---
BP.irq(trigger=machine.Pin.IRQ_RISING, handler=interruption_BP)



# --- Lecture de l'heure locale ---
while True:
    now = utime.ticks_ms()
    #  vérifier le double-clic pour eviter l'ajout d'heure en changeant de mode 12/24h
    if last_bp_ms != 0 and utime.ticks_diff(now, last_bp_ms) > 400:
        set_horraire()

    # mise à jour de l'heure chaque seconde
    if utime.ticks_diff(utime.ticks_ms(), last_time_check) >= 1000:# mise à jour chaque seconde
        last_time_check = utime.ticks_ms()
        t = utime.localtime()  # (année, mois, jour, heure[3], minute[4], seconde[5], jour_semaine, jour_année) temps UTC (US)
        heure, minute, seconde = horaire(t)
        
        # Met à jour la position du servo
        duty = convert_temps_to_angle(heure, minute, seconde)
        servo.duty_u16(duty) # 3800 à 15 800
        mode_str = "12h" if is_12h else "24h"
        print("Heure actuelle : {:02d}:{:02d}:{:02d}: +{}h".format(heure, minute, seconde, TIME_OFFSET))