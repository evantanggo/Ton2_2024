"""
Ton2 SS24, Fallstudie
Praxisproblem 2
Evan Tanggo Peter Simamora
2332397
"""

import os
import numpy as np
import sounddevice as sd
import tkinter as tk
from tkinter import ttk
from scipy.io.wavfile import read
import warnings

base_dir = os.path.dirname(os.path.abspath(__file__))
import_a = os.path.join(base_dir, "gitarre.wav") # für Aufgabeteil A
spuren = [
    "ton2_4spuren-001.wav",
    "ton2_4spuren-002.wav",
    "ton2_4spuren-003.wav",
    "ton2_4spuren-004.wav"
]

import_b = [os.path.join(base_dir, datei) for datei in spuren] # für Aufgabeteil B

# Funktion zum Importieren der Audiodaten
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
            left_channel = 0.5 * left_channel
            right_channel = 0.5 * right_channel
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
    
# Funktion zum Abspielen des Sounds
def abspielen(signal, Fs):
    sd.play(signal, Fs)
    sd.wait()

# Funktion zur Anwendung von Laufzeitdifferenz und Pegeldifferenz
def teil_a(signal, Fs, delay_ms, pegeldiff_db):
    # Zeitdifferenz in Array-Länge umgerechnet
    t_samples = round(delay_ms / 1000 * Fs)
    
    # y-achse, bei pegeldiff rechts lauter
    # x -achse, bei zeitdiff links früher
    
    # Signal für links und rechts anpassen
    if t_samples >= 0:
        extra = np.zeros(t_samples, dtype=signal.dtype)
        links_a = np.append(extra, signal) 
        rechts_a = np.append(signal, extra)
    else:
        t_samples = abs(t_samples)
        extra = np.zeros(t_samples, dtype=signal.dtype)
        links_a = np.append(signal, extra) / (10 ** (pegeldiff_db / 20))
        rechts_a = np.append(extra, signal)
    
    # Kürze das längere Signal, damit beide gleich lang sind
    min_len = min(len(links_a), len(rechts_a))
    links_a = links_a[:min_len]
    rechts_a = rechts_a[:min_len]
    
    stereo_a = np.vstack((links_a, rechts_a)).transpose()
    
    # Normalisierung, um Clipping zu vermeiden
    max_val = np.max(np.abs(stereo_a))
    if max_val > 0:
        stereo_a = stereo_a / max_val
    
    abspielen(stereo_a, Fs)

# Funktion zur Verarbeitung und Anwendung der GUI-Eingaben
def process_and_play():
    delay_ms = delay_scale.get()
    pegeldiff_db = pegeldiff_scale.get()
    update_delay_label(delay_ms)
    update_pegeldiff_label(pegeldiff_db)
    sample_rate, audio_data = import_data(import_a)
    if sample_rate is not None and audio_data is not None:
        teil_a(audio_data, sample_rate, delay_ms, pegeldiff_db)

# Funktion zur Aktualisierung der angezeigten Werte
def update_delay_label(value):
    delay_value_label.config(text=f"{float(value):.2f} ms")

def update_pegeldiff_label(value):
    pegeldiff_value_label.config(text=f"{float(value):.2f} dB")

# Funktion zur Anwendung von Zeitdifferenz
def zeitdifferenz(signal, Fs, delay_ms):
    t_samples = round(delay_ms / 1000 * Fs)
    if t_samples >= 0:
        extra = np.zeros(t_samples, dtype=signal.dtype)
        signal_delayed = np.append(signal, extra)
        return signal, np.append(extra, signal)
    else:
        t_samples = abs(t_samples)
        extra = np.zeros(t_samples, dtype=signal.dtype)
        return np.append(signal, extra), np.append(extra, signal)
    
# Funktion zur Anwendung von Pegeldifferenz
def pegeldifferenz(signal, pegeldiff_db):
    return signal / (10 ** (pegeldiff_db / 20))


def mischen(spuren, delay_ms, pegeldiff_db):
    # Importiere und normalisiere die Spuren
    sample_rate, signals = zip(*[import_data(file) for file in spuren])
    max_sample_rate = max(sample_rate)
    
    # Konvertiere Tuple in Liste, damit wir Änderungen vornehmen können
    signals = list(signals)
    
    # Wenden Sie Zeitdifferenz auf die ersten beiden Spuren an
    links, rechts = zeitdifferenz(signals[0], max_sample_rate, delay_ms)
    rechts = pegeldifferenz(rechts, pegeldiff_db)
    
    # Wenden Sie Pegeldifferenz auf die letzten beiden Spuren an
    signals[2] = pegeldifferenz(signals[2], pegeldiff_db)
    signals[3] = pegeldifferenz(signals[3], pegeldiff_db)
    
    # Berechne die minimale Länge für die Mischung
    min_len = min(len(links), len(rechts), len(signals[2]), len(signals[3]))
    
    # Kürze die Signale auf die minimale Länge
    links = links[:min_len]
    rechts = rechts[:min_len]
    signals[2] = signals[2][:min_len]
    signals[3] = signals[3][:min_len]
    
    # Erstellen Sie die Stereo-Mischung
    mixed_signal = np.zeros((min_len, 2))
    mixed_signal[:, 0] = links + signals[1]
    mixed_signal[:, 1] = rechts + signals[2] + signals[3]
    
    # Normalisierung
    max_val = np.max(np.abs(mixed_signal))
    if max_val > 0:
        mixed_signal = mixed_signal / max_val
    
    return max_sample_rate, mixed_signal

# Funktion zur Verarbeitung der Spuren für Aufgabe B
def aufgabe_b(delay_ms, pegeldiff_db):
    sample_rate, mixed_signal = mischen(import_b, delay_ms, pegeldiff_db)
    #output_file = "gemischte_spuren.wav"
    #os.write(output_file, sample_rate, mixed_signal.astype(np.float32))
    #print(f"Die gemischte Datei wurde erstellt: {output_file}")

    # Optional: Abspielen der gemischten Datei
    abspielen(mixed_signal, sample_rate)


def aufgabe_a():
    global delay_scale, pegeldiff_scale, delay_value_label, pegeldiff_value_label

    # GUI-Fenster erstellen
    root = tk.Tk()
    root.title("Phantomschallquelle GUI")

    # Laufzeitdifferenz-Scale
    delay_label = ttk.Label(root, text="Laufzeitdifferenz (ms):")
    delay_label.pack()
    delay_scale = tk.Scale(root, from_=-4, to=4, orient='horizontal', length=300, command=update_delay_label, resolution = 0.1)
    delay_scale.pack()
    delay_value_label = ttk.Label(root, text="0.00 ms")
    delay_value_label.pack()

    # Pegeldifferenz-Scale
    pegeldiff_label = ttk.Label(root, text="Pegeldifferenz (dB):")
    pegeldiff_label.pack()
    pegeldiff_scale = tk.Scale(root, from_=-16, to=16, orient='horizontal', length=300, command=update_pegeldiff_label, resolution = 0.1)
    pegeldiff_scale.pack()
    pegeldiff_value_label = ttk.Label(root, text="0.00 dB")
    pegeldiff_value_label.pack()

    # Button zum Abspielen des Sounds
    play_button = ttk.Button(root, text="Play", command=process_and_play)
    play_button.pack()

    # GUI-Loop starten
    root.mainloop()

if __name__ == "__main__":
    aufgabe_a()
    aufgabe_b(2.0, 4.0)
