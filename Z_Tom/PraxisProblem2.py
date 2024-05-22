#Praxis Problem 2 Gruppe 3
#Tom Butenschön
#

import numpy as np
from scipy.io.wavfile import read
from scipy.io.wavfile import write
import sounddevice as sd

sound_wav = "snow.wav"
# Auslesen und Speichern der Abtastrate in  Fs und des Signals als Array in signal aus der WAV-Datei
Fs, signal = read(sound_wav)

#wenn es 2 Kanäle gibt, beide addieren und halbieren --> Stereo zu Mono

if signal[1].size == 2:
    signal = signal[:,0] + signal[:,1] / 2

#normiert die Werte im Array auf 1
signal = signal/np.max(signal)

#######################################################################################
#-------------------------------------------------------------------------------------
#######################################################################################
#a Sound von rechts wahrgenommne, da links verzögert --> links zero_array davor, rechts zero_array dahinter
#Zeitdifferenz in Millisekunden umgerechnet in Arraylänge
t_ms = round(2/1000 * Fs)   #Zeitdifferenz 0,2 ms umgerechet in Arraylänge
#Array mit Nullen gefüllt abhänging von der gewählten Zeitdifferenz
extra = np.zeros(t_ms, dtype=int)
check = input("Aufgabenteil A ausführen? ja oder nein --> j/n: ")
if check == "j":
    links_a = np.append(extra,signal)
    rechts_a = np.append(signal,extra)
    stereo = np.vstack((links_a,rechts_a)).transpose()
    #neues Array mit 2 Kanälen in eine Wavedatei schreiben / kann aktiviert werden, wenn Datei erstellt werden soll
    #write("Aufgabe_A.wav", Fs, stereo)
    print("Aufgabe A wird abgespielt. --> links verzögert, dadurch rechts wahrgenommen")
    sd.play(1 * stereo, Fs)  #Array als Sound abspielen
    sd.wait()  #warten bis Wiedergabe beendet
else:
    print("Aufgabenteil A übersprungen.")
#######################################################################################
#-------------------------------------------------------------------------------------
#######################################################################################
#b - links Amplitude verkleinern 75% Regler entspricht ca -8dB links und 0dB rechts
#Sound von rechts wahrgenommen durch Amplituenverringerung links
check = input("Aufgabenteil B ausführen? ja oder nein --> j/n: ")
if check == "j":
    faktor = 2.5 #(8dB) da faktor= 10^(8/20) aus Abb PP2-3 75% entspricht ca 8 dB differenz
    links_b = signal / faktor
    rechts_b = signal
    stereo = np.vstack((links_b,rechts_b)).transpose()
    #write("Aufgabe_B.wav", Fs, stereo)
    print("Aufgabe B wird abgespielt. --> links leiser, dadruch rechts wahrgenommen")
    sd.play(1 * stereo, Fs)  #Array als Sound abspielen
    sd.wait()  #warten bis Wiedergabe beendet
else:
    print("Aufgabenteil B übersprungen.")
#######################################################################################
#-------------------------------------------------------------------------------------
#######################################################################################
#c - a & b zusammen, links später, rechts leiser
#noch optimierungsbedarf
#Zeitdifferenz aus A
#Faktor für Amplitude aus B
check = input("Aufgabenteil C ausführen? ja oder nein --> j/n: ")
if check == "j":
    links_c = np.append(extra,signal)
    rechts_c = np.append(signal,extra) / faktor
    stereo_c = np.vstack((links_c,rechts_c)).transpose()
    #write("Aufgabe_C.wav", Fs, stereo_c)
    print("Aufgabe C wird abgespielt. --> links verzögert, rechts leiser, dadurch mittig wahrgenommen")
    sd.play(1 * stereo, Fs)  #Array als Sound abspielen
    sd.wait()  #warten bis Wiedergabe beendet
else:
    print("Aufgabenteil C übersprungen")
#######################################################################################
#-------------------------------------------------------------------------------------
#######################################################################################
#d - Zeit bis Einzelsignale erkennbar
check = input("Aufgabenteil D ausführen? ja oder nein --> j/n: ")
if check == "j":
    delta_t = round(5/1000 *Fs) #5ms Schritte
    i=0
    for i in range (0,10):
        extra = np.zeros(delta_t*i, dtype=int)
        links_d = np.append(extra, signal)
        rechts_d = np.append(signal, extra)
        #arrays verkürzen um nicht immer 10 Sekunden zu hören
        links_d_kurz = links_d[0:(Fs*5)]
        rechts_d_kurz = signal[0:(Fs*5)]
        stereo = np.vstack((links_d_kurz,rechts_d_kurz)).transpose()
        #write("Aufgabe_D.wav", Fs, stereo)
        sd.play(1 * stereo, Fs)  # Array als Sound abspielen
        sd.wait()  # warten bis Wiedergabe beendet
        check = input("Sind zwei Einzelsignale zu erkennen? 0/1: ")
        if check == "1":
            time = round(delta_t * i / Fs * 1000)
            print("Die Laufzeitdifferenz zwischen den Kanälen beträgt: ",time," ms")
            break
        elif check == "0":
            i += 1
            print("Laufzeitdifferenz wird erhöht.")
        else:
            print("ungültige Eingabe. Erlaubte Eingabewerte: 0 oder 1")
            print("Die Laufzeitdifferenz ist unverändert.")
        i = i+1
else:
    print("Aufgabenteil D wird übersprungen")
#######################################################################################
#-------------------------------------------------------------------------------------
#######################################################################################

#e - links nach rechts automatisch -- Pegel links von 100% auf 0% / Pegel rechts von 0% auf 100%
# 10 sekunden Laufzeit wichtig signal muss mindestens 11 sek lang sein, sonst code anpassen
check = input("Aufgabenteil E ausführen? ja oder nein --> j/n: ")
if check == "j":
    if len(signal)/Fs > 10:
        i = 0
        j = 10
        links_e = 0
        rechts_e = 0
        while i <= 10:
            links = signal[Fs*i:Fs*(i+1)] * (0.1 * j)
            rechts = signal[Fs*i:Fs*(i+1)] * (0.1 * i)
            links_e = np.append(links_e,links)
            rechts_e = np.append(rechts_e,rechts)
            i +=1
            j -=1
        stereo = np.vstack((links_e,rechts_e)).transpose()
        #write("Aufgabe_E.wav", Fs, stereo)
        print("Aufgabenteil E wird abgespielt.")
        sd.play(1 * stereo, Fs)  # Array als Sound abspielen
        sd.wait()  # warten bis Wiedergabe beendet
    else:
        print("bitte ein längeres Signal (mind. 10 Sekunden) einfügen")
        print("das Signal ist: {:.2f}".format(len(signal)/Fs),"s lang")
else:
    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++Das Programm wird beendet")
