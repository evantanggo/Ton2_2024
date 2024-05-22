#Praxis Problem 4 Gruppe 3
#Tom Butenschön
#


import numpy as np
import scipy
import matplotlib.pyplot as plt
from scipy.io.wavfile import read
from scipy.io.wavfile import write
import sounddevice as sd

Eingang = 'voice.wav'                 #Sprachsignal "voice.wav"und Musiksignal "drop.wav" Sinus "Sine_100Hz.wav"

## Zentrale Schalter
wahl_dynamik = 1  # wenn wahl_dynamik = 1: dynamische Kennlinie, wenn 0: statische Kennlinie
wahl_funktion = 'Komp'  # Wahl:'Lim': Limiter, 'Komp': Kompressor

####################################
# Einlesen Testsignal
Signal = Eingang
Fs, x = read(Signal)

#wenn Eingangssignal 2 Kanäle hat, nimm den ersten (links)
if x[1].size == 2:
    x = x[:,0]

delta_t = 1 / Fs            #Zeitabstand zwischen 2 Werte im Array
samples = x.size            #Zahl der Samples des Arrays
dauer_s = samples / Fs      #Dauer in Sekunden
deltat = 1. / (Fs)          # Zeit-Schritt, float
t = np.arange(x.size) / float(Fs)

# umwandeln in float und normieren
x = np.array(x, dtype=np.float64)
x = x / np.max(np.abs(x))  # Normierung

### Kompressor-Parameter festlegen und Umrechnen in Abtastwerte
tAT = 0.1  # Attack-Time = 100µs                 üblich 50µs - 50ms             <-- selbst waehlen
tRT = 1  # Release-Time = 1s                              üblich 10ms - 3s

tAT_i = tAT * Fs
tRT_i = tRT * Fs

# smoothing detector filter:
faktor = np.log10(9)
a_R = np.e ** (-faktor / (tAT_i))
a_T = np.e ** (-faktor / (tRT_i))

## x_ref = np.abs(np.max(x))  #Referenzwert für Pegel
x_ref = 1       #Weil x schon norminiert ist --> max(abs(x)) = 1
L_thresh = -6  # Threshold = -6dB
u_thresh = 10 ** (L_thresh / 20) * x_ref  #Threshold in Proportion/Wert (Proportion zu maximale Wert des Arrays = 1)


R = 8  # Ratio in dB                             <-- waehlen, 20 sehr hoch, stark komprimiert
if R == 0: R = 0.1
L_M = 0  # Make up-Gain in dB

#########################################################################################################
#System A Clipping
#########################################################################################################
#clipping Funktion aus numpy (Signal, unterer Grenzwert, oberer Grenzwert, bearbeitetes Signal)
output_clip = np.zeros(samples)
#30% weniger als Beispiel
C = 0.7         #laut Aufgabenstellung fester Wert C (frei wählbar), Faktor der die Ampitude verändert

np.clip(x, -C, C, output_clip)

########################################################################################################
#System B
#########################################################################################################
## Kompression:
PegelMin = -95  # Pegelgrenze nach unten in dB

# Eingangssingal als Pegel:
Lx = np.zeros(samples)
Lx[1:] = 20 * np.log10(np.abs(x[1:]) / x_ref)
Lx[0] = Lx[1]  # damit nicht log(0)

# Begrenzung des minimalen Pegels (mathematisch erforderlich)
for i in range(samples):
    if Lx[i] < PegelMin:
        Lx[i] = PegelMin

# Vorbereitung der arrays:
Lx_c = np.zeros(samples)  # Pegel(x) nach statischer Kompressor-Kennlinie
Lg_c = np.zeros(samples)  # Pegel(gain) statisch (um wieviel wurde Lx gedämpft)
Lg_s = np.zeros(samples)  # Pegel(gain) dynamisch (smoothed, mit t_attack und t_release)
Lg_M = np.zeros(samples)  # Pegel(gain) dynamisch (smoothed, mit t_attack und t_release) mit Make up gain
g_a = np.zeros(samples)  # linearer gain dynamisch (smoothed, mit t_attack und t_release)

# Berechnung der momentanen Verstärkung/Dämpfung
## Limiter:

for i in range(samples):
    if wahl_funktion == 'Lim':  ## Limiter
        if Lx[i] >= L_thresh:
            Lx_c[i] = L_thresh          #ersetzt statisch zu hohe /gleich hohe Werte mit dem Treshold
        else:
            Lx_c[i] = Lx[i]             # übernimmt den aktuellen wert in neuen Array
    else:  # Kompressor
        if Lx[i] > L_thresh:
            Lx_c[i] = L_thresh + ((Lx[i] - L_thresh) / R )    #bei Überschreitung neuer Wert = Threshold + (Momentanwert - Treshold) geteilt durch Ratio
        else:
            Lx_c[i] = Lx[i]

    Lg_c[i] = Lx_c[i] - Lx[i]  # Dämpfung von Lx zum Zeitpunkt i

    #  dynamische Kennlinie
    Lg_s[0] = 0.0  # 20*np.log10(x[0]/x_ref) #!!! Startwert für dynamische Dämpfung
    if wahl_dynamik == 1:
        if i > 0:
            if Lg_c[i] > Lg_s[i - 1]:  # Release
                Lg_s[i] = a_T * Lg_s[i - 1] + (1 - a_T) * Lg_c[i]
            else:  # Attack
                Lg_s[i] = a_R * Lg_s[i - 1] + (1 - a_R) * Lg_c[i]
    else:
        Lg_s[i] = Lx_c[i]

# Anwenden der momentanen Verstärkung/Dämpfung
if wahl_dynamik == 1:       #dynamisch
    Lg_M = Lg_s + L_M  #L_M = 0

    g_a = 10 ** (Lg_M / 20)  # lineare Verstärkung, zeitabhängig
    y_a = x * g_a  # Ausgangssignal; hier ist das Vorzeichen im x vorhanden
else:                       #statisch
    g_mu = 10 ** (L_M / 20)  # verstärkung ergibt sich aus makeup-gain
    y_a = 10 ** (Lx_c / 20) * x_ref * g_mu  # y ist geclippter Eingang

    for i in range(samples):  # Vorzeichen ist verloren durch log, daher hinzufügen
        if x[i] < 0:
            y_a[i] = -y_a[i]

y_a = y_a / x_ref  # normieren, zur grafischen Darstellung

#####################################################################################################
#neue Wave Dateien erzeugen aus PP2
#######################################################################################################

links = output_clip
rechts = output_clip
stereo = np.vstack((links,rechts)).transpose()
#write("PP4_System_A.wav", Fs, stereo)
print("Es wird die Datei aus System A abgespielt.")
#sd.play(1 * stereo, Fs)  # Array als Sound abspielen       # #entfernen, wenn es abgespielt werde soll
#sd.wait()  # warten bis Wiedergabe beendet                 # #entfernen, wenn es abgespielt werde soll

links2 = y_a
rechts2 = y_a
stereo2 = np.vstack((links2,rechts2)).transpose()
#write("PP4_System_B.wav", Fs, stereo2)
print("Es wird die Datei aus System B abgespielt.")
sd.play(1 * stereo2, Fs)  # Array als Sound abspielen      # #entfernen, wenn es abgespielt werde soll
#sd.wait()  # warten bis Wiedergabe beendet                 # #entfernen, wenn es abgespielt werde soll

########################################################################################################
#FFT umwandeln in Frequenzbereich aus PP3
#######################################################################################################

NFFT = samples
t_plot = np.linspace(0,(NFFT-1)*delta_t, NFFT)
f = np.linspace(0,(NFFT-1)*(Fs/NFFT), NFFT)
f_plot = f[0:int(NFFT/2+1)]
############# original Signal #################
Spektrum = np.fft.fft(x) / NFFT
Spektrum_abs = np.abs(Spektrum)
Spektrum_plot = 2* Spektrum_abs[0:int(NFFT/2+1)]
Spektrum_plot[0] = Spektrum_plot[0]/2

############### System A ######################
Spektrum1 = np.fft.fft(output_clip) / NFFT
Spektrum1_abs = np.abs(Spektrum1)
Spektrum1_plot = 2* Spektrum1_abs[0:int(NFFT/2+1)]
Spektrum1_plot[0] = Spektrum1_plot[0]/2

############### System B ######################
Spektrum2 = np.fft.fft(y_a) / NFFT
Spektrum2_abs = np.abs(Spektrum2)
Spektrum2_plot = 2* Spektrum2_abs[0:int(NFFT/2+1)]
Spektrum2_plot[0] = Spektrum2_plot[0]/2

#######################################################################################################
#Effektivwert:
#######################################################################################################

print("___________original Signal___________")
eff_o = np.sqrt(1 / x.size * (np.sum(np.square(x))))
print("Effektivwert:    {:.2f}".format(eff_o))

#Crestfaktor:
crest_o = np.max(x) / eff_o
print("Crestfaktor:     {:.2f}".format(crest_o))

print("___________System A___________")
eff_a = np.sqrt(1 / output_clip.size * (np.sum(np.square(output_clip))))
print("Effektivwert:    {:.2f}".format(eff_a))

#Crestfaktor:
crest_a = np.max(output_clip) / eff_a
print("Crestfaktor:     {:.2f}".format(crest_a))

print("___________System B___________")
eff_b = np.sqrt(1 / y_a.size * (np.sum(np.square(y_a))))
print("Effektivwert:    {:.2f}".format(eff_b))

#Crestfaktor:
crest_b = np.max(y_a) / eff_b
print("Crestfaktor:     {:.2f}".format(crest_b))


#####################################################################
#Klirrfaktor berechnen

#u1, u2, u3 System A
index = np.argmax(Spektrum1_plot)
Frequenz = f[index]
u1_a = Spektrum1_plot[index]
h1_a = f[index * 2]
u2_a = Spektrum1_plot[index * 2]
h2_a = f[index * 3]
u3_a = Spektrum1_plot[index * 3]

#u1, u2, u3 System B
index2 = np.argmax(Spektrum2_plot)
Frequenz = f[index2]
u1_b = Spektrum2_plot[index2]
h1_b = f[index2 * 2]
u2_b = Spektrum2_plot[index2 * 2]
h2_b = f[index2 * 3]
u3_b = Spektrum2_plot[index2 * 3]
##########################################
print("____________Grundschwingung und Oberschwingungen____________")
print("System A u1: {:.4f}".format(u1_a),"    System B u1: {:.4f}".format(u1_b))
print("System A u2: {:.4f}".format(u2_a),"    System B u2: {:.4f}".format(u2_b))
print("System A u3: {:.4f}".format(u3_a),"    System B u3: {:.4f}".format(u3_b))

u1_a_2 = u1_a ** (2)  # Amplitude der Grundschwingung System A
u2_a_2 = u2_a ** (2)  # Amplitude der 1. Harmonischen System A
u3_a_2 = u3_a ** (2)  # Amplitude der 2. Harmonischen System A
u1_b_2 = u1_b ** (2)  # Amplitude der Grundschwingung System B
u2_b_2 = u2_b ** (2)  # Amplitude der 1. Harmonischen System B
u3_b_2 = u3_b ** (2)  # Amplitude der 2. Harmonischen System B
print(" ")
klirr_a = np.sqrt((u2_a_2 + u3_a_2) / (u1_a_2 + u2_a_2 + u3_a_2)) * 100
print("Klirrfaktor System A: {:.2f}%".format(klirr_a))
klirr_b = np.sqrt((u2_b_2 + u3_b_2) / (u1_b_2 + u2_b_2 + u3_b_2)) * 100
print("Klirrfaktor System B: {:.2f}%".format(klirr_b))

###### plot ###################
# Ausgangssignal
kurz = int(samples*0.04)    #Zeitbereich
kurz2 = int(samples/5)      #Frequenzbereich


fig, ax = plt.subplots(3,2)
ax[0,0].plot(t_plot,x)                  #org Signal
ax[0, 0].set_title("original Signal")
ax[0, 0].set_xlabel("Zeit [s]")
ax[0, 0].set_ylabel("Amplitude")
ax[0,1].plot(f_plot,Spektrum_plot)      #FB org Signal
ax[0,1].set_title("Spektrum original Signal")
ax[0,1].set_xlabel("Frequenz [Hz]")
ax[0,1].set_ylabel("Amplitude")
ax[1,0].plot(t_plot,output_clip)        # Signal System A
ax[1,0].set_title("Signal System A")
ax[1,0].set_xlabel("Zeit [s]")
ax[1,0].set_ylabel("Amplitude")
ax[1,1].plot(f_plot,Spektrum1_plot)     #FB Signal System A
ax[1,1].set_title("Spektrum System A")
ax[1,1].set_xlabel("Frequenz [Hz]")
ax[1,1].set_ylabel("Amplitude")
ax[2,0].plot(t_plot,y_a)                # Signal System B
ax[2,0].set_title("Signal System B")
ax[2,0].set_xlabel("Zeit [s]")
ax[2,0].set_ylabel("Amplitude")
ax[2,1].plot(f_plot,Spektrum2_plot)     #FB Signal System B
ax[2,1].set_title("Spektrum System B")
ax[2,1].set_xlabel("Frequenz [Hz]")
ax[2,1].set_ylabel("Amplitude")
ax[0,1].grid()
ax[1,1].grid()
ax[2,1].grid()
plt.show()
