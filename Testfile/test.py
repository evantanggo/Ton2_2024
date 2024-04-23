import numpy as np
import math

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

    def einzel_energie(y):
        energie = np.sum(y ** 2)
        return energie

    def effektiv_wert(y):
        y = y.astype(np.float64)
        square = np.square(y)
        integral = np.sum(square)
        eWert = math.sqrt((1 / T) * integral)
        return eWert

    print("Aufgabe 3")
    print("Sinusschwingung mit f = 100 Hz und t = 2s")
    print(f"Einzelenergie = {einzel_energie(y):.2f} Joule")
    print(f"Effektivwert = {effektiv_wert(y):.2f}")

aufgabe_3()
