# author: @SimonBudde
# group: 12
# created: 2024-09-05
# last edit: 2024-06-09

"""----------------------------------------------------------------
Praxisproblem 1 (von 3)
Tontechnik 2 (SoSe 2024)
Medientechnik (B.Sc.), HAW Hamburg

Fallstudie (Prüfungsleistung)
Dozentin: Frau Prof. Dr.-Ing. Eva Wilk

Für eine Raumimpulsantwort werden verschiedene Parameter berechnet,
um Aufschluss über die Raumeigenschaften zu erhalten.
----------------------------------------------------------------"""

import numpy as np
from scipy.io.wavfile import read
from scipy import signal as consig
from scipy.sparse import data
import matplotlib.pyplot as plt
import warnings
import os
#import librosa
import math
import sounddevice as sd
from scipy.fft import fft, fftfreq

base_dir = os.path.dirname(os.path.abspath(__file__))                       # Gesamtpfad in Dateiname konvertieren
data = ["Datei_B.wav", "Test-Impulsantwort.wav",                    # Dateien-Array erstellen
        "Sprache.wav", "Musik.wav"]
data = [os.path.join(base_dir, datei) for datei in data]                    # Pfade der Dateien in neues Array schreiben

# Funktionen für den Import, das Abschneiden und Einfaden des Signals
def import_file(file_path):
    try:
        # Datei einlesen
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            sample_rate, audio_data = read(file_path)                       # Abtastrate & Datenarray auslesen

        if audio_data.ndim == 2:                                            # Datei in Mono umwandeln, wenn Stereo
            left_channel = audio_data[:, 0]
            right_channel = audio_data[:, 1]
            mono_data = (left_channel + right_channel) / 2
        else:
            mono_data = audio_data

        max_amp = np.max(np.abs(mono_data))                                 # Signal auf höchsten Betragswert normalisieren
        mono_data_normalized = mono_data / max_amp

        return mono_data_normalized, sample_rate

    except Exception as e:
        print(f"Fehler beim Importieren der Daten aus {file_path}: {str(e)}")
        return None, None

def cut_signal(signal):
    y, fs = signal
    start = np.argmax(np.abs(y))                        # Suche nach höchstem Betragswert des Signals
    fade_seq = y[start-10:start]                        # Definition der Samples für das Fading, hier: n = 10
    g = fade_in(fade_seq)                               # Ausführung der Fade-Funktion
    y_s = np.append(g, y[start:-1], axis=None)          # Zusammensetzen von Fade-Sequenz und restlicher Impulsantwort

    cutsignal = build_tuple(y_s, fs)                    # Signal in gemeinsames Array aus Samples + Samplerate umwandeln
    return cutsignal

def fade_in(signal):
    fader = np.arange(0, 1, 1 / len(signal))            # Lineares Fading-Array definieren
    f_signal = signal * fader                           # Multiplikation des Signals mit dem linearen Fader
    return f_signal

def build_tuple(data, fs):                              # Daten und Abtastrate zusammenführen
    return data, fs

def info(signal):
    y, fs = signal
    print(f"\nInfos\nAbtastfrequenz:\t\t{fs}\n"                  # Informationen zum Signal ausgeben
          f"Abtastwerte:\t\t{len(y)}\n"
          f"Dauer in s:\t\t\t{round(len(y)/fs, 2)}\n")

# Plot-Funktionen
def waveform_plot(signal):
    y, fs = signal
    duration = len(y) / fs                              # Dauer des Signals in Sekunden definieren
    time = np.linspace(0, duration, len(y))         # Numpy-Array mit linearen Zeitwerten definieren

    # Plot der Impulantwort
    plt.figure()
    plt.plot(time, y, color='red')
    plt.xlabel('Zeit in s')
    plt.ylabel('Amplitude normalisiert')
    ax = plt.gca()
    ax.set_ylim([-1, 1])
    plt.title('Impulsantwort h(t)')
    plt.grid()
    plt.show()

def fft_plot(signal):
    y, fs = signal
    y_1 = np.fft.fft(y)                             # Fourier-Transformation des Eingangssignals
    y_2 = np.fft.fftshift(np.abs(y_1))              # Shifting & Betragswerte für verbesserte Darstellung
    y_3 = y_2 / np.max(y_2)                         # Normierung der Werte auf 1

    f0 = int(len(y_3) / 2)                          # Index der ersten positiven Frequenz finden
    y_4 = y_3[f0:]                                  # Begrenzung des Spektrums auf positive Frequenzen
    freq = np.arange(0, len(y_4), 1)

    plt.figure()
    plt.plot(freq, y_4, color='green', label='H(t)')
    plt.xscale('log')                               # Setze die x-Achse logarithmisch
    plt.yscale('log')                               # Setze die y-Achse logarithmisch
    plt.xlim([20, fs/2])                            # Frequenz-Grenzen bis zur halben Abtastrate setzen
    plt.ylim([0.001, 1])                            # Normalisierter Bereich
    plt.xticks([20, 100, 1000, 10000, 20000])
    plt.xlabel('Frequenz in Hz')
    plt.ylabel('Amplitude in dB')
    plt.title('Amplitudenfrequenzgang H(t)')
    plt.grid()
    plt.show()

def spektogramm_plot(signal):
    y, fs = signal

    fig, axs = plt.subplots(1, 1)
    Pxx, freqs, bins, im = axs.specgram(y, NFFT=1024, Fs=fs, noverlap=900)          # Ausführen der Spektogramm-Funktion
    plt.title('Spektogramm')
    plt.xlabel('Zeit in Sekunden')
    plt.ylabel('Frequenz in Hertz')
    plt.show()

def schroeder_plot(signal):
    y, fs = signal
    duration = len(y) / fs
    time = np.linspace(0, duration, len(y))

    frame_energie = []
    for i in range(len(y)):                                             # Energieberechnung durch Rückwärts-Integration
        log_data = np.sum(np.square(y[i:-1]))                           # Quadrierung der Werte und Summenbildung (numerische Integration)
        frame_energie.append(log_data + 1e-20)                          # Minimalen Wert addieren, um "Division by Zero" zu vermeiden
    L_gesamt = np.max(np.abs(frame_energie))                            # Gesamtenergie = größte "Frame-Energie"
    L = 10 * np.log10(frame_energie / L_gesamt)                         # Werte in dB

    # Berechnung und Ausgabe von Deutlichkeitsmaß C50 & Klarheitsmaß C80
    lim50 = int(fs * 0.05)                                                      # Index-Limit für C50 setzen
    lim80 = int(fs * 0.08)                                                      # Index-Limit für C80 setzen
    energie = np.square(y)                                                      # Momentan-Energie berechnen
    C50 = 10 * np.log10( np.sum(energie[:lim50]) / np.sum(energie[lim50:]))     # C50 durch logarithmierte Verhältnisrechnung
    C80 = 10 * np.log10( np.sum(energie[:lim80]) / np.sum(energie[lim80:]))     # C80 durch logarithmierte Verhältnisrechnung

    # Berechnung der Zeitpunkte und exakten Energiepegel für -5dB, -15dB, -25dB und -35dB
    T0 = min(min(np.where(L <= -5.0)))                                          # Zeitindizes finden
    T1 = min(min(np.where(L <= -15.0)))
    T2 = min(min(np.where(L <= -25.0)))
    T3 = min(min(np.where(L <= -35.0)))
    L0 = L[T0]                                                                  # Zugeordnete Energie-Werte definieren
    L1 = L[T1]
    L2 = L[T2]
    L3 = L[T3]

    # Berechnung der Nachhallzeiten T10, T20 und T30
    T10 = -60 * (((T1 - T0) / fs) / (L1 - L0))                                  # Nachhallzeit aus Geradensteigung berechnen
    T20 = -60 * (((T2 - T0) / fs) / (L2 - L0))
    T30 = -60 * (((T3 - T0) / fs) / (L3 - L0))
    list_str = ['T10', 'T20', 'T30']                                            # String-Liste für Print-Ausgabe erstellen
    list_float = [round(T10, 2), round(T20, 2), round(T30, 2)]                  # Werte-Liste erstellen


    # Geraden-Arrays für die Nachhallzeiten
    idx10 = int(T10 * fs) + 1                                   # Index zum Zeitpunkt der erreichten Nachhallzeit suchen
    idx20 = int(T20 * fs) + 1
    idx30 = int(T30 * fs) + 1
    g10 = np.linspace(L0, -60, idx10 - T0)                      # Zeit-Array für Gerade der Nachhallzeit erstellen
    g20 = np.linspace(L0, -60, idx20 - T0)
    g30 = np.linspace(L0, -60, idx30 - T0)

    # Plot der Geraden für T10, T20 und T30
    plt.figure()
    plt.plot(time[T0:idx10], g10, color='darkorange', label='T10 = {:.2f}s'.format(T10), linestyle=':', linewidth='1.5')
    plt.plot(time[T0:idx20], g20, color='fuchsia', label='T20 = {:.2f}s'.format(T20), linestyle=':', linewidth='1.5')
    plt.plot(time[T0:idx30], g30, color='darkcyan', label='T30 = {:.2f}s'.format(T30), linestyle=':', linewidth='1.5')

    # Marker für Nachhallzeiten setzen
    plt.scatter([T10], [-60], s=40, marker='x', color='darkorange')
    plt.scatter([T20], [-60], s=40, marker='x', color='fuchsia')
    plt.scatter([T30], [-60], s=40, marker='x', color='darkcyan')

    # Graph plotten, Legende, Beschriftung etc.
    plt.plot(time, L, color='blue')
    plt.title('Schroeder-Plot L(t)')
    plt.legend(loc='upper right')
    plt.xlabel("Zeit in Sekunden")
    plt.ylabel("L in dB")
    plt.ylim(-80, 5)
    plt.grid()
    plt.show()

    # Print-Ausgabe der errechneten Parameter
    print('Nachhallzeiten\nT10:\t\t\t\t\t {:.2f}s'.format(T10),
            '\nT20:\t\t\t\t\t {:.2f}s'.format(T20),
            '\nT30:\t\t\t\t\t {:.2f}s'.format(T30) )
    print('\nDeutlichkeitsmaß C50:\t {:.2f}dB'.format(C50),'\nKlarheitsmaß C80:\t\t {0:.2f}dB'.format(C80))

    # Abfrage eines Zeitpunktes für die Korrelationsberechnung
    cut_val = float(input(  '\nKorrelationsberechnung:'
                            '\nFließkommazahl des Zeitpunktes, an dem die Energiepegel-Kennlinie '
                            '\ngerade noch parallel zu den Nachhallzeiten-Geraden verläuft:  '))
    cut_idx = int(cut_val * fs) + 1                                     # Konvertierung des Zeitwertes in einen Index

    # Berechnung der Differenz der jeweiligen Nachhallzeit mit dem Energie-Pegel
    diff_array = (  L[T0:idx10] - g10,
                    L[T0:idx20] - g20,
                    L[T0:idx30] - g30  )

    diff_array = [d[:cut_idx] for d in diff_array]                      # Abschneiden auf kürzeste Nachhallzeit für Vergleich
    abs_diff_array = [[abs(val) for val in d] for d in diff_array]      # Betragsbildung als Vorbereitung auf Integration
    korr_value = [np.sum(d) for d in abs_diff_array]                    # Numerische Integration, um "Fläche unter der Kurve" zu ermitteln
    korr_idx = np.argmin(korr_value)                                    # Finden des geringsten Wertes

    # Differenz-Kennlinie für T10, T20 & T30
    plt.figure()
    plt.plot(time[T0:cut_idx], abs_diff_array[0][:cut_idx-T0], color='r', label='L - T10')
    plt.plot(time[T0:cut_idx], abs_diff_array[1][:cut_idx-T0], color='y', label='L - T20')
    plt.plot(time[T0:cut_idx], abs_diff_array[2][:cut_idx-T0], color='b', label='L - T30')
    plt.xlabel('Zeit in Sekunden')
    plt.ylabel('Differenz zu L ')
    plt.title('Differenzkennlinie als Vergleich von T10, T20 und T30 in Bezug zum Energiepegel L')
    plt.grid()
    plt.legend()
    plt.show()

    print(f'\n--> Die beste Näherung ergibt sich für '
          f'{list_str[korr_idx]} = {list_float[korr_idx]}s.\n')

    return None

# Faltungsfunktion
def convolve(signal1, signal2):
    a, fsa = signal1                                    # Import von Signal 1
    b, fsb = signal2                                    # Import von Signal 2
    if fsa == fsb:                                      # If-Abfrage, ob gleiche Abtastrate
        y_conv = 0.02 * consig.fftconvolve(a, b)        # Faltungsoperation mit Amplitudendämpfung für Wiedergabe
        sd.play(y_conv)                                 # Abspielen des gefalteten Signals
        sd.wait()
    else:
        print("\nDie Signale haben nicht die gleiche Abstastfrequenz.\nFaltung wird nicht ausgeführt!")
    return None

if __name__ == "__main__":
    h = cut_signal(import_file(data[0]))                # Import der Impulsantwort_B
    h_test = cut_signal(import_file(data[1]))           # Import der Test-Impulsantwort
    sprache = import_file(data[2])                      # Import eines Test-Signals mit Sprache
    musik = import_file(data[3])                        # Import eines Test-Signals mit Musik

    info(h_test)                                             # Ausgabe von Informationen zur Impulsantwort
    waveform_plot(h_test)                                    # Waveform-Darstellung der Impulsantwort
    fft_plot(h_test)                                         # Amplitudenfrequenzgang der Impulsantwort
    spektogramm_plot(h_test)                                 # Spektogramm-Darstellung der Impulsantwort
    schroeder_plot(h_test)                                   # Schroeder-Plot & Berechnungen für Nachhallzeit, C50, C80
    #convolve(h, musik)                                  # Faltung der Impulsantwort mit dem Musik-Signal