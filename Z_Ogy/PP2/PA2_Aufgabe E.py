import numpy as np
from scipy.io.wavfile import read
from scipy.io.wavfile import write
import matplotlib.pyplot as plt

#Einlesen der Sounddatei
abtastrate, data = read("Gitarre_mono.wav")
print('Abtastrate: ' + str(abtastrate) + ' Hz')

#Normierung des Monosignals auf die Amplitude 1
data = data / max(data, key=abs)

#Liste erzeugen

data_l = []
data_r = []
i = 0
Schrittweite = 1 / len(data)
print(Schrittweite)

for A in np.linspace(1, 0, len(data)):
    data_l.append(A * data[i])
    i += 1

i = 0
for A in np.linspace(0, 1, len(data)):
    data_r.append(A * data[i])
    i += 1


fig, ax = plt.subplots()
ax.plot(data_l)
ax.plot(data_r)
plt.show()


#Stereo
Stereo_data = np.column_stack((data_l, data_r))

#normieren auf 2**15-1 (maximaler Wert bei 16 Bit-Darstellung)
Stereo_data *= 32767 / np.max(np.abs(Stereo_data))

#konvertieren in 16-bit Daten
Stereo_data = Stereo_data.astype(np.int16)

#Erzeugen der Stereo-Wave-Datei
write("D_Wanderndes Signal.wav", abtastrate, Stereo_data)