'''
Praxisaufgabe 2
Einzelwerte von Signalen
'''

import math
from scipy.io.wavfile import read
import numpy as np

dataMono = np.array
file = 'sinus_440Hz_mono.wav' #um file zu ändern Dateinamen anpassen
(Fs, y) = read (file)

if y.ndim == 2: #überprüft, ob die Datei Stereo oder Mono ist und rechnet sie in Mono um
    y_L = y[:,0]
    y_R = y[:,1]
    dataMono = (y_L + y_R)/2
else:
    dataMono = y

T = len(dataMono)
samples = np.arange(len(dataMono)) #erstellt ein Array mit so viele Werten

def effektivWert(daten):
    global T, samples

    daten = daten.astype(np.float64) #andert in float 64
    square = np.square(daten)
    integral = sum(square)  # summiert alle Werte des Arrays
    eWert = math.sqrt(1 / T * integral)  # rechnet das Integral * 1/T und zieht die Wurzel
    return eWert

#def gleichRichtWert(daten):
    #global T, samples



print(effektivWert(dataMono))

