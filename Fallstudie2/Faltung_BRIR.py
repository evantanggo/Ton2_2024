import os
import numpy as np
import sounddevice as sd
import warnings
from scipy.io.wavfile import read
from scipy.signal import resample, fftconvolve
import time

base_dir = os.path.dirname(os.path.abspath(__file__))

spuren = [
    "ton2_4spuren-001.wav",  # Schlagzeug
    "ton2_4spuren-002.wav",  # Gesang
    "ton2_4spuren-003.wav",  # E-Guitar
    "ton2_4spuren-004.wav"   # Trompete
]

brir_files = [
    "BRIR_E/H12azi_0,0_ele_0,0.wav",
    "BRIR_E/H12azi_45,0_ele_0,0.wav",
    "BRIR_E/H12azi_90,0_ele_0,0.wav",
    "BRIR_E/H12azi_135,0_ele_0,0.wav",
    "BRIR_E/H12azi_180,0_ele_0,0.wav",
    "BRIR_E/H12azi_225,0_ele_0,0.wav",
    "BRIR_E/H12azi_270,0_ele_0,0.wav",
    "BRIR_E/H12azi_315,0_ele_0,0.wav"
]

import_b = [os.path.join(base_dir, datei) for datei in spuren]  # für Aufgabeteil B
brir_files = [os.path.join(base_dir, file) for file in brir_files]

# Funktion zum Importieren der Audiodaten
def import_data(file_path):
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Die Datei {file_path} existiert nicht.")
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            sample_rate, audio_data = read(file_path)
        
        if audio_data.ndim == 2:
            left_channel = audio_data[:, 0]
            right_channel = audio_data[:, 1]
            left_channel = 0.5 * left_channel
            right_channel = 0.5 * right_channel
            mono_data = (left_channel + right_channel) / 2
        else:
            mono_data = audio_data
        
        max_amp = np.max(np.abs(mono_data))
        if max_amp > 0:
            mono_data_normalized = mono_data / max_amp
        else:
            mono_data_normalized = mono_data
        return sample_rate, mono_data_normalized
    
    except Exception as e:
        print(f"Fehler beim Importieren der Daten aus {file_path}: {str(e)}")
        return None, None

def resample_signal(signal, original_fs, target_fs):
    num_samples = int(len(signal) * target_fs / original_fs)
    resampled_signal = resample(signal, num_samples)
    return resampled_signal

def convolve(signal1, signal2, target_fs=44100):
    fsa, a = signal1  # Import von Signal 1
    fsb, b = signal2  # Import von Signal 2

    # Resampling beider Signale auf die Zielabtastrate
    if fsa != target_fs:
        a = resample_signal(a, fsa, target_fs)
    if fsb != target_fs:
        b = resample_signal(b, fsb, target_fs)
    if fsb == fsa:
        fsa, a = signal1  # Import von Signal 1
        fsb, b = signal2

    # Faltungsoperation
    y_conv = fftconvolve(a, b, mode='full')

    # Normalisierung des gefalteten Signals
    max_amp = np.max(np.abs(y_conv))
    if max_amp > 0:  # Vermeidung von Division durch Null
        y_conv = y_conv / max_amp

    # Abspielen des gefalteten Signals
    sd.play(0.2*y_conv, target_fs)
    sd.wait()

    return y_conv

def play_sound(file_path):
    sample_rate, audio_data = import_data(file_path)
    if audio_data is not None:
        sd.play(0.2*audio_data, sample_rate, blocking=True)

def main():
    sample_rate, audio_data = import_data(import_b[0])
    sample_rate_brir, audio_data_brir = import_data(brir_files[2])
    print(sample_rate)
    play_sound(import_b[0])
    time.sleep(2)

    print("\n",sample_rate_brir)
    play_sound(brir_files[2])
    time.sleep(2)



    if audio_data is None or audio_data_brir is None:
        print("Fehler: Eine der Audiodateien konnte nicht importiert werden.")
        return

    convolve((sample_rate, audio_data), (sample_rate_brir, audio_data_brir))

if __name__ == "__main__":
    main()
