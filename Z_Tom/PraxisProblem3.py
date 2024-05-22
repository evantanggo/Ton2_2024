#Praxis Problem 3 Gruppe 3
#Tom Butenschön
#


import numpy as np
import scipy
import matplotlib.pyplot as plt
from scipy.io.wavfile import read
from scipy.io.wavfile import write
import sounddevice as sd

Eingang = 'voice.wav' #Auswahl Sprache "voice.wav" oder Musik "drop.wav"
fgr_HP = 1000       #vorgegebene Grenzfrequenz

fs, x_t = read(Eingang)         #Abtastfrequenz und Signal
delta_t = 1 / fs                #Abtastzeitinterval

#wenn es 2 Kanäle gibt, beide addieren und halbieren --> Stereo zu Mono
if x_t[1].size == 2:
    x_t = x_t[:,0] + x_t[:,1] / 2

x_t_n = x_t / max(x_t,key=abs) #*(pow(2,15)-1)

NFFT = len(x_t_n)                                  #NFFT= fs/f0 = len(x_t) Anzahl der Samples
Zeit = NFFT/fs
#Array erzeugen für die Achsem des Plots
t = np.linspace(0,(NFFT-1)*delta_t, NFFT)           #von, bis inklusiv, Menge an Werten
f = np.linspace(0,(NFFT-1)*(fs/NFFT), NFFT)       #T=1/f0 = fs/NFFT = fs/(fs/f0)

#Zeitbereich in Frequenzbereich Grundsignal
Spektrum = np.fft.fft(x_t_n) / NFFT
Spektrum_abs = np.abs(Spektrum)
f_plot = f[0:int(NFFT/2+1)]                                  #kürzer
Spektrum_plot = 2* Spektrum_abs[0:int(NFFT/2+1)]
Spektrum_plot[0] = Spektrum_plot[0]/2

######################################
# Hochpass erster Ordnung:
y_HP_1 = np.zeros(NFFT)

alpha_HP = 1 / (1 + fgr_HP * 2 * np.pi * delta_t)

y_HP_1[0] = x_t[0] * alpha_HP

for i in range(1, NFFT):
    y_HP_1[i] = alpha_HP * (y_HP_1[i - 1] + x_t[i] - x_t[i - 1])

y_HP_1 = y_HP_1/ max(y_HP_1, key=abs)  # *(pow(2,15)-1)

##### Transformation in den Frequenzbereich nach Filter 1. Ordnung:

Spektrum2 = np.fft.fft(y_HP_1) / NFFT
Spektrum2_abs = np.abs(Spektrum2)
f_plot = f[0:int(NFFT/2+1)]
Spektrum2_plot = 2* Spektrum2_abs[0:int(NFFT/2+1)]
Spektrum2_plot[0] = Spektrum2_plot[0]/2
write("PP3_HP1_output.wav", fs, y_HP_1)
###################################
# Hochpass zweiter Ordnung:
y_HP_2 = np.zeros(NFFT)

alpha_HP = 1 / (1 + fgr_HP * 2 * np.pi * delta_t)

y_HP_2[0] = y_HP_1[0] * alpha_HP

for i in range(1, NFFT):
    y_HP_2[i] = alpha_HP * (y_HP_2[i - 1] + y_HP_1[i] - y_HP_1[i - 1])

y_HP_2 = y_HP_2 / max(y_HP_2, key=abs)  # *(pow(2,15)-1)

##### Transformation in den Frequenzbereich nach Filter 2. Ordnung:
Spektrum3 = np.fft.fft(y_HP_2) / NFFT
Spektrum3_abs = np.abs(Spektrum3)
f_plot = f[0:int(NFFT/2+1)]                                  #kürzer, um an x-Achse anzupassen
Spektrum3_plot = 2* Spektrum3_abs[0:int(NFFT/2+1)]
Spektrum3_plot[0] = Spektrum3_plot[0]/2                       #x-Achse verkürzt, sonst Spektrale Wdl.
write("PP3_HP2_output.wav", fs, y_HP_2)

###### plot ###################
fig, ax = plt.subplots(3,2)
ax[0,0].plot(t,x_t_n)
ax[0,0].set_title("original Signal")
ax[0,0].set_xlabel("Zeit [s]")
ax[0,0].set_ylabel("Amplitude")
ax[0,1].plot(f_plot,Spektrum_plot)
ax[0,1].set_title("Spektrum original Signal")
ax[0,1].set_xlabel("Frequenz [Hz]")
ax[0,1].set_ylabel("Amplitude")
ax[0,1].axvline(x=fgr_HP, color='red', linestyle='-', label='Fgr')  #plottet Linie auf der Grenzfrequenz
ax[1,0].plot(t,y_HP_1)
ax[1,0].set_title("Signal nach HP1")
ax[1,0].set_xlabel("Zeit [s]")
ax[1,0].set_ylabel("Amplitude")
ax[1,1].plot(f_plot,Spektrum2_plot)
ax[1,1].set_title("Spektrum nach HP1")
ax[1,1].set_xlabel("Frequenz [Hz]")
ax[1,1].set_ylabel("Amplitude")
ax[1,1].axvline(x=fgr_HP, color='red', linestyle='-', label='Fgr')
ax[2,0].plot(t,y_HP_2)
ax[2,0].set_title("Signal nach HP2")
ax[2,0].set_xlabel("Zeit [s]")
ax[2,0].set_ylabel("Amplitude")
ax[2,1].plot(f_plot,Spektrum3_plot)
ax[2,1].set_title("Spektrum nach HP2")
ax[2,1].set_xlabel("Frequenz [Hz]")
ax[2,1].set_ylabel("Amplitude")
ax[2,1].axvline(x=fgr_HP, color='red', linestyle='-', label='Fgr')
ax[0,1].grid()
ax[1,1].grid()
ax[2,1].grid()
fig.tight_layout()
plt.show()

#######################################################################################
#-------------------------------------------------------------------------------------
#######################################################################################
check = input("PingPongDelay ausführen? ja oder nein --> j/n: ")
if check == "j":
    #PinPong-Delay

    t_ms = round(500/1000 * fs)     #Zeitdifferenz 50 ms umgerechet in Arraylänge
    #wenn 2 Kanäle vorhanden, aufteilen -->  sonst Signal einmal in den linken bzw. rechten Kanal übernehmen
    if x_t[1].size == 2:
        links = x_t[:,0]
        rechts = x_t[:,1]
    else:
        links = x_t
        rechts = x_t
    #Signale auf 1 normieren
    links = links/max(links,key=abs)
    rechts = rechts/max(rechts,key=abs)

    #Array mit Nullen gefüllt abhänging von der gewählten Zeitdifferenz
    extra_L = np.zeros(t_ms, dtype=int)
    extra_R = np.zeros((2*t_ms), dtype=int)
    #delay-Effekt für den linken Kanal erzeugen
    #2 Kanale links verzögert, rechts verlängert
    #Array mit Nullen davor für das delay, dahinter um auf die gleiche Länge wie beim rechten Delaykanal zu kommen
    links_delay_L_1 = np.append(extra_L,links)
    links_delay_L = np.append(links_delay_L_1, extra_L)
    #extra_R hinten an das Signal, um später alle Arrays gleich lang zu haben
    rechts_delay_L = np.append(rechts,extra_R)
    #delay-Effekt für den linken Kanal erzeugen
    #2 Kanale rechts verzögert, links verlängert
    #doppelter Nullenarray für doppelte Verzögerung
    links_delay_R = np.append(links,extra_R)
    rechts_delay_R = np.append(extra_R,rechts)
    #stereo_array für den linken Effekt und für den rechten Effekt
    stereo_delay_L = np.vstack((links_delay_L,rechts_delay_L)).transpose()
    stereo_delay_R = np.vstack((links_delay_R,rechts_delay_R)).transpose()
    #zusammenfügen der beiden Effektarrays in ein Effektarray und halbieren (Signalpegel/Amplitude verringern)
    stereo_delay_LR = (stereo_delay_L + stereo_delay_R) / 2
    #Ausgnagssignal verlängern, um den Effektarray addieren zu können
    links_new = np.append(links,extra_R)
    rechts_new = np.append(rechts,extra_R)
    stereo = np.vstack((links_new,rechts_new)).transpose()
    #Siganl + PingPongDelay
    stereo_output = stereo + stereo_delay_LR
    #neuerstellter Array mit 2 Kanälen in eine Wavedatei schreiben
    #write("PingPongDelay.wav", fs, stereo_output)
    sd.play(1 * stereo_output, fs)  # Array als Sound abspielen
    sd.wait()  # warten bis Wiedergabe beendet
else:
    print("PingPongDelay Aufgabenteil übersprungen.")