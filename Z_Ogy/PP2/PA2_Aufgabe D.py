import numpy as np
from scipy.io.wavfile import read
from scipy.io.wavfile import write
import matplotlib.pyplot as plt

#Einlesen der Sounddatei
abtastrate, data = read("schnipsen.wav")
print('Abtastrate: ' + str(abtastrate) + ' Hz')

#Normierung des Monosignals auf die Amplitude 1
data = data / max(data, key=abs)

#Mulitplikation mit Vorfaktor 0,5 --> Gesamtamplitude = 1
data_l = 0.5 * np.insert(data, 0, np.zeros(441))     #Delay mit zu Beginn angefügten Nullen
data_r = 0.5 * np.append(data, np.zeros(441))        #Zweiten Kanal auf dieselbe Länge erweitern