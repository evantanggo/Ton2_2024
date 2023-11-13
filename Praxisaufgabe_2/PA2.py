'''
Praxisaufgabe 2
Einzelwerte von Signalen
'''

import math
from scipy.io.wavfile import read
import numpy as np

dataMono = np.array #hier erstellt ein leeres array
file = 'sinus_100Hz_2s.wav' #um file zu ändern Dateinamen anpassen
(Fs, y) = read(file) #Fs = 44100Hz

if y.ndim == 2: #überprüft, ob die Datei Stereo oder Mono ist und rechnet sie in Mono um
    y_L = y[:,0]
    y_R = y[:,1]
    dataMono = (y_L + y_R)/2
else:
    dataMono = y

T = len(dataMono) #Anzahl der Werte
print(f"T", T)

samples = np.arange(len(dataMono)) #erstellt ein Array mit so viele Werten

def effektivWert(daten):
    global T, samples

    daten = daten.astype(np.float64) #andert in float 64
    square = np.square(daten) #quadrieren
    integral = sum(square)  # summiert alle Werte des Arrays

    eWert = math.sqrt((1/T) * integral)  # rechnet das Integral * 1/T und zieht die Wurzel

    return eWert

def gleichRichtwert(daten):
    global T, samples
    daten = daten.astype(np.float64)
    for i in range(len(daten)):
        daten[i] = abs([daten[i]]) # Betrag aller Werte des Arrays
    integral = sum(daten)
    gWert = 1/T * integral
    return gWert


def scheitelFaktor(effektivWert):
    global dataMono
    y_max = np.max(dataMono)
    y_min = np.min(dataMono)
    aMax = max(y_max, abs(y_min))

    c = aMax/effektivWert
    return c

print(f"Datei = ", file)
print(f"Effektivwert = ", effektivWert(dataMono))
print(f"Crest Faktor = ", scheitelFaktor(effektivWert(dataMono)))

