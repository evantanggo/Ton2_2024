import os
import numpy as np
import sounddevice as sd
import tkinter as tk
from tkinter import ttk
from scipy.io.wavfile import read
import warnings

# Funktion zum Abspielen des Sounds
def abspielen(signal, Fs):
    sd.play(signal, Fs)
    sd.wait()

# Funktion zur Anwendung von Laufzeitdifferenz und Pegeldifferenz
def teil_a(signal, Fs, delay_ms, pegeldiff_db):
    # Zeitdifferenz in Array-Länge umgerechnet
    t_samples = round(delay_ms / 1000 * Fs)
    
    # Signal für links und rechts anpassen
    if t_samples >= 0:
        extra = np.zeros(t_samples, dtype=signal.dtype)
        links_a = np.append(extra, signal) * (10 ** (-pegeldiff_db / 10))
        rechts_a = np.append(signal, extra)
    else:
        t_samples = abs(t_samples)
        extra = np.zeros(t_samples, dtype=signal.dtype)
        links_a = np.append(signal, extra) * (10 ** (-pegeldiff_db / 10))
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
    sample_rate, audio_data = import_data()
    if sample_rate is not None and audio_data is not None:
        teil_a(audio_data, sample_rate, delay_ms, pegeldiff_db)

# Funktion zum Importieren der Audiodaten
def import_data():
    file_path = "Fallstudie2/gitarre.wav"  # Hier den Dateipfad festlegen
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

# Funktion zur Aktualisierung der angezeigten Werte
def update_delay_label(value):
    delay_value_label.config(text=f"{float(value):.2f} ms")

def update_pegeldiff_label(value):
    pegeldiff_value_label.config(text=f"{float(value):.2f} dB")

# GUI-Fenster erstellen
root = tk.Tk()
root.title("Phantomschallquelle GUI")

# Laufzeitdifferenz-Scale
delay_label = ttk.Label(root, text="Laufzeitdifferenz (ms):")
delay_label.pack()
delay_scale = ttk.Scale(root, from_=-4, to=4, orient='horizontal', length=300, command=update_delay_label)
delay_scale.pack()
delay_value_label = ttk.Label(root, text="0.00 ms")
delay_value_label.pack()

# Pegeldifferenz-Scale
pegeldiff_label = ttk.Label(root, text="Pegeldifferenz (dB):")
pegeldiff_label.pack()
pegeldiff_scale = ttk.Scale(root, from_=-16, to=16, orient='horizontal', length=300, command=update_pegeldiff_label)
pegeldiff_scale.pack()
pegeldiff_value_label = ttk.Label(root, text="0.00 dB")
pegeldiff_value_label.pack()

# Button zum Abspielen des Sounds
play_button = ttk.Button(root, text="Play", command=process_and_play)
play_button.pack()

# GUI-Loop starten
root.mainloop()
