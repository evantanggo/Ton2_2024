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

def import_audio(file_path):
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Die Datei {file_path} wurde nicht gefunden.")
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            sample_rate, audio_data = read(file_path)
        
        if audio_data.ndim == 2:
            left = audio_data[:, 0]
            right = audio_data[:, 1]
            left = 0.5 * left
            right = 0.5 * right
            mono_data = (left + right) / 2
        else:
            mono_data = audio_data
        
        max_amp = np.max(np.abs(mono_data))
        normalized_data = mono_data / max_amp
        return sample_rate, normalized_data

    except Exception as e:
        print(f"Fehler beim Laden der Datei {file_path}: {str(e)}")
        return None, None
    
def play_audio(file_path):
    sample_rate, audio_data = import_audio(file_path)
    if audio_data is not None:
        sd.play(audio_data, sample_rate, blocking=True)

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
    filtered_signal = np.zeros(n)
    alpha = RC / (RC + dt)
    filtered_signal[0] = signal[0]
    for i in range(1, n):
        filtered_signal[i] = alpha * (filtered_signal[i - 1] + signal[i] - signal[i - 1])
    return filtered_signal

def convert_db_to_linear(Q_dB):
    return 10**(Q_dB / 10)

def compute_fl_fh(fc, Q_linear):
    fbw = fc / Q_linear
    fl = (-fbw + np.sqrt(fbw**2 + 4 * fc**2)) / 2
    fh = fbw + fl
    return fl, fh

def design_bandstop_filter(fs, fc, Q_dB):
    Q_linear = convert_db_to_linear(Q_dB)
    fl, fh = compute_fl_fh(fc, Q_linear)
    fl = max(fl, 20)
    fh = min(fh, 2000)
    
    nyquist = 0.5 * fs
    low = fl / nyquist
    high = fh / nyquist
    sos = butter(N=2, Wn=[low, high], btype='bandstop', output='sos')
    return sos, fl, fh

def plot_bode_diagram(sos, fs):
    w, h = sosfreqz(sos, worN=2000, fs=fs)
    plt.figure()
    plt.semilogx(w, 20 * np.log10(np.abs(h)), label='Amplitude')
    plt.title('Bode-Diagramm des Bandstop-Filters')
    plt.xlabel('Frequenz [Hz]')
    plt.ylabel('Amplitude [dB]')
    plt.grid()
    plt.show()

def plot_impulse_response(dt, RC, fs, filter_type, sos=None):
    impulse = np.zeros(100)
    impulse[0] = 1

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
    plt.stem(time, response, basefmt=" ")
    plt.title(title)
    plt.xlabel('Zeit [s]')
    plt.ylabel('Amplitude')
    plt.tight_layout()
    plt.show()



def plot_frequency_response(signal, fs, filter_type):
    NFFT = 1024
    freq = np.arange(0, fs / 2, fs / NFFT)

    def frequency_response(signal):
        spectrum = np.fft.fft(signal, NFFT) / NFFT
        magnitude = np.abs(spectrum)
        phase = np.angle(spectrum)
        return magnitude[:NFFT // 2] * 2, phase[:NFFT // 2]

    magnitude, phase = frequency_response(signal)

    if filter_type == 'tp':
        title = 'Frequenzantwort - Tiefpassfilter'
    elif filter_type == 'hp':
        title = 'Frequenzantwort - Hochpassfilter'
    elif filter_type == 'bs':
        title = 'Frequenzantwort - Bandsperre'
    else:
        print("Unbekannter Filtertyp.")
        return

    plt.figure()
    plt.subplot(2, 1, 1)
    plt.plot(freq, magnitude)
    plt.title(title)
    plt.xlabel('Frequenz (Hz)')
    plt.ylabel('Amplitude')
    plt.grid()
    plt.subplot(2, 1, 2)
    plt.plot(freq, phase)
    plt.xlabel('Frequenz (Hz)')
    plt.ylabel('Phase (Radiant)')
    plt.grid()
    plt.tight_layout()
    plt.show()

def plot_impulse_response_bs(sos, fs):
    impulse = np.zeros(100)
    impulse[0] = 1
    response = sosfilt(sos, impulse)

    time = np.arange(len(impulse)) / fs

    plt.figure()
    plt.stem(time, response, basefmt=" ", use_line_collection=True)
    plt.title('Impulsantwort - Bandsperre')
    plt.xlabel('Zeit [s]')
    plt.ylabel('Amplitude')
    plt.tight_layout()
    plt.show()

def plot_frequency_response_bs(sos, fs):
    w, h = sosfreqz(sos, worN=2000, fs=fs)

    max_freq = 2000
    mask = w <= max_freq
    w = w[mask]
    h = h[mask]

    plt.figure()
    plt.subplot(2, 1, 1)
    plt.plot(w, 20 * np.log10(np.abs(h)))
    plt.title('Frequenzantwort - Bandsperre')
    plt.xlabel('Frequenz (Hz)')
    plt.ylabel('Amplitude [dB]')
    plt.grid()
    
    plt.subplot(2, 1, 2)
    plt.plot(w, np.angle(h))
    plt.xlabel('Frequenz (Hz)')
    plt.ylabel('Phase (Radiant)')
    plt.grid()
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

def apply_filter_to_audio(signal, fs, fc, filter_type, Q_dB=None):
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
        plot_impulse_response(dt, RC, fs, filter_type)
        plot_frequency_response(filtered_signal, fs, filter_type)


def pingpong_effect(signal, fs, delay_ms=500):
    delay_samples = round(delay_ms / 1000 * fs)
    
    if signal.ndim == 2 and signal.shape[1] == 2:
        left_channel = signal[:, 0]
        right_channel = signal[:, 1]
    else:
        left_channel = signal
        right_channel = signal
    
    left_channel /= np.max(np.abs(left_channel))
    right_channel /= np.max(np.abs(right_channel))
    
    extra_L = np.zeros(delay_samples, dtype=int)
    extra_R = np.zeros(2 * delay_samples, dtype=int)
    
    left_delay_L_1 = np.append(extra_L, left_channel)
    left_delay_L = np.append(left_delay_L_1, extra_L)
    right_delay_L = np.append(right_channel, extra_R)
    
    left_delay_R = np.append(left_channel, extra_R)
    right_delay_R = np.append(extra_R, right_channel)
    
    stereo_delay_L = np.vstack((left_delay_L, right_delay_L)).T
    stereo_delay_R = np.vstack((left_delay_R, right_delay_R)).T
    
    stereo_delay_LR = (stereo_delay_L + stereo_delay_R) / 2
    
    left_new = np.append(left_channel, extra_R)
    right_new = np.append(right_channel, extra_R)
    stereo = np.vstack((left_new, right_new)).T
    
    stereo_output = stereo + stereo_delay_LR
    
    return stereo_output

def main():
    print("\nFILTER AUF NOISESIGNAL")
    # Benutzerabfrage nach dem Filtertyp
    filter_type = input("\nWelchen Filter möchten Sie anwenden? 'tp' für Tiefpass, 'hp' für Hochpass, 'bs' für Bandsperre: ").strip().lower()
    
    # Filtertyp überprüfen und anpassen
    if filter_type not in ['tp', 'hp', 'bs']:
        print("Unbekannter Filtertyp. Bitte 'tp', 'hp' oder 'bs' verwenden.")
        return
    
    # Parameter für den Filter
    fc = 700
    Q_dB = -3
    
    # Audiodateien laden
    fs_noise, noise_data = import_audio(noise_file)
    fs_voice, voice_data = import_audio(voice_file)
    
    if noise_data is None or voice_data is None:
        return
    
    # Filter anwenden basierend auf Benutzerwahl
    if filter_type == 'tp':
        apply_filter_to_audio(noise_data, fs_noise, fc, 'tp')
    elif filter_type == 'hp':
        apply_filter_to_audio(noise_data, fs_noise, fc, 'hp')
    elif filter_type == 'bs':
        apply_filter_to_audio(noise_data, fs_noise, fc, 'bs', Q_dB)
    
    # Ping Pong Delay 
    print("\nPING PONG DELAY EFFEKT AUF SPRACHSIGNAL")
    delay_abfrage = input("\nMöchten Sie den Ping Pong Effekt haben? [j/n] : ").strip().lower()

    if delay_abfrage == "j":
        processed_voice = pingpong_effect(voice_data, fs_voice)
        time.sleep(1)
        sd.play(processed_voice, fs_voice)
        sd.wait()
    elif delay_abfrage == "n":
        print("\nAufgabe übersprungen")
    
    #Effektanwendung auf Sprachsignal
    effekt_abfrage = input("\nMöchten Sie Tiefpass/Hochpass/Bandsperre auf das Sprachsignal\nTippen Sie [tp/hp/bs], wenn nicht tippen Sie [n]: ").strip().lower()

    if effekt_abfrage == 'tp':
        print("\nOriginaldatei wird abgespielt (zum Vergleichen)..")
        play_audio(voice_file)
        print("\nOriginaldatei mit Effekt wird abgespielt..")
        apply_filter_to_audio_onlyplay(voice_data, fs_voice, fc, 'tp')
    elif effekt_abfrage == 'hp':
        print("\nOriginaldatei wird abgespielt (zum Vergleichen)..")
        play_audio(voice_file)
        print("\nOriginaldatei mit Effekt wird abgespielt..")
        apply_filter_to_audio_onlyplay(voice_data, fs_voice, fc, 'hp')
    elif effekt_abfrage == 'bs':
        print("\nOriginaldatei wird abgespielt (zum Vergleichen)..")
        play_audio(voice_file)
        print("\nOriginaldatei mit Effekt wird abgespielt..")
        apply_filter_to_audio_onlyplay(voice_data, fs_voice, fc, 'bs', Q_dB)
    elif effekt_abfrage == "n":
        print("\nAufgabe übersprungen")
        
if __name__ == "__main__":
    main()
