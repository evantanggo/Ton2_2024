''' PP2 - Panning Verfahren
Gruppe 5
Zia Asmara (2416041) '''

import numpy as np
import soundfile as sf
import sounddevice as sd

def stereo2mono(file_path):
    # Laden der WAV-Datei und Extrahieren der Abtastrate (Fs) und des Signals
    signal, Fs = sf.read(file_path)

    # Falls das Signal stereo ist, in Mono umwandeln
    if signal.ndim == 2:
        signal = np.mean(signal, axis=1)

    # Das Signal auf den Bereich von -1 bis 1 normieren
    signal = signal / np.max(np.abs(signal))
    return Fs, signal

def abspielen(signal, Fs):
    # Das Audio-Signal mit sounddevice abspielen
    sd.play(signal, Fs)
    sd.wait()  # Warten, bis die Wiedergabe beendet ist

def test_datei(prompt):
    check = input(prompt + " (1 für Rosa Rauschen, 2 für Gitarre): ")
    return check.lower() == "2"

# Testsignale laden und normieren
file1 = "pinknoise.wav"
file2 = "gitarre.wav"

Fs1, signal1 = stereo2mono(file1)
Fs2, signal2 = stereo2mono(file2)

def aufgaben(aufgabe, signal, Fs):
    test_signal_2 = test_datei("\n"+ aufgabe.__name__ + " ausführen?")
    if test_signal_2:
        signal = signal2
        Fs = Fs2
    else:
        signal = signal1
        Fs = Fs1

    test = input(aufgabe.__name__ + " wird abgespielt. Soll es fortgesetzt werden? Ja oder Nein? (j/n):")
    if test.lower() == "j":
        aufgabe(signal, Fs)
    else:
        print(aufgabe.__name__ + " übersprungen.")

### Aufgabe Teil A: Laufzeitdifferenzen zwischen L und R ###
def teil_a(signal, Fs):
    t_ms = round(2 / 1000 * Fs)   # Zeitdifferenz von 0,2 ms in Array-Länge umgerechnet
    extra = np.zeros(t_ms, dtype=int)

    # Links verzögert, dadurch wird es rechts wahrgenommen
    links_a = np.append(extra, signal)
    rechts_a = np.append(signal, extra)
    stereo_a = np.vstack((links_a, rechts_a)).transpose()
    abspielen(stereo_a, Fs)

### Aufgabe Teil B: Pegeldifferenzen zwischen L und R ###
def teil_b(signal, Fs):
    # Links leiser stellen (75% Reduzierung entspricht etwa -8 dB links und 0 dB rechts)
    faktor = 2.5  # Faktor = 10^(8/20) (75% entspricht ca. 8 dB Unterschied)

    links_b = signal / faktor
    rechts_b = signal

    stereo_b = np.vstack((links_b, rechts_b)).transpose()
    abspielen(stereo_b, Fs)

### Aufgabe Teil C: Zusammenhang zwischen Reglerstellung und Kanaldämpfung
def teil_c(signal, Fs):
    t_ms = round(2 / 1000 * Fs)   # Zeitdifferenz von 0,2 ms in Array-Länge umgerechnet
    extra = np.zeros(t_ms, dtype=int)

    faktor = 2.5  # Faktor = 10^(8/20) (75% entspricht ca. 8 dB Unterschied)

    links_c = np.append(extra, signal)
    rechts_c = np.append(signal, extra) / faktor
    stereo_c = np.vstack((links_c, rechts_c)).transpose()
    abspielen(stereo_c, Fs)

### Aufgabe Teil D:  Ermittlung der Laufzeitdifferenz zwischen den Kanälen ###
def teil_d(signal, Fs):
    delta_t = round(5 / 1000 * Fs)  # 5 ms Schritte
    i = 0
    for i in range(0, 10):
        extra = np.zeros(delta_t * i, dtype=int)
        links_d = np.append(extra, signal)
        rechts_d = np.append(signal, extra)
        # Verkürzung der Arrays, um nicht immer 10 Sekunden zu hören
        links_d_kurz = links_d[:Fs * 5]
        rechts_d_kurz = signal[:Fs * 5]
        stereo_d = np.vstack((links_d_kurz, rechts_d_kurz)).transpose()
        abspielen(stereo_d, Fs)

        check = input("Sind zwei Einzelsignale zu erkennen? (0/1): ")
        if check == "1":
            time = round(delta_t * i / Fs * 1000)
            print("Die Laufzeitdifferenz zwischen den Kanälen beträgt:", time, "ms")
            break
        elif check == "0":
            i += 1
            print("Laufzeitdifferenz wird erhöht.")
        else:
            print("Ungültige Eingabe. Erlaubte Eingabewerte: 0 oder 1")
            print("Die Laufzeitdifferenz ist unverändert.")
        i = i + 1

### Aufgabe Teil E: Automatische Signalwanderung von links nach rechts ###
def teil_e(signal, Fs):
    if len(signal) / Fs > 5:  # Das Signal muss mindestens 5 Sekunden lang sein
        i = 0
        j = 10
        links_e = np.array([], dtype=float)
        rechts_e = np.array([], dtype=float)

        while i <= 5:
            links = signal[Fs * i: Fs * (i + 1)] * (0.1 * j)
            rechts = signal[Fs * i: Fs * (i + 1)] * (0.1 * i)
            links_e = np.append(links_e, links)
            rechts_e = np.append(rechts_e, rechts)
            i += 1
            j -= 1

        stereo_e = np.vstack((links_e, rechts_e)).transpose()
        abspielen(stereo_e, Fs)

def main():
    teil_aufgaben = [teil_a, teil_b, teil_c, teil_d, teil_e]

    for task_func in teil_aufgaben:
        aufgaben(task_func, signal1, Fs1)

if __name__ == "__main__":
    main()