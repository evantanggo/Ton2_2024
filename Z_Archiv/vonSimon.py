import os
import numpy as np
import sounddevice as sd
import tkinter as tk
from tkinter import ttk
from scipy.io.wavfile import read
import warnings
from threading import Thread

# Globale Variable für das Signal und die Abtastrate
global_signal = np.zeros((0, 2))
global_fs = None
global_stream = None

# Funktion zum Abspielen des Sounds
def abspielen(signal, fs):
    global global_stream
    global_stream = sd.OutputStream(samplerate=fs, channels=2, callback=audio_callback)
    global_stream.start()

# Callback-Funktion für den Audio-Stream
def audio_callback(outdata, frames, time, status):
    global global_signal
    if len(global_signal) >= frames:
        outdata[:] = global_signal[:frames]
        global_signal = global_signal[frames:]
    else:
        outdata[:len(global_signal)] = global_signal
        outdata[len(global_signal):] = 0
        global_signal = np.zeros((0, 2))  # Stelle sicher, dass das Array die richtige Form hat

# Funktion zur Anwendung von Laufzeitdifferenz und Pegeldifferenz
def panning_effect(signal, fs, delay_ms, pegeldiff_db):
    global global_signal, global_fs
    global_signal = signal
    global_fs = fs

    # Zeitdifferenz in Array-Länge umgerechnet
    t_samples = round(delay_ms / 1000 * fs)

    # Signal für links und rechts anpassen
    if t_samples >= 0:
        extra = np.zeros(t_samples, dtype=signal.dtype)
        lc = np.append(extra, signal) * (10 ** (-pegeldiff_db / 20))
        rc = np.append(signal, extra)
    else:
        t_samples = abs(t_samples)
        extra = np.zeros(t_samples, dtype=signal.dtype)
        lc = np.append(signal, extra) * (10 ** (-pegeldiff_db / 20))
        rc = np.append(extra, signal)

    # Kürze das längere Signal, damit beide gleich lang sind
    min_len = min(len(lc), len(rc))
    lc = lc[:min_len]
    rc = rc[:min_len]

    stereo_a = np.vstack((lc, rc)).transpose()

    # Normalisierung, um Clipping zu vermeiden
    max_val = np.max(np.abs(stereo_a))
    if max_val > 0:
        stereo_a = stereo_a / max_val

    global_signal = stereo_a
    abspielen(stereo_a, fs)

# Funktion zur Verarbeitung und Anwendung der GUI-Eingaben
def process_and_play():
    delay_ms = delay_scale.get()
    pegeldiff_db = pegeldiff_scale.get()
    update_delay_label(delay_ms)
    update_pegeldiff_label(pegeldiff_db)
    fs, data = import_data()
    if fs is not None and data is not None:
        # Erstelle und starte einen neuen Thread für die Wiedergabe
        play_thread = Thread(target=panning_effect, args=(data, fs, delay_ms, pegeldiff_db))
        play_thread.start()
        # Deaktiviere den Play-Button während der Wiedergabe
        play_button.config(state='disabled')

# Funktion zum Stoppen der Wiedergabe mit Fade-Out
def stop_playing():
    global global_stream, global_signal
    if global_stream is not None and global_stream.active and global_signal.size > 0:
        fade_out_duration = min(20, len(global_signal))  # Anzahl der Abtastwerte für Fade-Out
        fade_out_signal = global_signal[-fade_out_duration:].copy()

        # Fade-Out anwenden
        for i in range(1, fade_out_duration + 1):
            fade_factor = (fade_out_duration - i) / fade_out_duration
            fade_out_signal[-i] *= fade_factor

        # Den Rest des Signals durch Nullwerte ersetzen
        global_signal[-fade_out_duration:] = fade_out_signal

        # Wiedergabe beenden
        global_stream.stop()
        global_stream.close()
        global_stream = None
        global_signal = np.zeros((0, 2))  # Stelle sicher, dass das Array die richtige Form hat

    # Aktiviere den Play-Button nach dem Stoppen der Wiedergabe
    play_button.config(state='normal')

# Funktion zum Importieren der Audiodaten
def import_data():
    # Basisverzeichnis, in dem sich das Skript befindet
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Datei untersuchen (verwenden Sie den relativen Pfad)
    file_path = os.path.join(base_dir, "gitarre.wav")
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

def exit_app():
    root.quit()

def aufgabe_1():
    global root, delay_scale, pegeldiff_scale, play_button, delay_value_label, pegeldiff_value_label

    # GUI-Fenster erstellen
    root = tk.Tk()
    x = 500
    y = 250
    root.geometry(f"{x}x{y}")
    root.title("Phantomschallquelle Aufgabenteil A")

    # Laufzeitdifferenz-Scale
    delay_label = ttk.Label(root, text="Laufzeitdifferenz (ms):")
    delay_label.pack()
    delay_min = -4
    delay_max = 4
    num_val = abs(delay_min) + abs(delay_max)
    delay_scale = tk.Scale(root, from_=delay_min, to=delay_max, orient='horizontal', length=300,
                            command=update_delay_label, resolution = 1.0)
    delay_scale.pack()
    delay_value_label = ttk.Label(root, text="0.00 ms")
    delay_value_label.pack()

    # Pegeldifferenz-Scale
    pegeldiff_label = ttk.Label(root, text="Pegeldifferenz (dB):")
    pegeldiff_label.pack()
    pegeldiff_scale = tk.Scale(root, from_=-16, to=16, orient='horizontal', length=300,
                                command=update_pegeldiff_label, resolution=1.0)
    pegeldiff_scale.pack()
    pegeldiff_value_label = ttk.Label(root, text="0.00 dB")
    pegeldiff_value_label.pack()

    # Button zum Abspielen des Sounds
    play_button = ttk.Button(root, text="Play", command=process_and_play)
    play_button.pack()

    # Button zum Stoppen der Wiedergabe
    stop_button = ttk.Button(root, text="Stop", command=stop_playing)
    stop_button.pack()

    # Exit-Button
    style = ttk.Style()
    style.configure('Exit.TButton', foreground='red', background='white')
    exit_button = ttk.Button(root, text="Exit", style='Exit.TButton', command=exit_app)
    exit_button.pack()

    # GUI-Loop starten
    root.mainloop()

if __name__ == "__main__":
    aufgabe_1()
