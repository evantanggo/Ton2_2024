import numpy as np
import matplotlib.pyplot as plt
from scipy.io.wavfile import read, write
from scipy.fftpack import fft, rfft, rfftfreq, irfft, ifft
from scipy import signal
import time

# Einlesen der Audiodatein
abtastrate, ht = read("Datei_i.wav")
abtastrate, xt = read("plopp.wav")

abtastrate0, xt_0 = read("D2azi_0,0_ele_0,0.wav")
abtastrate45, xt_45 = read("D2azi_45,0_ele_0,0.wav")
abtastrate90, xt_90 = read("D2azi_90,0_ele_0,0.wav")
abtastrate135, xt_135 = read("D2azi_135,0_ele_0,0.wav")
abtastrate180, xt_180 = read("D2azi_180,0_ele_0,0.wav")
abtastrate225, xt_225 = read("D2azi_225,0_ele_0,0.wav")
abtastrate270, xt_270 = read("D2azi_270,0_ele_0,0.wav")

BRIR = [xt_0, xt_45, xt_90, xt_135, xt_180, xt_225, xt_270]

print('Abtastrate: ' + str(abtastrate) + ' Hz')             # Abtastrate ausgeben lassen


# Länge der Signale
n_h = len(ht)                                                                   # Anzahl der Samples der Impulsantwort
signallaenge_h = n_h / abtastrate                                               # durch Abtastrate teilen, um auf Länge
print('Länge der Impulsantwort: ' + str(np.round(signallaenge_h, 2)) + ' sek.')  # in Sekunden zu kommen.

n_x = len(xt)                                                                   # Anzahl der Samples des Eingangssignals
signallaenge_x = n_x / abtastrate                                               # durch Abtastrate teilen, um auf Länge
print('Länge der Audio: ' + str(np.round(signallaenge_x,2)) + ' sek.')          # in Sekunden zu kommen.


# Linker Kanal aus Stereo Datei
ht = [x[0] for x in ht]   # durch x[0/1] kann man den linken/rech-
#xt = [x[0] for x in xt]                                                                                # ten extrahieren -> Mono

#Normalisierung
ht = ht / max(ht)
xt = xt / max(xt)



# Faltung im Zeitbereich
start = time.time()                                                             # Start der Zeitmessung
yt = np.convolve(ht, xt)                                                        # Faltung
ende = time.time()                                                              # Ende der Zeitmessung
print("Dauer Faltung: {:5.3f}s".format(ende-start))  # Zeitdifferenz ausgeben  # Ausgabe der gemessenen Zeit

# Signale auf gleiche Länge bringen
diff = len(yt) - len(xt)
xt_0 = np.append(xt, np.zeros(diff))                                # So viele Nullen wie Differenz anhängen


# Faltung im Frequenzbereich
start = time.time()                                                             # Start der Zeitmessung
# Zero-padding: Signal doppelt so lang machen & mit Nullen auffüllen
diff = len(xt) - len(ht)
Xt = np.append(xt, np.zeros(len(xt) - 1))
Ht = np.append(ht, np.zeros(len(ht) - 1 + 2*diff))

# FFT der beiden Eingangssignale
Xf = np.fft.rfft(Xt)
Hf = np.fft.rfft(Ht)

# Multiplikation im Frequenzbereich = Faltung im Zeitbereich
Yf = Hf * Xf
# Rücktransformation
yt_fft = np.fft.irfft(Yf) # Inverse FFT
ende = time.time()                                                               # Ende der Zeitmessung
print("Dauer FFT Multiplikation: {:5.3f}s".format(ende-start))                   # Ausgabe der gemessenen Zeit

# Das Ausgangssignal ist länger als das Eingangssignal xt -> xt mit Nullen aufgefüllt
diff = len(yt_fft) - len(xt)
xtf_0 = np.append(xt, np.zeros(diff))


# Erneutes Normieren beider Signale
yt = yt / max(yt, key=abs)
yt_fft = yt_fft / max(yt_fft, key=abs)

# Als wav. speichern
write("Hall_T.wav", abtastrate, yt)
write("Hall_FFT.wav", abtastrate, yt_fft)

BR = []

for h in BRIR:

    Xt = 0
    Ht = 0

    # Faltung im Frequenzbereich
    start = time.time()
    # Zero-padding: Signal doppelt so lang machen & mit Nullen auffüllen
    #print("Länge xt:", len(xt), "Länge ht:", len(h))
    # Überprüfung ob die Files gleichlang sind
    if len(h) < len(xt):
        # wenn Eingang länger als Impulsantwort
        # differenz berechnen
        diff = len(xt) - len(h)
        # so viele nullen dranhängen, wie die differenz beträgt
        # axis=0 sorgt dafür, dass es ein 2-dimensionales array (stereo) bleibt
        h_t = np.append(h, np.zeros((diff, 2)), axis=0)
    
    Xt = np.append(xt, np.zeros(len(xt)  ))


    Ht = np.append(h, np.zeros(len(h) ))

    if len(Ht) < len(Xt):
        diff = len(Xt) - len(Ht)
        Ht = np.append(Ht, np.zeros(diff), axis=0)


    # FFT der beiden Eingangssignale
    Xf = np.fft.rfft(Xt)

    Hf = np.fft.rfft(Ht)



    # Multiplikation im Frequenzbereich = Faltung im Zeitbereich
    Yf = Hf * Xf
    # Rücktransformation
    yt_fft = np.fft.irfft(Yf) # Inverse FFT
    ende = time.time()                                                               # Ende der Zeitmessung
    print("Dauer FFT Multiplikation: {:5.3f}s".format(ende-start))                   # Ausgabe der gemessenen Zeit

    # Das Ausgangssignal ist länger als das Eingangssignal xt -> xt mit Nullen aufgefüllt
    diff = len(yt_fft) - len(xt)
    xtf_0 = np.append(xt, np.zeros(diff))
    yt_fft = yt_fft / max(yt_fft, key=abs)
BR.append(yt_fft)


BR = np.asarray(BR)

BR = np.asarray(BR, dtype=np.float32)
plt.figure()
plt.plot(BR)
plt.show()
write("Binaural Plopp.wav", abtastrate, BR.T)
