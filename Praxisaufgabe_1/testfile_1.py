import numpy as np
import sounddevice as sd
import time
import matplotlib.pyplot as plt

# Definitionen
fs = 44100  # Abtastfrequenz
sek = 1  # Zeit
t = np.linspace(0, sek, fs * sek)  # Array von 0 bis "sek" über Abtastwerte
dBref = 0  # Referenzwert Pegel
FreqList = [20, 40, 80, 125, 250, 500, 1000, 2000, 4000, 8000, 12000, 16000, 19000]  # Liste der zu testenden Frequenzen
Results = np.empty(13)  # Leeres Array mit 13 Stellen für zu testende Frequenzen
# for-Schleife für die Amplitude der Referenzschwingung

for i in range(20):
    sd.stop()  # Anhalten gespielter Ton
    dB = 100 - 5 * i  # Pegel-Veränderung in 5-er Schritten
    a = pow(10, -dB / 20)  # Berechnen der Amplitude
    rad = 2 * np.pi * 1000 * t  # Berechnung des Sinusinhalts mit f = 1000 Hz
    sine = a * np.sin(rad)  # Erstellung des Sinus
    sd.play(sine, fs / sek)  # Abspielen des Sinus-Tons
    time.sleep(1)  # Delay zwischen den Durchläufen der Schleife
    in_string = input("Press Enter to continue, S to stop")
    if in_string.lower() == "s":  # Wenn ein Knopf gedrückt wird...(Nutzereingabe)
        print("1000 Hz |", -dB, "dB")  # Ausgabe der Werte
        dBref = dB  # Festlegen des Referenzwertes
        break  # Unterbrechen der Schleife

# for-Schleife für die Frequenzänderung
for j in range(13):
    if j != 6:  # Ausschluss der zuvor gemessenen Frequenz 1000 Hz
        freq = FreqList[j]  # Auswahl der Frequenz aus dem Array
        rad = 2 * np.pi * freq * t  # Erstellung des Sinusinhalts
        for i in range(23):  # for-Schleife ür die Amplitude
            sd.stop()  # Anhalten gespielter Ton
            dB = 100 - 5 * i  # Pegelveränderung in 5-er Schritten
            if i >= 18:  # Unterscheidung der dB-Werte, falls dB = -5...
                dB = 23 - i  # dB in 1-er Schritten
            a = pow(10, -dB / 20)  # Berechnen der Amplitude
            sine = a * np.sin(rad)  # Erstellung des Sinus
            sd.play(sine, fs / sek)  # Abspielen des Sinus-Tons
            time.sleep(1)  # Delay zwischen den Durchläufen der Schleife
            in_string = input("Press Enter to continue, S to stop")
            if in_string.lower() == "s":  # Wenn ein Knopf gedrückt wird...(Nutzereingabe)
                print("1000 Hz |", -dB, "dB")  # Ausgabe der Werte
                dBref = dB  # Festlegen des Referenzwertes
                break  # Unterbrechen der Schleife
            # Falls 0 dB erreicht werden...
            if i == 22:
                print(freq, "Hz", "|", "inaudible")  # Print Rückmeldung

# Plotten der Grafischen Darstellung
plt.plot(FreqList, Results, 'b', label='Hörschwelle')
plt.plot(FreqList, Results, 'ko')  # Schwarze Punkte zur Orientierung
plt.title('Hörschwelle')  # Titel
plt.xlabel('Frequenz [in Hz]')  # X-Achsenbeschriftung (Frequenz)
plt.xscale('log')  # Logarithmische Skalierung der x-Achse
plt.ylabel('Hörschwelle [in dB]')  # Y-Achsenbeschriftung (Pegel)
plt.grid()  # Rastergitter
plt.show()  # Anzeigen des Plots
