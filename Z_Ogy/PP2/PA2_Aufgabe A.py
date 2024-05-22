import numpy as np
from scipy.io.wavfile import read
from scipy.io.wavfile import write
import matplotlib.pyplot as plt

#Einlesen der Sounddatei
abtastrate, data = read("schnipsen.wav")
print('Abtastrate: ' + str(abtastrate) + ' Hz')

#Normierung des Monosignals auf die Amplitude 1
data = data / max(data, key=abs)

Delay = [441, 441*2, 441*3]

#Mulitplikation mit Vorfaktor 0,5 --> Gesamtamplitude = 1

for d in Delay:
    data_l = 0.5 * np.insert(data, 0, np.zeros(d))     #Delay mit zu Beginn angefügten Nullen
    data_r = 0.5 * np.append(data, np.zeros(d))        #Zweiten Kanal auf dieselbe Länge erweitern
    Stereo_data = np.column_stack((data_l, data_r))
    Stereo_data *= 32767 / np.max(np.abs(Stereo_data))
    Stereo_data = Stereo_data.astype(np.int16)
    write("Delay Schnipsen_" + str(d / 44100) + " ms" + ".wav", abtastrate, Stereo_data)