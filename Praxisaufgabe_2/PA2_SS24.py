'''
Praxisaufgabe 2
Tontechnik_SS24
'''

import math
from scipy.io.wavfile import read
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import quad
from scipy.signal import correlate

def effektiv_wert(daten):
    T = len(daten)
    daten = daten.astype(np.float64) # in float 
    square = np.square(daten) 
    integral = np.sum(square) 
    eWert = math.sqrt((1 / T) * integral) 
    return eWert

def scheitel_faktor(daten):
    y_max = np.max(daten)
    y_min = np.min(daten)
    aMax = max(y_max, y_min) # Scheitelwert finden. 
    eWert = effektiv_wert(daten)
    c = aMax / eWert
    return c

def aufgabe_1und2(file):  # Crestfaktor berechnen

    Fs, y = read(file)  # Fs = 44100Hz

    # Datei in Mono umwandeln
    if y.ndim == 2:
        y_L = y[:, 0]
        y_R = y[:, 1]
        dataMono = (y_L + y_R) / 2
    else:
        dataMono = y

    #print("Aufgabe 1 / 2")
    print(f"Datei = {file}")
    print(f"Crest Faktor = {scheitel_faktor(dataMono):.2f}")
    print("\n")

# Dateien untersuchen
dateien = ['Praxisaufgabe_2/Piano.wav', 'Praxisaufgabe_2/sprache.wav', 'Praxisaufgabe_2/sinus.wav', 'Praxisaufgabe_2/saegezahn.wav', 'Praxisaufgabe_2/rechteck.wav']



def aufgabe_3():  # Sinusschwingung

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
        energie = sum(y ** 2)

        return energie

    def effektiv_wert(y):
        y = y.astype(np.float64)
        square = np.square(y)
        integral = np.sum(square)
        eWert = math.sqrt((1 / T) * integral)
        return eWert

    print("Aufgabe 3")
    print("Sinusschwingung mit f = 100 Hz und t = 2s")
    print(f"Einzelenergie = {einzel_energie():.2f} Joule")
    print(f"Effektivwert = {effektiv_wert(y):.2f}")


def aufgabe_4():  # Orthogonalität der Sinusschwingungen
    def f1(x, f1):
        return np.sin(2 * np.pi * f1 * x)

    def f2(x, f2):
        return np.sin(2 * np.pi * f2 * x)

    def integrand(x, f1, f2):
        return f1(x, 1.0) * f2(x, 2.0)  # Hier ist f2 = 2 * f1

    result, error = quad(integrand, 0, 1, args=(f1, f2))

    # Runden auf Null, wenn das Ergebnis sehr nah an Null liegt
    if abs(result) < 1e-10:
        result = 0

    print("\n")
    print("Aufgabe 4 (Orthogonalität)")
    print(f"Summer der Integral von beiden Schwingungen ist: {result}")


# Ausführen
if __name__ == "__main__":
    print("Aufgabe 1 / 2")
    for datei in dateien:
        aufgabe_1und2(datei)
    aufgabe_3()
    aufgabe_4()
    
