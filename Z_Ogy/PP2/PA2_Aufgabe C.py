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

#Liste mit Amplitudenwerten für Kanal L + R für ILD
A1 = [0.8]
A2 = [0.2]

#Multiplikation mit Amplitude aus Liste
data_l = A1 * data_l
data_r = A2 * data_r

#Stereo
Stereo_data = np.column_stack((data_l, data_r))

#normieren auf 2**15-1 (maximaler Wert bei 16 Bit-Darstellung)
Stereo_data *= 32767 / np.max(np.abs(Stereo_data))

#konvertieren in 16-bit Daten
Stereo_data = Stereo_data.astype(np.int16)

#Erzeugen der Stereo-Wave-Datei
write("C_Panning_ILD_ITD_80_20_10ms_L.wav", abtastrate, Stereo_data)