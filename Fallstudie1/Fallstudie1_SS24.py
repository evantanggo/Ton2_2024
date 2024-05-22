import os
import librosa
import librosa.display
import sounddevice as sd
from scipy.io.wavfile import read
import matplotlib.pyplot as plt
import numpy as np
from scipy.fft import fft, fftfreq
import warnings

# Basisverzeichnis, in dem sich das Skript befindet
base_dir = os.path.dirname(os.path.abspath(__file__))

# Datei untersuchen (verwenden Sie den relativen Pfad)
file_path = os.path.join(base_dir, "Datei_B.wav")

def import_data(file_path):
    try:
        # Überprüfe, ob die Datei existiert
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Die Datei {file_path} existiert nicht.")
        
        # Datei einlesen
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            sample_rate, audio_data = read(file_path)
        
        # Datei in Mono umwandeln, wenn Stereo
        if audio_data.ndim == 2:
            left_channel = audio_data[:, 0]
            right_channel = audio_data[:, 1]
            mono_data = (left_channel + right_channel) / 2
        else:
            mono_data = audio_data
        
        # Signal normalisieren
        max_amp = np.max(np.abs(mono_data))
        mono_data_normalized = mono_data / max_amp
        return sample_rate, mono_data_normalized

    except Exception as e:
        print(f"Fehler beim Importieren der Daten aus {file_path}: {str(e)}")
        return None, None

def find_impulse_start(audio_data, threshold=0.01):
    for i, sample in enumerate(audio_data):
        if abs(sample) > threshold:
            return i
    return 0

# Sound abspielen
def play_sound(file_path):
    sample_rate, audio_data = import_data(file_path)
    if audio_data is not None:
        sd.play(audio_data, sample_rate, blocking=True)

def calculate_fft(signal, sample_rate):
    n = len(signal)
    frequencies = fftfreq(n, 1 / sample_rate)
    fft_values = fft(signal)

    # Berechnung des Betrags des Amplitudenfrequenzgangs
    amplitude_spectrum = np.abs(fft_values)
    return frequencies, fft_values, amplitude_spectrum

def schroeder_plot(audio_data, sample_rate):
    schroeder = []
    zeit = []
    energy = np.sum(audio_data ** 2) / sample_rate  # Total energy of the signal

    # Initialisierung der Variablen
    t_10, t_20, t_30, t_40 = None, None, None, None

    for t in range(0, len(audio_data), 1000):
        frame_energy = np.sum(np.square(audio_data[t:t+1000])) / sample_rate
        if frame_energy > 0:  # Avoid log(0) which is undefined
            schroeder.append(10 * np.log10(frame_energy / energy))
            zeit.append(t / sample_rate)

        if t_10 is None and frame_energy <= energy * 0.1:
            t_10 = t / sample_rate
        if t_20 is None and frame_energy <= energy * 0.01:
            t_20 = t / sample_rate
        if t_30 is None and frame_energy <= energy * 0.001:
            t_30 = t / sample_rate
        if t_40 is None and frame_energy <= energy * 0.0001:
            t_40 = t / sample_rate

    return schroeder, zeit, energy, t_10, t_20, t_30, t_40

def nachhallzeit(t_anfang, t_ende, pegelAbstand):
    T = (60 * (t_ende - t_anfang)) / pegelAbstand
    return T

def calculate_c50_c80(audio_data, sample_rate):
    # Berechne das quadratische Signal
    raumquad = np.square(audio_data)
    
    # Berechne n_50 und n_80
    n_50 = int(sample_rate * 0.05)
    n_80 = int(sample_rate * 0.08)

    # Berechne C50 und C80
    C50 = 10 * np.log10(sum(raumquad[0:n_50]) / sum(raumquad[n_50:]))
    C80 = 10 * np.log10(sum(raumquad[0:n_80]) / sum(raumquad[n_80:]))

    return C50, C80

def main():
    sample_rate, audio_data = import_data(file_path) # Fs, y
    impulse_start = find_impulse_start(audio_data)
    
    # Berechne die Zeit des Impulsstarts in Sekunden
    impulse_start_time = impulse_start / sample_rate

    # Nur den Teil des Audiosignals ab dem Impulsstart verwenden
    audio_data = audio_data[impulse_start:]

    frequencies, fft_values, amplitude_spectrum = calculate_fft(audio_data, sample_rate)
    schroeder, zeit, energy, t_10, t_20, t_30, t_40 = schroeder_plot(audio_data, sample_rate)

    # Hier für Amplitudenfrequenzgang
    # Bereich von 0 bis 20 kHz auswählen
    freq_range = (frequencies >= 0) & (frequencies <= 20000)
    freq_selected = frequencies[freq_range]
    amp_selected = amplitude_spectrum[freq_range]

    # Nachhallzeit-Berechnung
    T_10 = nachhallzeit(t_10, t_20, 10)
    T_20 = nachhallzeit(t_10, t_30, 20)
    T_30 = nachhallzeit(t_10, t_40, 30)
    print(f"\nT10 ist {T_10:.2f} s")
    print(f"T20 ist {T_20:.2f} s")
    print(f"T30 ist {T_30:.2f} s")
    print("__________________________")
    # Deutlichkeitsmaß und Klarheitsmaß berechnen
    C50, C80 = calculate_c50_c80(audio_data, sample_rate)
    print(f"\nC50 ist {C50:.2f} dB")
    print(f"C80 ist {C80:.2f} dB")

    # Plots erstellen
    fig, axs = plt.subplots(2, 1, figsize=(10, 8))

    # Amplitudenfrequenzgang
    axs[0].plot(freq_selected, amp_selected)
    axs[0].set_xscale('log')
    axs[0].set_yscale('log')
    axs[0].set_title('Amplitudenfrequenzgang (0-20 kHz)')
    axs[0].set_xlabel('Frequenz (Hz)')
    axs[0].set_ylabel('Amplitude')
    # Markiere den Impulsstart
    axs[0].axvline(x=impulse_start_time, color='r', linestyle='--', label='Impulsstart')
    axs[0].legend()

    # Spektrogramm
    NFFT = 1024  # Größe des FFT-Fensters
    Pxx, freqs, bins, im = axs[1].specgram(audio_data, NFFT=NFFT, Fs=sample_rate, noverlap=900)
    axs[1].set_title('Spektrogramm')
    axs[1].set_xlabel('$t$ in s')
    axs[1].set_ylabel('$f$ in Hz')

    # Layout anpassen und erste Figure anzeigen
    plt.tight_layout()
    plt.show()

    # Zweite Figure für Schroeder-Plot
    fig2, ax2 = plt.subplots(figsize=(10, 4))
    ax2.plot(zeit, schroeder)
    ax2.grid()
    ax2.set_title("Schroeder-Plot")
    ax2.set_xlabel("Zeit in sek.")
    ax2.set_ylabel("Energie in dB")
    # Markiere den Impulsstart
    ax2.axvline(x=impulse_start_time, color='r', linestyle='--', label='Impulsstart')
    ax2.legend()

    # Layout anpassen und zweite Figure anzeigen
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # play_sound(file_path)
    main()
