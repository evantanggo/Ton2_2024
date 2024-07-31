"""
Ton2 SS24, Fallstudie
Praxisproblem 1
Evan Tanggo Peter Simamora
2332397
"""

import os
import sounddevice as sd
from scipy.io.wavfile import read
from scipy.signal import resample, fftconvolve
import matplotlib.pyplot as plt
import numpy as np
from scipy.fft import fft, fftfreq
import warnings

# Basisverzeichnis, in dem sich das Skript befindet
base_dir = os.path.dirname(os.path.abspath(__file__))

# Datei untersuchen (verwenden Sie den relativen Pfad)
file_impulsantwort = os.path.join(base_dir, "Datei_B.wav")
file_musik = os.path.join(base_dir, "gitarre.wav")
file_sprache = os.path.join(base_dir, "sprache.wav")

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
        if audio_data.ndim == 2:  # Überprüfe, ob das Audiosignal Stereo ist (zwei Kanäle)
            left_channel = audio_data[:, 0]  # Extrahiere den linken Kanal
            right_channel = audio_data[:, 1]  # Extrahiere den rechten Kanal
            left_channel = 0.5 * left_channel  # Skaliere die Amplitude des linken Kanals um 50%
            right_channel = 0.5 * right_channel  # Skaliere die Amplitude des rechten Kanals um 50%
            
            # Kombiniere die skalierten Kanäle zu einem Monosignal, indem die Mittelwerte der Kanäle gebildet werden
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

# Threshold nutzen, um eine Schwelle festzulegen
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
    energy = np.sum(audio_data ** 2)                             # Total energy of the signal
    cumulative_energy = np.cumsum(audio_data[::-1] ** 2)[::-1]   # Berechne die kumulierte Energie rückwärts (invertiere das Signal, summiere dann kumulativ und invertiere erneut)
    schroeder = 10 * np.log10(cumulative_energy / energy)        # Berechne den Schroeder-Plot (in dB) als 10 * Logarithmus der kumulierten Energie normiert auf die Gesamtenergie
    zeit = np.arange(len(audio_data)) / sample_rate              # Erzeuge ein Zeit-Array, das die Zeitpunkte der Samples enthält, normiert auf die Sample-Rate

    # Berechnung der Nachhallzeiten
    try:
        t_10 = np.where(schroeder <= -10)[0][0]
        l_10 = schroeder[t_10]
    except IndexError:
        t_10 = None
        l_10 = None

    try:
        t_20 = np.where(schroeder <= -20)[0][0]
        l_20 = schroeder[t_20]
    except IndexError:
        t_20 = None
        l_20 = None

    try:
        t_30 = np.where(schroeder <= -30)[0][0]
        l_30 = schroeder[t_30]
    except IndexError:
        t_30 = None
        l_30 = None

    try:
        t_40 = np.where(schroeder <= -40)[0][0]
        l_40 = schroeder[t_40]
    except IndexError:
        t_40 = None
        l_40 = None

    return schroeder, zeit, l_10, l_20, l_30, l_40, t_10, t_20, t_30, t_40

def nachhallzeit(t_anfang, t_ende, pegelAbstand):
    if t_anfang is None or t_ende is None:
        return None
    T = (60 * (t_ende - t_anfang)) / abs(pegelAbstand)
    return T

def calculate_c50_c80(audio_data, sample_rate):
    # Berechne das quadratische Signal
    energy = np.square(audio_data)
    
    # Berechne n_50 und n_80
    n_50 = int(sample_rate * 0.05)
    n_80 = int(sample_rate * 0.08)

    # Berechne C50 und C80
    C50 = 10 * np.log10(sum(energy[0:n_50]) / sum(energy[n_50:]))
    C80 = 10 * np.log10(sum(energy[0:n_80]) / sum(energy[n_80:]))

    return C50, C80

def resample_signal(signal, original_fs, target_fs):
    num_samples = int(len(signal) * target_fs / original_fs)
    resampled_signal = resample(signal, num_samples)
    return resampled_signal

def convolve(signal1, signal2, target_fs=48000):
    fsa, a = signal1                                    # Import von Signal 1
    fsb, b = signal2                                    # Import von Signal 2

    # Resampling beider Signale auf die Zielabtastrate
    if fsa != target_fs:
        a = resample_signal(a, fsa, target_fs)
    if fsb != target_fs:
        b = resample_signal(b, fsb, target_fs)

    # Faltungsoperation
    y_conv = fftconvolve(a, b, mode='full')

    # Normalisierung des gefalteten Signals
    max_amp = np.max(np.abs(y_conv))
    if max_amp > 0:  # Vermeidung von Division durch Null
        y_conv = y_conv / max_amp

    # Abspielen des gefalteten Signals
    sd.play(y_conv, target_fs)
    sd.wait()

    return y_conv

def main():
    sample_rate, audio_data = import_data(file_impulsantwort) # Fs, y
    
    if audio_data is None:
        return 

    impulse_start = find_impulse_start(audio_data)
    
    # Berechne die Zeit des Impulsstarts in Sekunden
    impulse_start_time = impulse_start / sample_rate

    # Nur den Teil des Audiosignals ab dem Impulsstart verwenden
    audio_data = audio_data[impulse_start:]

    frequencies, fft_values, amplitude_spectrum = calculate_fft(audio_data, sample_rate)
    schroeder, zeit, l_10, l_20, l_30, l_40, t_10, t_20, t_30, t_40 = schroeder_plot(audio_data, sample_rate)

    # Hier für Amplitudenfrequenzgang
    # Bereich von 0 bis 20 kHz auswählen
    freq_range = (frequencies >= 0) & (frequencies <= 20000)
    freq_selected = frequencies[freq_range]
    amp_selected = amplitude_spectrum[freq_range]
   
    # Play the panned audio
    print(f"\nPlaying audio mit Abtastrate von {sample_rate}...")
    sd.play(audio_data, sample_rate)
    sd.wait()  # Wait until the audio is finished playing
    
    # Nachhallzeit-Berechnung
    T_10 = nachhallzeit(t_10 / sample_rate, t_20 / sample_rate, (l_20-l_10))
    T_20 = nachhallzeit(t_10 / sample_rate, t_30 / sample_rate, (l_30-l_10))
    T_30 = nachhallzeit(t_10 / sample_rate, t_40 / sample_rate, (l_40-l_10))

    if T_10 is not None:
        print(f"\nT10 ist {T_10:.2f} s")
    else:
        print("\nT10 konnte nicht berechnet werden")

    if T_20 is not None:
        print(f"T20 ist {T_20:.2f} s")
    else:
        print("T20 konnte nicht berechnet werden")

    if T_30 is not None:
        print(f"T30 ist {T_30:.2f} s")
    else:
        print("T30 konnte nicht berechnet werden")

    print("__________________________")

    # Deutlichkeitsmaß und Klarheitsmaß berechnen
    C50, C80 = calculate_c50_c80(audio_data, sample_rate)
    print(f"\nC50 ist {C50:.2f} dB")
    print(f"C80 ist {C80:.2f} dB")

    # Geraden-Arrays für die Nachhallzeiten
    if t_10 is not None:
        zeit_10 = zeit[t_10:]
        if T_10 is not None:
            idx10 = int(T_10 * sample_rate) + 1                     # Index zum Zeitpunkt der erreichten Nachhallzeit
            g10 = np.linspace(schroeder[t_10], -60, idx10 - t_10)   # Zeit-Array für Gerade der Nachhallzeit erstellen
        if T_20 is not None:
            idx20 = int(T_20 * sample_rate) + 1
            g20 = np.linspace(schroeder[t_10], -60, idx20 - t_10)
        if T_30 is not None:
            idx30 = int(T_30 * sample_rate) + 1
            g30 = np.linspace(schroeder[t_10], -60, idx30 - t_10)

    # Plots erstellen
    
    fig, axs = plt.subplots(2, 1, figsize=(10, 8))

    # Amplitudenfrequenzgang
    axs[0].plot(freq_selected, amp_selected)
    axs[0].set_xscale('log')
    axs[0].set_yscale('log')
    axs[0].set_title('Amplitudenfrequenzgang (0-20 kHz)')
    axs[0].set_xlabel('Frequenz (Hz)')
    axs[0].set_ylabel('Amplitude')
    
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
    plt.ion()
    fig2, ax2 = plt.subplots(figsize=(10, 4))
    ax2.plot(zeit, schroeder)

    if T_10 is not None:
        ax2.plot(zeit_10[:len(g10)], g10, color='darkorange', label='T10 = {:.2f}s'.format(T_10), linestyle=':', linewidth='1.5')
        ax2.scatter([T_10], [-60], s=40, marker='x', color='darkorange')
    if T_20 is not None:
        ax2.plot(zeit_10[:len(g20)], g20, color='fuchsia', label='T20 = {:.2f}s'.format(T_20), linestyle=':', linewidth='1.5')
        ax2.scatter([T_20], [-60], s=40, marker='x', color='fuchsia')
    if T_30 is not None:
        ax2.plot(zeit_10[:len(g30)], g30, color='darkcyan', label='T30 = {:.2f}s'.format(T_30), linestyle=':', linewidth='1.5')
        ax2.scatter([T_30], [-60], s=40, marker='x', color='darkcyan')

    ax2.grid()
    ax2.set_title("Schroeder-Plot")
    ax2.set_xlabel("Zeit in sek.")
    ax2.set_ylabel("Energie in dB")
    ax2.legend()

    # Layout anpassen und zweite Figure anzeigen
    plt.tight_layout()
    plt.show(block=False)
     

    # Berechnung der Differenz der jeweiligen Nachhallzeit mit dem Energie-Pegel
    cut_val = float(input('\nKorrelationsberechnung:'
                      '\nFließkommazahl des Zeitpunktes, an dem die Energiepegel-Kennlinie '
                      '\ngerade noch parallel zu den Nachhallzeiten-Geraden verläuft:  '))          

    plt.ioff()
    # Calculate `cut_idx` based on `cut_val`
    cut_idx = int(cut_val * sample_rate) + 1

    # Calculate differences
    diff_array = (
        schroeder[t_10:idx10] - g10,
        schroeder[t_10:idx20] - g20,
        schroeder[t_10:idx30] - g30
    )

    # Truncate to `cut_idx` length
    diff_array = [d[:cut_idx] for d in diff_array] 

    # Absolute values for integration
    abs_diff_array = [[abs(val) for val in d] for d in diff_array]

    # Numerical integration to find the "area under the curve"
    korr_value = [np.sum(d) for d in abs_diff_array]

    # Index of the minimum value
    korr_idx = np.argmin(korr_value)


    # List for output
    list_str = ["T10", "T20", "T30"]
    list_float = [round(T_10, 2), round(T_20, 2), round(T_30, 2)] 

    # Dritte Figure des Differenzs von T10, T20 & T30 mit dem Energie-Pegel
    fig3, ax3 = plt.subplots(figsize=(10, 4))

    ax3.plot(zeit[t_10:cut_idx], abs_diff_array[0][:cut_idx-t_10], color='darkorange', label='L - T10')
    ax3.plot(zeit[t_10:cut_idx], abs_diff_array[1][:cut_idx-t_10], color='fuchsia', label='L - T20')
    ax3.plot(zeit[t_10:cut_idx], abs_diff_array[2][:cut_idx-t_10], color='darkcyan', label='L - T30')

    ax3.set_title("Differenz-Kennlinie für T10, T20 & T30")
    ax3.set_xlabel("Zeit in sek.")
    ax3.set_ylabel("Differenz in dB")
    ax3.legend()
    ax3.grid()

    # Layout anpassen und dritte Figure anzeigen
    plt.tight_layout()
    plt.show()

    print(f'\nDie beste Näherung ergibt sich für '
          f'{list_str[korr_idx]} = {list_float[korr_idx]}s.\n')

     # User input to select either music or speech file
    while True:
        choice = input("Für Auralistaion bitte drücke '1' für Musik oder '2' für Sprache: ")
        if choice == '1':
            file_signal = os.path.basename(file_musik)
            sample_rate_signal, audio_data_signal = import_data(file_musik)
            break
        elif choice == '2':
            file_signal = os.path.basename(file_sprache)
            sample_rate_signal, audio_data_signal = import_data(file_sprache)
            break
        else:
            print("Ungültige Eingabe. Bitte drücke '1' oder '2'.")

    print(f"\nPlaying Auralisation mit {file_signal}...\n")
    convolve((sample_rate, audio_data), (sample_rate_signal, audio_data_signal))

if __name__ == "__main__":
    main()
