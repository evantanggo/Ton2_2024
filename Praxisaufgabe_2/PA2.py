'''
Praxisaufgabe 2
Tontechnik_WS23
'''

import math
from scipy.io.wavfile import read
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import quad
from scipy.signal import correlate


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
        aMax = max(y_max, y_min)
        c = aMax / effektivWert
        return c

    print("Aufgabe 1 / 2")
    print(f"Datei = ", file)
    # print(f"Effektivwert = ", effektiv_wert(dataMono))
    print(f"Crest Faktor = ", scheitel_faktor(effektiv_wert(dataMono)))
    print("\n")


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
    print(f"Einzelenergie = ", einzel_energie(), "Joule")
    print(f"Effektivwert = ", effektiv_wert(y))


def aufgabe_4():  # Orthogonalität der Sinusschwingungen
    def f1(x, f1):
        return np.sin(2 * np.pi * f1 * x)

    def f2(x, f2):
        return np.sin(2 * np.pi * f2 * x)

    def integrand(x, f1, f2):
        return f1(x, 1.0) * f2(x, 2.0)  # Hier ist f2 = 2 * f1

    result, error = quad(integrand, 0, 1, args=(f1, f2))

    print("\n")
    print("Aufgabe 4 (Orthogonalität)")
    print(f"Summer der Integral von beiden Schwingungen ist: {result}")


def aufgabe_5():
    def file1():

        file = '21_Piano2.wav'  # um file zu ändern Dateinamen anpassen
        (Fs, y) = read(file)  # Fs = 44100Hz

        if y.ndim == 2:  # überprüft, ob die Datei Stereo oder Mono ist und rechnet sie in Mono um
            y_L = y[:, 0]
            y_R = y[:, 1]
            dataMono = (y_L + y_R) / 2
        else:
            dataMono = y

        return dataMono

    def file2():

        file = '45_VoxSFX4.wav'  # um file zu ändern Dateinamen anpassen
        (Fs, y) = read(file)  # Fs = 44100Hz

        if y.ndim == 2:  # überprüft, ob die Datei Stereo oder Mono ist und rechnet sie in Mono um
            y_L = y[:, 0]
            y_R = y[:, 1]
            dataMono1 = (y_L + y_R) / 2
        else:
            dataMono1 = y

        return dataMono1


    def calculate_energy(signal):
        signal = signal.astype(np.float64)
        square = np.square(signal)  # quadrieren
        integral = sum(square)  # summiert alle Werte des Arrays

        return integral

    def calculate_total_energy(signal1, signal2):
        return calculate_energy(signal1) + calculate_energy(signal2)

    def calculate_correlation_factor(signal1, signal2):
        correlation = correlate(signal1, signal2, mode='full')
        max_correlation = np.max(correlation)
        energy_product = calculate_energy(signal1) * calculate_energy(signal2)
        return max_correlation / np.sqrt(energy_product)


    individual_energy1 = calculate_energy(file1())
    individual_energy2 = calculate_energy(file2())
    total_energy = calculate_total_energy(file1(), file2())
    correlation_factor = calculate_correlation_factor(file1(), file2())

    print("\n")
    print("Aufgabe 5")
    print(f'Individual Energy 1: {individual_energy1}')
    print(f'Individual Energy 2: {individual_energy2}')
    print(f'Total Energy: {total_energy}')
    print(f'Correlation Factor: {correlation_factor}')

# Ausführen
if __name__ == "__main__":
    aufgabe_1und2()
    aufgabe_3()
    aufgabe_4()
    aufgabe_5()
