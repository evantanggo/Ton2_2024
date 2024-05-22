import numpy as np
import matplotlib.pyplot as plt
from scipy.io.wavfile import read, write
from scipy.fftpack import fft, rfft, rfftfreq, irfft, ifft
import sounddevice as sd

# Einlesen der Audiodatein
Abtastrate, Klavier = read("Klavier.wav")
Abtastrate, Vox = read("Sprache.wav")
Abtastrate, Sinus = read("1khz.wav")

print('Abtastrate: ' + str(Abtastrate) + ' Hz')                                # Drucken der Abtastrate

# Länge des Signals
n_K = len(Klavier)                                                              # Anzahl der Samples der Klavier-Audiodatei
Signallaenge_Klavier = n_K / Abtastrate                                              # durch Abtastrate teilen, um auf Länge
                                                                               # in Sekunden zu kommen.
print('Länge des Signals Klavier: ' + str(np.round(Signallaenge_Klavier,5)) + ' sek.') # Drucken der Länge in Sekunden

n_V = len(Vox)                                                               # Anzahl der Samples der Voice-Audiodatei
Signallaenge_Vox = n_V / Abtastrate                                              # durch Abtastrate teilen, um auf Länge
                                                                               # in Sekunden zu kommen.
print('Länge des Signals Vox: ' + str(np.round(Signallaenge_Vox,5)) + ' sek.') # Drucken der Länge in Sekunden

#Erzeugen von Monodateien aus Stereoformat
Klavier_M = [x[0] for x in Klavier]                                         # x[0/1] für linken/rechten Kanal
Vox_M = [x[0] for x in Vox]
Sinus_M = [x[0] for x in Sinus]

#Normierung auf Amplitude = 1
Klavier_M = Klavier_M / max(Klavier_M)
Vox_M = Vox_M / max(Vox_M)
Sinus_M = Sinus_M / max(Sinus_M)


# System A
x = np.linspace(0, 100, 100)                                           # Definition von x: 100 Werte zwischen 0 und 100

System_A = -0.5 / np.tan(x + np.pi / 2)                            # Definition der Kennlinie System A


# Ausgang
Y_Klavier_A = [-0.5 / np.tan(x + np.pi / 2) for x in Klavier_M]  #
Y_Vox_A = [-0.5 / np.tan(x + np.pi / 2) for x in Vox_M]   #

# Normierung auf Amplitude = 1
Y_Klavier_A = Y_Klavier_A / max(Y_Klavier_A)
Y_Vox_A = Y_Vox_A / max(Y_Vox_A)

# Als wav. speichern
write("Klavier_System_A.wav", Abtastrate, Y_Klavier_A)
write("Vox_System_A.wav", Abtastrate, Y_Vox_A)


# System B (Clipping)

# Clipping bei Amplitude = 0,7
Clipping_Klavier = list()                                                             # Clipping-Piano als Liste definieren
Clipping_Vox = list()                                                             # Clipping-Voice als Liste definieren
Clipping_Limit = 0.7                                                                 # Definition der Clipping-Grenze (0-1)

for x in Klavier_M:
    if x > Clipping_Limit:                      # Sobald ein Samplewert x im Signal größer als mein gesetztes Limit ist
        Clipping_Klavier.append(Clipping_Limit)       # wird x = limit (Schneidet das Signal quasi ab)

    elif x < -Clipping_Limit:                 # Sobald ein Samplewert x im Signal kleiner als mein gesetztes negatives Limit ist
        Clipping_Klavier.append(-Clipping_Limit)      # wird x = -limit gesetzt.

    else:
        Clipping_Klavier.append(x)            # Ansonsten bleibt x = x

for x in Vox_M:                       # Hier passiert das selbe für mein anderes Audiosignal
    if x > Clipping_Limit:
        Clipping_Vox.append(Clipping_Limit)

    elif x < -Clipping_Limit:
        Clipping_Vox.append(-Clipping_Limit)

    else:
        Clipping_Vox.append(x)
        
write("Klavier_System_B.wav", Abtastrate, Klavier_M)
write("Vox_System_B.wav", Abtastrate, Vox_M)

# FFT der Eingangssignale Klavier, Vox und Sinus
FFT_Klavier_M = np.fft.rfft(Klavier_M)
FFT_Vox_M = np.fft.rfft(Vox_M)
FFT_Sinus_M = np.fft.rfft(Sinus_M)

#FFT der Ausgangssignale des System A
FFT_Klavier_A = np.fft.rfft(Y_Klavier_A)
FFT_Vox_A = np.fft.rfft(Y_Vox_A)

# Frequenzen aus der FFT werden in ein Array über Länge des Signals gepackt
Yf_Klavier = np.fft.rfftfreq(len(Klavier_M), 1 / Abtastrate)
Yf_Vox = np.fft.rfftfreq(len(Vox_M), 1 / Abtastrate)
Yf_Clipping_Vox = np.fft.rfft(Clipping_Vox)      # Clipping wird auch transformiert



# Klirrfaktor mit 1kHz Sinus

# System A

# Ausgang
Y_Sinus_A = [-0.5 / np.tan(x + np.pi / 2)  for x in Sinus_M]      #
FFT_Sinus_A = np.fft.rfft(Y_Sinus_A)          # Ausgang wird Fourier-transformiert

# Frequenzen aus der FFT werden in ein Array gepackt, über Länge des Signals
f = np.fft.rfftfreq(len(Sinus_M), 1 / Abtastrate)

# System B Clipping des Sinussignals bei Amplitude = 0,7
Clipping_Sinus = list()
for x in Sinus_M:
    if x > Clipping_Limit:               # Sobald ein Samplewert x im Signal größer als mein gesetztes Limit ist
        Clipping_Sinus.append(Clipping_Limit)     # wird x = limit gesetzt.
    elif x < -Clipping_Limit:            # Sobald ein Samplewert x im Signal kleiner als mein gesetztes negatives Limit ist
        Clipping_Sinus.append(-Clipping_Limit)    # wird x = -limit gesetzt.
    else:
        Clipping_Sinus.append(x)          # Ansonsten bleibt x = x

FFT_Clipping_Sinus = np.fft.rfft(Clipping_Sinus)     # FFT des Ausgangssignals

System_B = [[-1, -Clipping_Limit, 0, Clipping_Limit, 1], [-Clipping_Limit, -Clipping_Limit, 0, Clipping_Limit, Clipping_Limit]] # Definition der Clipping-Kennlinie

# Klirren System A
k1_A = abs(FFT_Sinus_A[5000])  # Wert der FFT bei 1000 Hz
k2_A = abs(FFT_Sinus_A[10000])  # Wert der FFT bei 2000 Hz
k3_A = abs(FFT_Sinus_A[15000])  # Wert der FFT bei 3000 Hz

# Klirren System B
k1_B = abs(FFT_Clipping_Sinus[5000])  # Wert der FFT bei 1000 Hz
k2_B = abs(FFT_Clipping_Sinus[10000])  # Wert der FFT bei 2000 Hz
k3_B = abs(FFT_Clipping_Sinus[15000])  # Wert der FFT bei 3000 Hz

# Berechnen des Klirrfaktors anhand der FFT Werte bei den harmonischen
kf_A = np.round(100 * np.sqrt( (k2_A**2 + k3_A**2) / (k1_A**2 + k2_A**2 + k3_A**2) ), 2)
kf_B = np.round(100 * np.sqrt( (k2_B**2 + k3_B**2) / (k1_B**2 + k2_B**2 + k3_B**2) ), 2)

# THD
THD_A = np.round(100 * np.sqrt((k2_A**2+k3_A**2)/k1_A**2), 2)
print('THD System A: ' + str(np.round(THD_A, 2)) + ' %' )
print('Klirrfaktor System A: ' + str(np.round(kf_A, 2)) + ' %' )
print('Klirrfaktor System B: ' + str(np.round(kf_B, 2)) + ' %' )

# Skalierung der X-Achse
t_Klavier = np.arange(0, len(Klavier)/Abtastrate, 1/Abtastrate) # Von 0 - Länge des Signals geteilt durch Abtastrate in 1/Abtastrate-Schritten
t_Vox = np.arange(0, len(Vox)/Abtastrate, 1/Abtastrate)

# Plots
fig, axes = plt.subplots(2, 4)
plt.subplots_adjust(wspace=1.0, hspace=0.7)

axes[0, 0].set_title("System A - Kennlinie")
axes[0, 0].set_xlabel("x")
axes[0, 0].set_ylabel("y = -0.5/tan(x+pi/2)")
axes[0, 0].plot(System_A)
axes[0, 0].grid()

axes[1, 0].set_title("System B - Kennlinie")
axes[1, 0].set_xlabel("x")
axes[1, 0].set_ylabel("y(x)")
axes[1, 0].plot(System_B[0], System_B[1])
axes[1, 0].grid()

axes[0, 1].set_title("Vox Eingang")
axes[0, 1].plot(t_Vox, Vox_M)
axes[0, 1].set_xlabel("Zeit (s)")
axes[0, 1].set_ylabel("Amplitude")
axes[0, 1].set_ylim(-1, 1)
axes[0, 1].grid()

axes[1, 1].set_title("Vox Eingang")
axes[1, 1].plot(t_Vox, Vox_M)
axes[1, 1].set_xlabel("Zeit (s)")
axes[1, 1].set_ylabel("Amplitude")
axes[1, 1].set_ylim(-1, 1)
axes[1, 1].grid()

axes[0, 3].set_title("Ausgang f System A")
axes[0, 3].plot(Yf_Vox, 10*np.log10(abs(FFT_Vox_A)))
axes[0, 3].set_xlabel("Frequenzen (Hz)")
axes[0, 3].set_ylabel("Amplitude")
axes[0, 3].grid()

axes[1, 3].set_title("Ausgang f System B")
axes[1, 3].plot(Yf_Vox, 10*np.log10(abs(Yf_Clipping_Vox)))
axes[1, 3].set_xlabel("Frequenzen (Hz)")
axes[1, 3].set_ylabel("Amplitude")
axes[1, 3].grid()

axes[0, 2].set_title("Ausgang Zeit A")
axes[0, 2].plot(t_Vox, Y_Vox_A)
axes[0, 2].set_xlabel("Zeit (sek.)")
axes[0, 2].set_ylabel("Amplitude")
axes[0, 2].set_ylim(-1, 1)
axes[0, 2].grid()

axes[1, 2].set_title("Ausgang Zeit B")
axes[1, 2].plot(t_Vox, Clipping_Vox)
axes[1, 2].set_xlabel("Zeit (sek.)")
axes[1, 2].set_ylabel("Amplitude")
axes[1, 2].set_ylim(-1, 1)
axes[1, 2].grid()

plt.show()