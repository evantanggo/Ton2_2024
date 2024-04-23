# Praxisaufgabe 2
# by Simon Budde, last edit: 23.04.24
# 1. Berechnung der Crest-Faktoren verschiedener deterministischer Signale
# 2. Berechnung der Crest-Faktoren in Tonspuren (Musik, Sprache)
# 3. Berechnung der Energie und des Effektivwertes einer 2-sekündigen Sinusschwingung
# 4. Nachweis der Orthogonalität zweier Sinusschwingungen mit unterschiedlicher Frequenz

# Bibliotheken importieren
import numpy as np
import matplotlib.pyplot as plt
import sounddevice as sd
from scipy import signal
from scipy.io.wavfile import read
import math

# Globale Variablen
fs = 44100
dauer = 2
x_dach = 1
f = 5
delta_t = 1./ fs
t = np.arange(0, dauer, delta_t)

# Deterministische Signale
sinus = np.array(x_dach * np.sin(2 * np.pi * f * t))
dreieck = np.array(x_dach * signal.sawtooth(2 * np.pi * f * t, 0.5))
sägezahn = np.array(x_dach * signal.sawtooth(2 * np.pi * f * t, 1))
rechteck = np.array(x_dach * signal.square(2 * np.pi * f * t))

# Audio-Dateien
Fs, m_data = read('/Users/simonbudde/Desktop/High_and_Dry.wav')
Fs, s_data = read('/Users/simonbudde/Desktop/Peter Pan.wav')
mono_data = (m_data[:,0] + m_data[:,1] / 2)
sono_data = (s_data[:,0] + s_data[:,1] / 2)

musik = np.array(mono_data[:dauer * fs])                    # Datenarray der Audiodatei "Musik"
sprache = np.array(sono_data[:dauer * fs])                  # Datenarray der Audiodatei "Sprache"

type = [['s', 'd', 'sz', 'r', 'm', 'sp'], ["Sinus", "Dreieck", "Sägezahn", "Rechteck", "Musik", "Sprache"],
        [sinus, dreieck, sägezahn, rechteck, musik, sprache]]
order = 0
def count():
    counter = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]       # Anzahl möglicher auswählbarer Signalspuren
    userIp = ""
    ip_message = ("Wie viele Signale möchten Sie wählen?")
    ip_message += "\t"
    while userIp not in counter:                                        # User-Input
        userIp = input(ip_message)
        global order
        order = int(userIp)
    return order

def signalType(order):
    result_array = np.zeros((order, fs * dauer))                # Erstellung eines Ergebnis-Arrays mit entsprechender Größe
    for i in range(order):                                      # Durch-Iterieren der Abfragen zur Wahl eines Signals
        userInput = ""
        input_message = (f"{i+1}. Signal auswählen:"
                         "\n" + type[1][0] + "\t\t [s]"
                         "\n" + type[1][1] + "\t\t [d]"
                         "\n" + type[1][2] + "\t [sz]"
                         "\n" + type[1][3] + "\t [r]"
                         "\n" + type[1][4] + "\t\t [m]"
                         "\n" + type[1][5] + "\t\t [sp]\n")
        input_message += "\nEingabe: \t"
        while userInput.lower() not in type[0]:
            userInput = input(input_message)
        index = type[0].index(userInput)
        print("Deine Auswahl: " + type[1][index] + "\n")
        result_array[i] = type[2][index]                        # Anreihung der Signaldaten an Ergebnis-Array
    return result_array

def plot(result_array):                                         # Darstellung der einzelnen Signale in einem Plot
    plt.figure(figsize=(20, 8))
    for i in range(0, result_array.shape[0]):
        plt.plot(t, result_array[i,:],label=f"Signal {i + 1}")
    plt.xlabel("Time in s")
    plt.ylabel("Amplitude")
    plt.legend()
    plt.grid()
    plt.show()
    return result_array

def operation(result_array):
    signal = np.array(result_array)
    def einzahl_werte(signal):
                                                            # Berechnung des Effektivwertes
        T = len(signal)                                         # Länge des Signals
        signal = np.abs(signal)                                 # Gleichrichtung
        energie = sum(signal ** 2)                              # Summenbildung (numerische Integration) / Energie
        rms = math.sqrt((1 / T) * energie)                      # Wurzel ziehen und normieren
                                                            # Berechnung des Crest-Faktors
        x_top = np.max(signal)                                  # Signalspitze ermitteln
        c = x_top / rms                                         # mit Effektivwert verrechnen
        return rms, c, energie                                  # Ausgabe von Effektivwert & Crest-Faktor & Energie

    for nr in range(0, signal.shape[0]):                        # Iteration
        ergebnis = einzahl_werte(signal[nr,:])
        print(f"Das {nr+1}. Signal hat folgende Werte:\nEffektivwert:"
              f"\t\t{round(ergebnis[0], 3)}\nScheitel-Faktor:\t{round(ergebnis[1], 3)}\n"
              f"Energie:\t\t\t{round(ergebnis[2], 3)}\n")

operation( plot(signalType( count() ) ))                        # Ausführung der Funktionen
# sd.play(musik, fs)
# sd.wait()