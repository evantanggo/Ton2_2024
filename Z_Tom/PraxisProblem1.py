#Praxis Problem 1 Gruppe 3
#Tom Butenschön
#

import numpy as np
from scipy.io.wavfile import read
from matplotlib import pyplot as plt


impulsantwort_wav = 'TON2 Tom/Datei_B.wav'

# Auslesen und Speichern der Abtastrate in  Fs und der Impulsantwort als Array in impulsantwort aus der WAV-Datei
Fs, impulsantwort = read(impulsantwort_wav)

#wenn es 2 Kanäle gibt, beide addieren und halbieren --> Stereo zu Mono
if impulsantwort[1].size == 2:
    impulsantwort = impulsantwort[:, 0] + impulsantwort[:1] / 2

#normieren auf 1, alle Werte im Array werden durch den größten Wert dividiert
impulsantwort_n = impulsantwort/np.max(impulsantwort)

#Startpunkt = Stelle im Array mit größstem Wert == Startpunkt für c50 und c80
for n in range(0, len(impulsantwort_n)):
    if impulsantwort_n[n] == np.max(impulsantwort_n):
        Startpunkt = n

#Summe der Quadrate geteilt durch Abtastrate
Gesamtenergie_n = np.sum(np.square(impulsantwort_n))

#erstellen eines Arrays mit den Energiesummen von jedem Zeitpunkt bis zum Ende
Einzelenergien = np.zeros(len(impulsantwort_n))
for n in range(0, len(impulsantwort_n)):
    Einzelenergien[n] = np.sum(np.square(impulsantwort_n[n:len(impulsantwort_n)]))
#Einzelenergien = Einzelenergien/Fs  --> wenn nicht normiert

#Zwischenrechnung Array gefüllt mit Teilenergien geteilt durch Gesamtenergie
Schroeder_temp = Einzelenergien / Gesamtenergie_n

#Berechnung des Arrays für den Schröderplot
Schroeder = 10* np.log10(Schroeder_temp)
#########################################################################################################
#Nachhallzeit TN
#Zeitpunkt: 5 dB Abfall um Direktschall auszuschließen
t5 = 0
Schroeder_t5 = Schroeder[Startpunkt:len(Schroeder)]
for s in range(0, len(Schroeder_t5)):
    if (Schroeder_t5[s] < -5):
        t5 = s /Fs
        xt5 = t5
        yt5 = Schroeder[s]
        break

#selbgewählt, kleinster akzeptierter dB-Abfall (7 dB), da linearer Bereich sehr sehr klein
T12 = 0
Schroeder_t5 = Schroeder[Startpunkt:len(Schroeder)]
for s in range(0, len(Schroeder_t5)):
    if (Schroeder_t5[s] < -12):
        T12 = s /Fs
        break
T7 = (T12-t5) * (60/7)
print()
print("T7 in Sekunden:  {:.2f}".format(T7))
print()
T15 = 0
Schroeder_t5 = Schroeder[Startpunkt:len(Schroeder)]
for s in range(0, len(Schroeder_t5)):
    if (Schroeder_t5[s] < -15):
        T15 = s /Fs
        break
T10 = (T15-t5) * 6
#########################################################################################################
# Korrelationsfaktor T10 im Bezug auf T7
K = T7 / T10
print("T10 in Sekunden: {:.2f}".format(T10),"   mit einem Korrelationsfaktor von: {:.2f}".format(K))

T25 = 0
Schroeder_t5 = Schroeder[Startpunkt:len(Schroeder)]
for s in range(0, len(Schroeder_t5)):
    if (Schroeder_t5[s] < -25):
        T25 = s /Fs
        break
T20 = (T25-t5) * 3

# Korrelationsfaktor T20 im Bezug auf T7
K = T7 / T20
print("T20 in Sekunden: {:.2f}".format(T20),"   mit einem Korrelationsfaktor von: {:.2f}".format(K))

T35 = 0
Schroeder_t5 = Schroeder[Startpunkt:len(Schroeder)]
for s in range(0, len(Schroeder_t5)):
    if (Schroeder_t5[s] < -35):
        T35 = s /Fs
        break
T30 = (T35-t5) * 2
# Korrelationsfaktor T30 im Bezug auf T7
K = T7 / T30
print("T30 in Sekunden: {:.2f}".format(T30),"   mit einem Korrelationsfaktor von: {:.2f}".format(K))

print("-----------------------------------------------------------------")
#########################################################################################################
#C50 und C80
#neuen Array erstellen, erste Stelle auch erster Wert der Impulsantwort
impulsantwort_n_modifiziert = impulsantwort_n[Startpunkt:len(impulsantwort_n)]

#Stelle im Array an der 50 bzw. 80ms Wert steht
t50 = round(50 / 1000 * Fs)
t80 = round(80/1000 * Fs)

#Brechnung Teilenergiesumme bis 50ms und nach 50ms + Verhältnis
Energie_C50 = np.sum(np.square(impulsantwort_n_modifiziert[0:t50])) / np.sum(np.square(impulsantwort_n_modifiziert[t50+1:]))
C50 = 10* np.log10(Energie_C50)
print("Deutlichkeitsmaß: {:.2f}".format(C50), "dB")
#Berechnung Teilenergiesumme bis 80ms und nach 80ms + Verhältnis
Energie_C80 = np.sum(np.square(impulsantwort_n_modifiziert[0:t80])) / np.sum(np.square(impulsantwort_n_modifiziert[t80+1:]))
C80 = 10* np.log10(Energie_C80)
print("Klarheitsmaß:     {:.2f}".format(C80), "dB")
#########################################################################################################
#plot
x1 = np.arange(len(Schroeder))/Fs
y1 = impulsantwort_n
x2 = np.arange(len(Schroeder))/Fs
y2 = Schroeder

Figure, Plot = plt.subplots(2)
Plot[0].plot(x1, y1, "tab:blue")
Plot[0].set_title("Impulsantwort normiert")
Plot[0].set_xlabel("Zeit [s]")

Plot[1].plot(x2, y2, "tab:red")
Plot[1].set_title("Schroeder Plot")
Plot[1].set_xlabel("Zeit [s]")
Plot[1].set_ylabel("Sound level [dB]")
Plot[1].plot(xt5, yt5, marker = "X", c="black", label="t5")  #markiert t5
Plot[1].legend(loc='upper right')
Figure.tight_layout()

plt.show()

