"""
Teil 1 (Filter) wurde von Murad Zeynalli (Tiefpass) und
Pascal Nikiema (Hochpass) programmiert und kommentiert. Ein Weißes Rauschen
wurde als Testsignal verwendet. Die geforderten Kurven sind je nach gewähltem Filter
sichtbar.
-------
Teil 2 (DELAY) berechnet aus einer WAV-Datei den C50 und C80 Wert
Dieser code wurde von Marten Klein und Sönke Marquardt geschrieben und Kommentiert.
Der gesamte Code wurde von Pascal Nikiema zusammengeführt. Es kann direkt in der
Konsole direkt ausgewählt werden, welchen Audioeffekt man anwenden möchte.
--------
*Prüfungsgruppe 5*
19.07.2024
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.io.wavfile import read, write
import wave
import os


# Generiere ein Weißes Rauschen Signal
def generate_white_noise(length, fs):
    """
    Generiert ein Stereo-White-Noise-Signal mit einstellbarer Lautstärke
    :param length: Länge des Signals in Sekunden
    :param fs: Abtastrate (Sampling-Rate) in Hz
    :return: White-Noise-Signal (numpy array)
    """
    num_samples = int(length * fs)
    white_noise = np.random.randn(num_samples)
    white_noise = white_noise / max(abs(white_noise))  # Normalisierung des Signals
    return white_noise


def write_wave(file, sound, fs):
    """
    Schreibt ein Audiosignal und die Parameter in eine WAV-Datei.
    :param file: Pfad zur WAV-Datei
    :param sound: Audiosignal als Numpy-Array
    :param fs: Abtastrate des Audiosignals
    """
    with wave.open(file, 'wb') as wf:
        wf.setnchannels(1)  # Mono
        wf.setsampwidth(2)  # 16 bits
        wf.setframerate(fs)
        wf.writeframes(sound.tobytes())  # Schreibt die Frames in die WAV-Datei


def echo(audio_signal, delay, level, framerate):
    """
    Diese Echo funktion wurde von Sönke Marquardt geschrieben und kommentiert.
    Erzeugt ein Echo-Effekt auf einem Audiosignal.
    Erzeugt ein Echo-Effekt auf einem Audiosignal.
    :param audio_signal: Eingangs-Audiosignal als NumPy-Array
    :param delay: Verzögerungszeit für das Echo in Sekunden
    :param level: Laustärke für das Echo
    :param framerate: Abtastrate des Audiosignals
    :return: Audiosignal mit Echo-Effekt als NumPy-Array
    """
    dly_samples = int(framerate * delay)  # Berechnet die Verzögerung in Samples
    echo_signal = np.zeros(len(audio_signal) + dly_samples)  # Erzeugt ein leeres Array
    echo_signal[:len(audio_signal)] = audio_signal  # Kopiert das Originalsignal in das Echo-Array
    echo_signal[dly_samples:] += level * audio_signal  # Fügt das verzögerte Echo hinzu
    return echo_signal / np.max(np.abs(echo_signal)) * 32767  # Normalisierung und Konvertierung in int16


def reversed_echo(audio_signal, delay, level, framerate):
    """
    Diese reversed_Echo funktion wurde von Sönke Marquardt geschrieben und kommentiert.
    Erzeugt einen umgekehrten Echo-Effekt auf einem Audiosignal.
    :param audio_signal: Eingangs-Audiosignal als NumPy-Array
    :param delay: Verzögerungszeit für das Echo in Sekunden
    :param level: Laustärke für das Echo
    :param framerate: Abtastrate des Audiosignals
    :return: Audiosignal mit umgekehrtem Echo-Effekt als NumPy-Array
    """
    reversed_signal = audio_signal[::-1]  # Audiosignal wird umgedreht
    echo_signal = echo(reversed_signal, delay, level, framerate)  # Erzeugt ein Echo auf dem umgedrehten Signal
    return echo_signal[::-1]  # Echo-Signal wird wieder umgedreht


def read_wave(file):
    """
    Liest eine WAV-Datei und gibt das Audiosignal und die Parameter der Datei zurück.
    :param file: Pfad zur WAV-Datei
    :return: Tuple aus Audiosignal (als Numpy-Array) und Parameter der WAV-Datei
    """
    with wave.open(file, 'rb') as wf:
        params = wf.getparams()  # Parameter(Framerate, Anzahl der Kanäle) aus der WAV-Datei lesen
        frames = wf.readframes(params.nframes)  # Alle Frames aus der WAV-Datei lesen
        sound = np.frombuffer(frames, dtype=np.int16)  # Konvertieren der Frames in ein Numpy-Array
    return sound, params


# Tiefpassfilter mit Rückkopplung
def tiefpass_filter(x, dt, RC):
    n = len(x)
    y = np.zeros(n)
    alpha = dt / (RC + dt)
    y[0] = alpha * x[0]
    for i in range(1, n):
        y[i] = alpha * x[i] + (1 - alpha) * y[i - 1]
    return y


# Hochpassfilter mit Rückkopplung
def hochpass_filter(x, dt, RC):
    n = len(x)
    y = np.zeros(n)
    alpha = RC / (RC + dt)
    y[0] = x[0]
    for i in range(1, n):
        y[i] = alpha * (y[i - 1] + x[i] - x[i - 1])
    return y


# Anwendung der Filter auf ein Audiosignal und Speichern der Ergebnisse
def filter_auf_audio_anwenden(x_t, fs, fgr, filter_typ):
    delta_T = 1 / fs

    if filter_typ == 'tp':
        RC = 1 / (2 * np.pi * fgr)
        y = tiefpass_filter(x_t, delta_T, RC)  # TP 1. Ordnung
        y = tiefpass_filter(y, delta_T, RC)  # TP 2. Ordnung
        filename = 'TP_Output2.wav'
        title = 'Tiefpass-gefiltertes Audiosignal'
    elif filter_typ == 'hp':
        RC = 1 / (2 * np.pi * fgr)
        y = hochpass_filter(x_t, delta_T, RC)  # HP 1. Ordnung
        y = hochpass_filter(y, delta_T, RC)  # HP 2. Ordnung
        filename = 'HP_Output2.wav'
        title = 'Hochpass-gefiltertes Audiosignal'
    else:
        print("Ungültiger Filtertyp. Bitte 'TP' für Tiefpass oder 'HP' für Hochpass eingeben.")
        return

    write_wave(filename, y.astype(np.int16), fs)

    # Visualisierung der Audiosignale
    zeit = np.arange(len(x_t)) / fs
    plt.figure()
    plt.subplot(2, 1, 1)
    plt.plot(zeit, x_t)
    plt.title('Originales Audiosignal')
    plt.xlabel('Zeit [s]')
    plt.ylabel('Amplitude')

    plt.subplot(2, 1, 2)
    plt.plot(zeit, y)
    plt.title(title)
    plt.xlabel('Zeit [s]')
    plt.ylabel('Amplitude')

    plt.tight_layout()
    plt.show()

    # Berechnung und Anzeige der Impulsantworten
    impulsantworten(delta_T, RC, fs, filter_typ)

    # Berechnung und Anzeige der Frequenzantworten
    plot_frequenzantworten(y, fs, filter_typ)

    print("Der Filter wurde erfolgreich angewendet. Das gefilterte Rauschen ist im Ordner verfügbar.")


def impulsantworten(dt, RC, fs, filter_typ):
    impulse = np.zeros(100)
    impulse[0] = 1

    if filter_typ == 'tp':
        y = tiefpass_filter(impulse, dt, RC)
        y = tiefpass_filter(y, dt, RC)  # Zweite Ordnung
        title = 'Impulsantwort - Tiefpassfilter'
    elif filter_typ == 'hp':
        y = hochpass_filter(impulse, dt, RC)
        y = hochpass_filter(y, dt, RC)  # Zweite Ordnung
        title = 'Impulsantwort - Hochpassfilter'
    else:
        print("Ungültiger Filtertyp.")
        return

    zeit = np.arange(len(impulse)) * dt

    plt.figure()
    plt.stem(zeit, y)
    plt.title(title)
    plt.xlabel('Zeit [s]')
    plt.ylabel('Amplitude')

    plt.tight_layout()
    plt.show()


def plot_frequenzantworten(y, fs, filter_typ):
    NFFT = 1024  # Anzahl der Punkte für die FFT
    X = np.arange(0, fs / 2, fs / NFFT)

    def frequenzantwort(signal):
        Sp = np.fft.fft(signal, NFFT) / NFFT
        Sp_abs = np.abs(Sp)
        Sp_phase = np.angle(Sp)
        return Sp_abs[:NFFT // 2] * 2, Sp_phase[:NFFT // 2]

    Y, Phase = frequenzantwort(y)

    if filter_typ == 'tp':
        title = 'Frequenzantwort - Tiefpassfilter'
    elif filter_typ == 'hp':
        title = 'Frequenzantwort - Hochpassfilter'
    else:
        print("Ungültiger Filtertyp.")
        return

    plt.figure()
    plt.subplot(2, 1, 1)
    plt.plot(X, Y)
    plt.title(title)
    plt.xlabel('Frequenz (Hz)')
    plt.ylabel('Amplitude')
    plt.grid()
    plt.subplot(2, 1, 2)
    plt.plot(X, Phase)
    plt.xlabel('Frequenz (Hz)')
    plt.ylabel('Phase (Radiant)')
    plt.grid()
    plt.tight_layout()
    plt.show()


def main():
    print(
        "Für die Einfachheit des Tests werden wir entweder Geräusche von weißem Rauschen oder eine vorhandene Vocals-Datei verwenden.")

    while True:
        while True:
            choice = input(
                "Welchen Effekt möchten Sie anwenden? Geben Sie 'f' für Filter oder 'd' für Delay ein: ").strip().lower()
            if choice in ['f', 'd']:
                break
            print("Ungültige Eingabe. Bitte 'f' für Filter oder 'd' für Delay eingeben.")

        if choice == 'f':
            print("Wir werden ein weißes Rauschen als Testton verwenden.")
            fs = 44100  # Standard-Abtastrate für Audio
            length = 3  # Länge des Signals in Sekunden
            white_noise_signal = generate_white_noise(length, fs)  # Generierung des White-Noise-Signals

            fgr = 2400  # Grenzfrequenz für den Filter

            while True:
                filter_typ = input(
                    "Welchen Filter möchten Sie verwenden? Geben Sie 'TP' für Tiefpass oder 'HP' für Hochpass ein: ").strip().lower()
                if filter_typ in ['tp', 'hp']:
                    break
                print("Ungültiger Filtertyp. Bitte 'TP' für Tiefpass oder 'HP' für Hochpass eingeben.")

            filter_auf_audio_anwenden(white_noise_signal, fs, fgr, filter_typ)
        elif choice == 'd':
            print(
                "Eine vorhandene Vocals-Datei wurde als Testton verwendet. Der Echo- und Reverse-Echo-Effekt wurde erfolgreich angewendet und die Hördateien sind im Ordner verfügbar.")
            input_file = 'Vocal.wav'  # Pfad und Dateiname der WAV-Datei
            echo_output_file = 'Vocal_mit_Echo.wav'  # Pfad und Dateiname der Ausgabedatei mit Echo-Effekt
            reverse_echo_output_file = 'Vocal_mit_Reversed_Echo.wav'  # Pfad und Dateiname der Ausgabedatei mit Reversed Echo-Effekt
            delay = 0.4  # Echo-Verzögerung in Sekunden
            level = 2  # Echo-Lautstärke

            audio_signal, params = read_wave(input_file)  # Liest WAV-Datei
            framerate = params.framerate  # Holt sich die Abtastrate aus den Parametern

            echo_signal = echo(audio_signal, delay, level, framerate)  # Erzeugt das Echo-Signal
            write_wave(echo_output_file, echo_signal.astype(np.int16),
                       framerate)  # Speichert das Echo-Signal als WAV-Datei

            reversed_echo_signal = reversed_echo(audio_signal, delay, level,
                                                 framerate)  # Erzeugt das umgekehrte Echo-Signal
            write_wave(reverse_echo_output_file, reversed_echo_signal.astype(np.int16),
                       framerate)  # Speichert das umgekehrte Echo-Signal als WAV-Datei

        while True:
            repeat = input("Möchten Sie das andere Audio-Effekt testen? (j/n): ").strip().lower()
            if repeat in ['j', 'n']:
                break
            print("Ungültige Eingabe. Bitte 'j' für Ja oder 'n' für Nein eingeben.")

        if repeat == 'n':
            print("Programm beendet.")
            break


if __name__ == "__main__":
    main()
