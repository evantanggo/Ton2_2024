"""
Ton2 SS24, Fallstudie
Praxisproblem 3
Evan Tanggo Peter Simamora
2332397
"""

import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.io.wavfile import read
from scipy.signal import butter, sosfilt, sosfreqz
import sounddevice as sd
import warnings
import time

# Basisverzeichnis, in dem sich das Skript befindet
base_dir = os.path.dirname(os.path.abspath(__file__))

# Dateipfade festlegen
noise_file = os.path.join(base_dir, "pinknoise.wav")
voice_file = os.path.join(base_dir, "sprache.wav")
music_file = os.path.join(base_dir, "gitarre.wav")

def import_audio(file_path):
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Die Datei {file_path} wurde nicht gefunden.")
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            sample_rate, audio_data = read(file_path)
        
        if audio_data.ndim == 2:  # Überprüfe, ob das Audiosignal Stereo ist (zwei Kanäle)
            left_channel = audio_data[:, 0]  # Extrahiere den linken Kanal
            right_channel = audio_data[:, 1]  # Extrahiere den rechten Kanal
            left_channel = 0.5 * left_channel  # Skaliere die Amplitude des linken Kanals um 50%
            right_channel = 0.5 * right_channel  # Skaliere die Amplitude des rechten Kanals um 50%
            
            # Kombiniere die skalierten Kanäle zu einem Monosignal, indem die Mittelwerte der Kanäle gebildet werden
            mono_data = (left_channel + right_channel) / 2
        else:
            mono_data = audio_data
        
        max_amp = np.max(np.abs(mono_data))
        normalized_data = mono_data / max_amp
        return sample_rate, normalized_data

    except Exception as e:
        print(f"Fehler beim Laden der Datei {file_path}: {str(e)}")
        return None, None
    
def low_pass_filter(signal, dt, RC):
    n = len(signal)
    filtered_signal = np.zeros(n)
    alpha = dt / (RC + dt)
    filtered_signal[0] = alpha * signal[0]
    for i in range(1, n):
        filtered_signal[i] = alpha * signal[i] + (1 - alpha) * filtered_signal[i - 1]
    return filtered_signal

def high_pass_filter(signal, dt, RC):
    n = len(signal)
    #filtered_signal = np.zeros(n)
    alpha = RC / (RC + dt)
    filtered_signal = np.zeros_like(signal)
    for i in range(1, n):
        filtered_signal[i] = alpha * (filtered_signal[i - 1] + (signal[i] - signal[i - 1]))
    return filtered_signal


def convert_db_to_linear(Q_dB):
    return 10**(Q_dB / 10)

def compute_fl_fh(fc, Q_linear):
    # Berechnung für Grenzfrequenz von Tief- und Hochpass
    fbw = fc / Q_linear
    fl = (-fbw + np.sqrt(fbw**2 + 4 * fc**2)) / 2
    fh = fbw + fl
    return fl, fh

def design_bandstop_filter(fs, fc, Q_dB):
    # Konvertiere Q-Faktor von dB in lineare Skala
    Q_linear = convert_db_to_linear(Q_dB)

    # Berechne die untere und obere Grenzfrequenz basierend auf der Mittenfrequenz und dem Q-Faktor
    fl, fh = compute_fl_fh(fc, Q_linear)

    # Begrenze die Grenzfrequenzen auf den Bereich von 20 Hz bis 2000 Hz
    fl = max(fl, 20)
    fh = min(fh, 2000)

    # Berechne die Nyquist-Frequenz (halbe Abtastrate)
    nyquist = 0.5 * fs

    # Normiere die Grenzfrequenzen auf die Nyquist-Frequenz
    low = fl / nyquist
    high = fh / nyquist

    # Entwerfe ein Butterworth-Bandstopfilter mit der gegebenen Ordnung und Grenzfrequenzen
    sos = butter(N=2, Wn=[low, high], btype='bandstop', output='sos')

    # Gib das Filter und die berechneten Grenzfrequenzen zurück
    return sos, fl, fh

def plot_impulse_response(dt, RC, filter_type, sos=None):
    n = 100
    impulse = np.zeros(n)
    impulse_a = np.zeros(n)
    impulse[0] = 1 # mit Dirac für die Impulsantwort

    if filter_type == 'tp':
        response = low_pass_filter(impulse, dt, RC)
        title = 'Impulsantwort - Tiefpassfilter'
    elif filter_type == 'hp':
        response = high_pass_filter(impulse, dt, RC)
        title = 'Impulsantwort - Hochpassfilter'
    elif filter_type == 'bs' and sos is not None:
        response = sosfilt(sos, impulse)
        title = 'Impulsantwort - Bandsperre'
    else:
        print("Unbekannter Filtertyp.")
        return

    time = np.arange(len(impulse)) * dt

    plt.figure()
    plt.stem(time, response)
    plt.title(title)
    plt.xlabel('Zeit [s]')
    plt.ylabel('Amplitude')
    plt.tight_layout()
    plt.show()

def plot_frequency_response(signal, fs, filter_type):
    NFFT = 1024  # Anzahl der Punkte für die FFT-Berechnung
    freq = np.arange(0, fs / 2, fs / NFFT)  # Frequenzachse für die erste Hälfte des Spektrums

    def frequency_response(signal):
        # Berechne das Frequenzspektrum des Signals
        spectrum = np.fft.fft(signal, NFFT) / NFFT  # Normalisierte FFT-Berechnung
        magnitude = np.abs(spectrum)  # Betragsspektrum
        phase = np.angle(spectrum)  # Phasenspektrum
        return magnitude[:NFFT // 2] * 2, phase[:NFFT // 2]  # Rückgabe der ersten Hälfte des Spektrums

    magnitude, phase = frequency_response(signal)  # Berechne Frequenzgang des Signals

    # Bestimme den Titel basierend auf dem Filtertyp
    if filter_type == 'tp':
        title = 'Frequenzantwort - Tiefpassfilter'
    elif filter_type == 'hp':
        title = 'Frequenzantwort - Hochpassfilter'
    elif filter_type == 'bs':
        title = 'Frequenzantwort - Bandsperre'
    else:
        print("Unbekannter Filtertyp.")
        return

    # Erstelle eine neue Abbildung
    plt.figure()

    # Erstelle den Amplitudenplot
    plt.subplot(2, 1, 1)
    plt.plot(freq, magnitude)
    plt.title(title)  # Titel der Grafik
    plt.xlabel('Frequenz (Hz)')  # X-Achsenbeschriftung
    plt.ylabel('Amplitude')  # Y-Achsenbeschriftung
    plt.grid()

    # Erstelle den Phasenplot
    plt.subplot(2, 1, 2)
    plt.plot(freq, phase)
    plt.xlabel('Frequenz (Hz)')  # X-Achsenbeschriftung
    plt.ylabel('Phase (Radiant)')  # Y-Achsenbeschriftung
    plt.grid()

    # Optimierung des Layouts und Anzeige der Grafik
    plt.tight_layout()
    plt.show()

def plot_impulse_response_bs(sos, fs):
    # Erzeuge einen Impuls (Einheitsimpuls)
    impulse = np.zeros(100)
    impulse[0] = 1  # Setze den ersten Wert auf 1 (Dirac)

    # Berechne die Impulsantwort des Filters
    response = sosfilt(sos, impulse)

    # Erzeuge einen Zeitvektor
    time = np.arange(len(impulse)) / fs

    # Erstelle eine neue Abbildung
    plt.figure()

    # Erstelle einen Stemm-Plot der Impulsantwort
    plt.stem(time, response)
    plt.title('Impulsantwort - Bandsperre')  # Titel der Grafik
    plt.xlabel('Zeit [s]')  # X-Achsenbeschriftung
    plt.ylabel('Amplitude')  # Y-Achsenbeschriftung

    # Layout der Grafik optimieren und anzeigen
    plt.tight_layout()
    plt.show()

def plot_frequency_response_bs(sos, fs):
    # Berechne die Frequenzantwort des Filters
    w, h = sosfreqz(sos, worN=2000, fs=fs)

    # Begrenze die Frequenzanzeige auf maximal 2000 Hz
    max_freq = 2000
    mask = w <= max_freq
    w = w[mask] # Frequenzen auf den Bereich bis 2000 Hz beschränken
    h = h[mask] # Entsprechende Frequenzantworten beschränken

    plt.figure() # Erstelle eine neue Abbildung

     # Erste Untergrafik: Amplitudenfrequenzgang
    plt.subplot(2, 1, 1)  # Zwei Zeilen, eine Spalte, erste Grafik
    plt.plot(w, 20 * np.log10(np.abs(h)))  # Amplituden in dB plotten
    plt.title('Frequenzantwort - Bandsperre')  # Titel der Grafik
    plt.xlabel('Frequenz (Hz)')  # X-Achsenbeschriftung
    plt.ylabel('Amplitude [dB]')  # Y-Achsenbeschriftung
    plt.grid()  # Raster anzeigen
    
    # Zweite Untergrafik: Phasenfrequenzgang
    plt.subplot(2, 1, 2)  # Zwei Zeilen, eine Spalte, zweite Grafik
    plt.plot(w, np.angle(h))  # Phase in Radiant plotten
    plt.xlabel('Frequenz (Hz)')  # X-Achsenbeschriftung
    plt.ylabel('Phase (Radiant)')  # Y-Achsenbeschriftung
    plt.grid()  # Raster anzeigen

    # Layout der Grafiken optimieren und anzeigen
    plt.tight_layout()
    plt.show()

def apply_filter_to_audio_onlyplay(signal, fs, fc, filter_type, Q_dB=None):
    dt = 1 / fs

    if filter_type == 'tp':
        RC = 1 / (2 * np.pi * fc)
        filtered_signal = low_pass_filter(signal, dt, RC)
        title = 'Tiefpass-gefiltertes Audiosignal'
    elif filter_type == 'hp':
        RC = 1 / (2 * np.pi * fc)
        filtered_signal = high_pass_filter(signal, dt, RC)
        title = 'Hochpass-gefiltertes Audiosignal'
    elif filter_type == 'bs' and Q_dB is not None:
        sos, fl, fh = design_bandstop_filter(fs, fc, Q_dB)
        filtered_signal = sosfilt(sos, signal)
        title = 'Bandsperre-gefiltertes Audiosignal'
    else:
        print("Unbekannter Filtertyp. Bitte 'tp', 'hp' oder 'bs' verwenden.")
        return

    sd.play(filtered_signal, fs)
    sd.wait()

def apply_filter_to_audio(signal, fs, fgr, filter_type, Q_dB=None):
    dt = 1 / fs

    if filter_type == 'tp':
        RC = 1 / (2 * np.pi * fgr)
        filtered_signal = low_pass_filter(signal, dt, RC)
        title = 'Tiefpass-gefiltertes Audiosignal'
    elif filter_type == 'hp':
        RC = 1 / (2 * np.pi * fgr)
        filtered_signal = high_pass_filter(signal, dt, RC)
        title = 'Hochpass-gefiltertes Audiosignal'
    elif filter_type == 'bs' and Q_dB is not None:
        sos, fl, fh = design_bandstop_filter(fs, fgr, Q_dB)
        filtered_signal = sosfilt(sos, signal)
        title = 'Bandsperre-gefiltertes Audiosignal'
    else:
        print("Unbekannter Filtertyp. Bitte 'tp', 'hp' oder 'bs' verwenden.")
        return

    sd.play(filtered_signal, fs)
    sd.wait()

    time = np.arange(len(signal)) / fs
    plt.figure()
    plt.subplot(2, 1, 1)
    plt.plot(time, signal)
    plt.title('Originales Audiosignal')
    plt.xlabel('Zeit [s]')
    plt.ylabel('Amplitude')

    plt.subplot(2, 1, 2)
    plt.plot(time, filtered_signal)
    plt.title(title)
    plt.xlabel('Zeit [s]')
    plt.ylabel('Amplitude')
    plt.tight_layout()
    plt.show()

    if filter_type == 'bs':
        plot_impulse_response_bs(sos, fs)
        plot_frequency_response_bs(sos, fs)
    else:
        plot_impulse_response(dt, RC, filter_type)
        plot_frequency_response(filtered_signal, fs, filter_type)


def pingpong_effect(signal, fs, delay_ms=500):
    # Berechne die Verzögerung in Samples
    delay_samples = round(delay_ms / 1000 * fs)
    
    # Überprüfe, ob das Signal stereo ist oder nicht
    if signal.ndim == 2 and signal.shape[1] == 2:
        left_channel = signal[:, 0]
        right_channel = signal[:, 1]
    else:
        left_channel = signal
        right_channel = signal
    
    # Normalisiere die Signale auf den Bereich [-1, 1]
    left_channel /= np.max(np.abs(left_channel))
    right_channel /= np.max(np.abs(right_channel))
    
    # Erzeuge Arrays für zusätzliche Verzögerungspuffer
    extra_L = np.zeros(delay_samples, dtype=int)
    extra_R = np.zeros(2 * delay_samples, dtype=int)
    
    # Füge Verzögerungen für den linken Kanal hinzu
    left_delay_L_1 = np.append(extra_L, left_channel)
    left_delay_L = np.append(left_delay_L_1, extra_L)

    # Füge Verzögerungen für den rechten Kanal hinzu
    right_delay_L = np.append(right_channel, extra_R)
    
    # Weitere Verzögerungen für den linken und rechten Kanal
    left_delay_R = np.append(left_channel, extra_R)
    right_delay_R = np.append(extra_R, right_channel)
    
    # Erzeuge verzögerte Stereo-Signale
    stereo_delay_L = np.vstack((left_delay_L, right_delay_L)).T
    stereo_delay_R = np.vstack((left_delay_R, right_delay_R)).T
    
    # Mische die verzögerten Stereo-Signale
    stereo_delay_LR = (stereo_delay_L + stereo_delay_R) / 2
    
    # Erweiterung der ursprünglichen Kanäle um die Verzögerung
    left_new = np.append(left_channel, extra_R)
    right_new = np.append(right_channel, extra_R)
    stereo = np.vstack((left_new, right_new)).T
    
    # Kombiniere das ursprüngliche Stereo-Signal mit den verzögerten Signalen
    stereo_output = stereo + stereo_delay_LR
    
    return stereo_output

def main():
    # Parameter für den Filter
    fc = 700    # Grenzfrequenz für Bandsperre
    Q_dB = -3   # Gütefaktor in dB
    
    # Audiodateien laden
    fs_noise, noise_data = import_audio(noise_file)
    fs_voice, voice_data = import_audio(voice_file)
    fs_music, music_data = import_audio(music_file)
    
    if noise_data is None or voice_data is None:
        return
    
    # fl ist die untere Grenzfrequenz, fh ist die obere Grenzfrequenz
    sos, fl, fh = design_bandstop_filter(fs_noise, fc, Q_dB)
    print(fl)
    print(fh)

    print("\nFILTER AUF NOISESIGNAL")
    # Benutzerabfrage nach dem Filtertyp
    filter_type = input("\nWelchen Filter möchten Sie anwenden? 'tp' für Tiefpass, 'hp' für Hochpass, 'bs' für Bandsperre: ").strip().lower()
    
    # Filtertyp überprüfen und anpassen
    if filter_type not in ['tp', 'hp', 'bs']:
        print("Unbekannter Filtertyp. Bitte 'tp', 'hp' oder 'bs' verwenden.")
        return
    # Filter anwenden basierend auf Benutzerwahl
    if filter_type == 'tp':
        apply_filter_to_audio(noise_data, fs_noise, fl, 'tp')
    elif filter_type == 'hp':
        apply_filter_to_audio(noise_data, fs_noise, fh, 'hp')
    elif filter_type == 'bs':
        apply_filter_to_audio(noise_data, fs_noise, fc, 'bs', Q_dB)
    
    # Ping Pong Delay 
    print("\nPING PONG DELAY EFFEKT AUF SPRACHSIGNAL")
    delay_abfrage = input("\nMöchten Sie den Ping Pong Effekt haben? [j/n] : ").strip().lower()

    if delay_abfrage == "j":
        signal = input("\nSprache oder Musik? : ").strip().lower()
        if signal == "sprache":
            processed_delay = pingpong_effect(voice_data, fs_voice)
            print("Ping Pong Delay wird abgespielt..")
            time.sleep(1)
            sd.play(processed_delay, fs_voice)
            sd.wait()

            effekt_abfrage = input("\nMöchten Sie Tiefpass/Hochpass/Bandsperre auf das Signal\nTippen Sie [tp/hp/bs], wenn nicht tippen Sie [n]: ").strip().lower()

            if effekt_abfrage == 'tp':
                print("\nOriginaldatei mit Effekt wird abgespielt..")
                apply_filter_to_audio_onlyplay(voice_data, fs_voice, fl, 'tp')
            elif effekt_abfrage == 'hp':
                print("\nOriginaldatei mit Effekt wird abgespielt..")
                apply_filter_to_audio_onlyplay(voice_data, fs_voice, fh, 'hp')
            elif effekt_abfrage == 'bs':
                print("\nOriginaldatei mit Effekt wird abgespielt..")
                apply_filter_to_audio_onlyplay(voice_data, fs_voice, fc, 'bs', Q_dB)
            elif effekt_abfrage == "n":
                print("\nAufgabe übersprungen")

        elif signal == "musik":
            processed_delay = pingpong_effect(music_data, fs_music)
            print("Ping Pong Delay wird abgespielt..")
            time.sleep(1)
            sd.play(processed_delay, fs_music)
            sd.wait()

            effekt_abfrage = input("\nMöchten Sie Tiefpass/Hochpass/Bandsperre auf das Signal\nTippen Sie [tp/hp/bs], wenn nicht tippen Sie [n]: ").strip().lower()

            if effekt_abfrage == 'tp':
                print("\nOriginaldatei mit Effekt wird abgespielt..")
                apply_filter_to_audio_onlyplay(music_data, fs_music, fl, 'tp')
            elif effekt_abfrage == 'hp':
                print("\nOriginaldatei mit Effekt wird abgespielt..")
                apply_filter_to_audio_onlyplay(music_data, fs_music, fh, 'hp')
            elif effekt_abfrage == 'bs':
                print("\nOriginaldatei mit Effekt wird abgespielt..")
                apply_filter_to_audio_onlyplay(music_data, fs_music, fc, 'bs', Q_dB)
            elif effekt_abfrage == "n":
                print("\nAufgabe übersprungen")
        else:
            print("Ungültige Eingabe. Bitte geben Sie 'Sprache' oder 'Musik' ein.")
    elif delay_abfrage == "n":
        print("\nAufgabe übersprungen")

if __name__ == "__main__":
    main()

