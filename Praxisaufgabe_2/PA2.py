'''
Praxisaufgabe 2
Einzelwerte von Signalen
'''


import math
from scipy.io.wavfile import read
import numpy as np
import matplotlib.pyplot as plt

def aufgabe_1und2():  # Crestfaktor berechnen

    file = 'sägezahn_440Hz_mono_3s.wav'  # Dateinamen anpassen, um file zu ändern
    Fs, y = read(file)  # Fs = 44100Hz

    if y.ndim == 2:
        y_L = y[:, 0]
        y_R = y[:, 1]
        dataMono = (y_L + y_R) / 2
    else:
        dataMono = y

    T = len(dataMono)

    def effektiv_wert(daten):
        daten = daten.astype(np.float64)
        square = np.square(daten)
        integral = np.sum(square)
        eWert = math.sqrt((1 / T) * integral)
        return eWert

    def scheitel_faktor(effektivWert):
        y_max = np.max(dataMono)
        y_min = np.min(dataMono)
        aMax = max(y_max,y_min)
        c = aMax / effektivWert
        return c

    print("Aufgabe 1 / 2")
    print(f"Datei = ", file)
    #print(f"Effektivwert = ", effektiv_wert(dataMono))
    print(f"Crest Faktor = ", scheitel_faktor(effektiv_wert(dataMono)))
    print("\n")


def aufgabe_3(): # Sinusschwingung

    Fs = 44100  # Abtastfrequenz, Fs >= 2*fmax
    f = 100  # Signalfrequenz
    y_dach = 1  # Amplitude (ist Maximalwert für Wiedergabe mit sounddevice)
    dauer = 2  # Dauer in sec.
    deltat = 1. / Fs  # Ts; Schrittweite für Signalerzeugung.

    # Sinus erzeugen:
    t = np.arange(0, dauer, deltat)  # Zeit-Werte
    T = len(t)
    y = y_dach * np.sin(2 * np.pi * f * t)  # Sinusschwingung

    def einzel_energie():
        energie = sum(y**2)

        return energie

    def effektiv_wert(y):
        y = y.astype(np.float64)
        square = np.square(y)
        integral = np.sum(square)
        eWert = math.sqrt((1 / T) * integral)
        return eWert

    print("Aufgabe 3")
    print("Sinusschwingung mit f = 100 Hz und t = 2s")
    print(f"Einzelenergie = ", einzel_energie(), "Joule")
    print(f"Effektivwert = ", effektiv_wert(y))

def aufgabe_4():

    Fs = 44100  # Abtastfrequenz, Fs >= 2*fmax
    f = 100  # Signalfrequenz
    y_dach = 1  # Amplitude (ist Maximalwert für Wiedergabe mit sounddevice)
    dauer = 2  # Dauer in sec.
    deltat = 1. / Fs  # Ts; Schrittweite für Signalerzeugung.

    # 1.Sinus erzeugen:
    t = np.arange(0, dauer, deltat)  # Zeit-Werte
    T = len(t)
    y = y_dach * np.sin(2 * np.pi * f * t)  # Sinusschwingung

    # 2. Sinus erzeugen:
    n = 2 # für verschiedene Frequenzen

    t1 = np.arange(0, dauer, deltat)  # Zeit-Werte
    T1 = len(t)
    y1 = y_dach * np.sin(2 * np.pi * n * f * t)  # Sinusschwingung

    fig, (ax1) = plt.subplots(nrows=1)  # Vorbereitung für zwei Plots
    plt.subplots_adjust(left=None, bottom=None, right=None, top=None,
                        wspace=None, hspace=0.5)  # Abstand zwischen Subplots

    # erste Grafik:
    ax1.plot(t, y, t1,y1,'.')  # Plotten von y über t
    ax1.set_ylim(-1 * y_dach, y_dach)  # Grenzen der y-Achse
    ax1.set_xlim(0, 2 / f)  # Grenzen der x-Achse
    ax1.set_xlabel('$n \cdot T_s$ in s')  # Beschriftung x-Achse, $x$ stellt x kursiv dar
    ax1.set_ylabel('$y$($n T_s$)')  # Beschriftung y-Achse
    ax1.set_title(f"Sinus mit {f} und {n*f} Hz")
    #ax1.set_title('$y$ = $\hat{y}$ $\cdot$ sin (2 $\pi$ $f$ $n$ $T_s$)')
    ax1.grid(True)
    plt.show()


# Ausführen
aufgabe_1und2()
aufgabe_3()
aufgabe_4()



