import numpy as np
from scipy.io.wavfile import read
from scipy.io.wavfile import write
import matplotlib.pyplot as plt

#Einlesen der Sounddatei
abtastrate, data = read("schnipsen.wav")
print('Abtastrate: ' + str(abtastrate) + ' Hz')

#Normierung des Monosignals auf die Amplitude 1
data = data / max(data, key=abs)

#Liste mit Amplitudenwerten für Kanal L + R für ILD
A1 = [0.8, 0.6, 0.3]
A2 = [0.2, 0.4, 0.7]

#Multiplikation mit Amplitude aus Liste
for i, j in zip(A1, A2):
    data_l = i * data
    data_r = j * data
    Stereo_data = np.column_stack((data_l, data_r))
    Stereo_data *= 32767 / np.max(np.abs(Stereo_data))
    Stereo_data = Stereo_data.astype(np.int16)
    write("Amplitude " + str(i) + "_" + str(j) + ".wav", abtastrate, Stereo_data)