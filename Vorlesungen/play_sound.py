import matplotlib.pyplot as plt  # grafische Darstellung
import numpy as np  # Array-Verarbeitung
#import winsound  # Sound-Ein- und Ausgabe unter Windows
import sounddevice as sd  # Plattformunabhängige Sound-Ein- und Ausgabe
from scipy.io.wavfile import read  # Lesen von wav-Datei
from scipy.io.wavfile import write  # Schreiben in wav-Datei
import time  # Timer-Funktionen, Pause einfügen

# -----------
Fs = 10000  # Abtastfrequenz, Fs >= 2*fmax
# Üblich in der Audiotechnik: Fs = 44100 Hz
f = 300  # Signalfrequenz
y_dach = 1  # Amplitude (ist Maximalwert für Wiedergabe mit sounddevice)
dauer = 3  # Dauer in sec.
deltat = 1. / Fs  # Ts; Schrittweite für Signalerzeugung.
# Der . hinter der 1 zeigt Python, dass es ein float-Wert
# ist (bei 1/Fs wird Integer angenommen, dh. auf ganze
# Zahlen gerundet.


# -------------
# Sinus erzeugen:
t = np.arange(0, dauer, deltat)  # Zeit-Werte
# Nomenklatur: np.arange(Startwert, Stopwert, Schrittweite)

# print(len(t))        #Anzahl t_i-Werte (bei Interesse ausgeben lassen)

y = y_dach * np.sin(2 * np.pi * f * t)  # Sinusschwingung,
# y ist ein array, weil t ein array ist
# direkte Ausgabe des Arrays als Audiosignal, dazu Amplitude normiert auf 1
print("sd.play:")
sd.play(y / np.abs(np.max(y)), Fs)  # abspielen des arrays als Sound
sd.wait()  # Python-Interpreter hält an, bis der Sound zu Ende abgespielt wurde
# (https://python-sounddevice.readthedocs.io/en/0.4.2/usage.html)

time.sleep(1)  # 1 sec. Pause (https://realpython.com/python-sleep/)

# -----------------
##- Speichern array als wav-Signal, dazu umwandeln in Wertebereich: 16 Bit Integer
y2 = y / np.max(y)  # normieren auf 1
y2 = y2 * (np.power(2, 15) - 1)  # 2 hoch 15 - 1 --> ein Bit für Vorzeichen, null ist extra
b = np.array(y2, dtype=np.int16)

write('test.wav', int(Fs), b)  # Schreiben in Datei (scipy.io.wavfile schreibt Integer-Werte in Datei,
# höchster Wert ist (2^15)-1
# dies geschieht mit "write" aus scipy.io.wavfile

# -- Wiedergeben array aus File
#print("winsound.PlaySound: ")

###################
# -Einlesen aus Audiodatei
(Fs1, y1) = read('test.wav')  # auslesen der Dateiinformationen als Audiosignal
# dies geschieht mit "read" aus scipy.io.wavfile

deltat1 = 1.0 / Fs1
t1 = np.arange(0, dauer, deltat1)  # Zeit-Werte

######################
##
##  Grafische Darstellung
##
######################
fig, (ax1, ax2) = plt.subplots(nrows=2)  # Vorbereitung für zwei Plots
plt.subplots_adjust(left=None, bottom=None, right=None, top=None,
                    wspace=None, hspace=0.5)  # Abstand zwischen Subplots

# erste Grafik:
ax1.plot(t, y, '.')  # Plotten von y über t
ax1.set_ylim(-1 * y_dach, y_dach)  # Grenzen der y-Achse
ax1.set_xlim(0, 2 / f)  # Grenzen der x-Achse
ax1.set_xlabel('$n \cdot T_s$ in s')  # Beschriftung x-Achse, $x$ stellt x kursiv dar
ax1.set_ylabel('$y$($n T_s$)')  # Beschriftung y-Achse
ax1.set_title('$y$ = $\hat{y}$ $\cdot$ sin (2 $\pi$ $f$ $n$ $T_s$)')
ax1.grid(True)

## zweite Grafik:
# ax2.plot(t1, y1, '.')  # Plotten von y1 über t1
# ax2.set_ylim(-1 * np.max(y1), np.max(y1))  # Grenzen der y-Achse
# ax2.set_xlim(0, 2 / f)  # Grenzen der x-Achse
plt.show()

