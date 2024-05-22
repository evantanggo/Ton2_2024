import os
import librosa
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

def spectrogram(Fs, y):
    # Compute spectrogram
    S = librosa.stft(y)
    D = librosa.amplitude_to_db(abs(S), ref=np.max)
    # Plot spectrogram
    plt.figure(figsize=(10, 4))
    librosa.display.specshow(D, sr=Fs, x_axis='time', y_axis='log')
    plt.colorbar(format='%+2.0f dB')
    plt.title('Spectrogram')
    plt.show()

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

    for t in range(0, len(audio_data), 1000):
        frame_energy = np.sum(np.square(audio_data[t:t+1000])) / sample_rate
        if frame_energy > 0:  # Avoid log(0) which is undefined
            schroeder.append(10 * np.log10(frame_energy / energy))
            zeit.append(t / sample_rate)

    return schroeder, zeit, energy

def main():
    sample_rate, audio_data = import_data(file_path) # Fs, y
    impulse_start = find_impulse_start(audio_data)
    
    # Berechne die Zeit des Impulsstarts in Sekunden
    impulse_start_time = impulse_start / sample_rate

    # Nur den Teil des Audiosignals ab dem Impulsstart verwenden
    audio_data = audio_data[impulse_start:]

    frequencies, fft_values, amplitude_spectrum = calculate_fft(audio_data, sample_rate)
    schroeder, zeit, energy = schroeder_plot(audio_data, sample_rate)

    # Hier für Amplitudenfrequenzgang
    # Bereich von 0 bis 20 kHz auswählen
    freq_range = (frequencies >= 0) & (frequencies <= 20000)
    freq_selected = frequencies[freq_range]
    amp_selected = amplitude_spectrum[freq_range]

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

    # Schroeder-Plot
    axs[1].plot(zeit, schroeder)
    axs[1].grid()
    axs[1].set_title("Schroeder-Plot")
    axs[1].set_xlabel("Zeit in sek.")
    axs[1].set_ylabel("Energie in dB")
    # Markiere den Impulsstart
    axs[1].axvline(x=impulse_start_time, color='r', linestyle='--', label='Impulsstart')
    axs[1].legend()

    # Layout anpassen
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # play_sound(file_path)
    main()
