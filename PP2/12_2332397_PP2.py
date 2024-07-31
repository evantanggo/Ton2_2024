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
import scipy.signal as consig
from scipy.fft import fft, fftfreq
import warnings
import time

# Basisverzeichnis, in dem sich das Skript befindet
base_dir = os.path.dirname(os.path.abspath(__file__))

spuren = [
    "ton2_4spuren-001.wav", # Schlagzeug
    "ton2_4spuren-002.wav", # Gesang
    "ton2_4spuren-003.wav", # E-Guitar
    "ton2_4spuren-004.wav"  # Trompete
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


import_a = os.path.join(base_dir, "gitarre.wav")  # für Aufgabeteil A
import_b = [os.path.join(base_dir, datei) for datei in spuren]  # für Aufgabeteil B
brir_files = [os.path.join(base_dir, file) for file in brir_files] # BRIRs

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
        mono_data_normalized = mono_data / max_amp
        return sample_rate, mono_data_normalized
    
    except Exception as e:
        print(f"Fehler beim Importieren der Daten aus {file_path}: {str(e)}")
        return None, None

# Funktion zum Abspielen des Sounds
def abspielen(signal, Fs):
    sd.play(signal, Fs)
    sd.wait()

# Funktion zur Anwendung von Laufzeitdifferenz
def zeitdifferenz(signal, Fs, delay_ms):
    if delay_ms is None:
        return np.zeros_like(signal), np.zeros_like(signal)
    t_samples = round(delay_ms / 1000 * Fs)
    if t_samples > 0:
        extra = np.zeros(t_samples, dtype=signal.dtype)
        return np.append(extra, signal)[:len(signal)], signal[:len(signal)-t_samples]
    else:
        t_samples = abs(t_samples)
        extra = np.zeros(t_samples, dtype=signal.dtype)
        return signal[:len(signal)-t_samples], np.append(extra, signal)[:len(signal)]

# Funktion zur Anwendung von Pegeldifferenz
def pegeldifferenz(signal, pegeldiff_db):
    if pegeldiff_db is None:
        return np.zeros_like(signal)
    return signal / (10 ** (pegeldiff_db / 20))

class Mischpult:
    def __init__(self, spuren):
        self.spuren = spuren # Initialisiere die Spuren (Dateipfade der Audiodateien)
    
    def mischen_a(self, delay_ms_list):
        # Importiere die Audiodaten und ihre Abtastraten
        sample_rate, signals = zip(*[import_data(file) for file in self.spuren])
        max_sample_rate = max(sample_rate)
        signals = list(signals)
        
        left_channels, right_channels = [], []
        for signal, delay_ms in zip(signals, delay_ms_list):
            # Erzeuge die linke und rechte Kanäle unter Berücksichtigung der Zeitdifferenz
            left, right = zeitdifferenz(signal, max_sample_rate, delay_ms)
            left_channels.append(left)
            right_channels.append(right)
        
        # Bestimme die minimale Länge der Kanäle, um sie auf dieselbe Länge zu bringen
        min_len = min(min(len(l) for l in left_channels), min(len(r) for r in right_channels))
        left_channels = [l[:min_len] for l in left_channels]
        right_channels = [r[:min_len] for r in right_channels]

        # Mische die Kanäle zusammen
        mixed_signal = np.zeros((min_len, 2))
        mixed_signal[:, 0] = sum(left_channels)
        mixed_signal[:, 1] = sum(right_channels)
        
        # Normalisiere das gemischte Signal, um Übersteuerungen zu vermeiden
        max_val = np.max(np.abs(mixed_signal))
        if max_val > 0:
            mixed_signal = mixed_signal / max_val
        
        # Spiele das gemischte Signal ab
        abspielen(mixed_signal, max_sample_rate)

    def mischen_b(self, pegeldiff_db_list):
        # Importiere die Audiodaten und ihre Abtastraten
        sample_rate, signals = zip(*[import_data(file) for file in self.spuren])
        max_sample_rate = max(sample_rate) # Bestimme die höchste Abtastrate
        signals = list(signals)
        
        left_channels, right_channels = [], []
        for signal, pegeldiff_db in zip(signals, pegeldiff_db_list):
            # Erzeuge die linke und rechte Kanäle unter Berücksichtigung der Pegeldifferenz
            left = signal
            right = pegeldifferenz(signal, pegeldiff_db)
            left_channels.append(left)
            right_channels.append(right)
        
        # Bestimme die minimale Länge der Kanäle, um sie auf dieselbe Länge zu bringen
        min_len = min(min(len(l) for l in left_channels), min(len(r) for r in right_channels))
        left_channels = [l[:min_len] for l in left_channels]
        right_channels = [r[:min_len] for r in right_channels]

        # Mische die Kanäle zusammen
        mixed_signal = np.zeros((min_len, 2))
        mixed_signal[:, 0] = sum(left_channels)
        mixed_signal[:, 1] = sum(right_channels)
        
        # Normalisiere das gemischte Signal, um Übersteuerungen zu vermeiden
        max_val = np.max(np.abs(mixed_signal))
        if max_val > 0:
            mixed_signal = mixed_signal / max_val
        
        abspielen(mixed_signal, max_sample_rate)  # Spiele das gemischte Signal ab

    def mischen_c(self, delay_ms_list, pegeldiff_db_list):
        # Importiere die Audiodaten und ihre Abtastraten
        sample_rate, signals = zip(*[import_data(file) for file in self.spuren])
        max_sample_rate = max(sample_rate)
        signals = list(signals)
        
        left_channels, right_channels = [], []
        for signal, delay_ms, pegeldiff_db in zip(signals, delay_ms_list, pegeldiff_db_list):
            # Erzeuge die linke und rechte Kanäle unter Berücksichtigung der Zeitdifferenz und Pegeldifferenz
            left, right = zeitdifferenz(signal, max_sample_rate, delay_ms)
            right = pegeldifferenz(right, pegeldiff_db)
            left_channels.append(left)
            right_channels.append(right)
        
        # Bestimme die minimale Länge der Kanäle, um sie auf dieselbe Länge zu bringen
        min_len = min(min(len(l) for l in left_channels), min(len(r) for r in right_channels))
        left_channels = [l[:min_len] for l in left_channels]
        right_channels = [r[:min_len] for r in right_channels]

        # Mische die Kanäle zusammen
        mixed_signal = np.zeros((min_len, 2))
        mixed_signal[:, 0] = sum(left_channels)
        mixed_signal[:, 1] = sum(right_channels)
        
        # Normalisiere das gemischte Signal, um Übersteuerungen zu vermeiden
        max_val = np.max(np.abs(mixed_signal))
        if max_val > 0:
            mixed_signal = mixed_signal / max_val
        
        abspielen(mixed_signal, max_sample_rate) # Spiele das gemischte Signal ab

    def mischen_brir(self, brir_files):
        # Importiere die Audiodaten und ihre Abtastraten
        sample_rate, signals = zip(*[import_data(file) for file in self.spuren])
        brir_sample_rate, brirs = zip(*[import_data(file) for file in brir_files])
        
        # Überprüfe, ob alle BRIR-Dateien die gleiche Abtastrate haben
        if len(set(brir_sample_rate)) != 1:
            raise ValueError("Alle BRIR-Dateien müssen die gleiche Abtastrate haben.")
        
        # Überprüfe, ob die Abtastraten der BRIR-Dateien mit denen der Audiodateien übereinstimmen
        if brir_sample_rate[0] != sample_rate[0]:
            raise ValueError("Die Abtastraten der BRIR-Dateien und Audiodateien müssen übereinstimmen.")
        
        max_sample_rate = max(sample_rate)
        signals = list(signals)
        
        convoluted_signals_left = []
        convoluted_signals_right = []

        for signal, brir in zip(signals, brirs):
            if brir.ndim == 1:
                # Mono BRIR, auf Stereo ausdehnen
                brir = np.column_stack((brir, brir))
            elif brir.ndim != 2 or brir.shape[1] != 2:
                raise ValueError("BRIR-Dateien müssen Stereo sein.")
            
            # Führe die Faltung des Signals mit den BRIR-Kanälen durch
            convoluted_left = consig.fftconvolve(signal, brir[:, 0], mode='full')[:len(signal)]
            convoluted_right = consig.fftconvolve(signal, brir[:, 1], mode='full')[:len(signal)]
            convoluted_signals_left.append(convoluted_left)
            convoluted_signals_right.append(convoluted_right)
        
        # Bestimme die minimale Länge der gefalteten Signale, um sie auf dieselbe Länge zu bringen
        min_len = min(min(len(l) for l in convoluted_signals_left), min(len(r) for r in convoluted_signals_right))
        convoluted_signals_left = [l[:min_len] for l in convoluted_signals_left]
        convoluted_signals_right = [r[:min_len] for r in convoluted_signals_right]

        # Mische die gefalteten Signale zusammen
        mixed_signal = np.zeros((min_len, 2))
        mixed_signal[:, 0] = sum(convoluted_signals_left)
        mixed_signal[:, 1] = sum(convoluted_signals_right)

        # Normalisiere das gemischte Signal, um Übersteuerungen zu vermeiden
        max_val = np.max(np.abs(mixed_signal))
        if max_val > 0:
            mixed_signal = mixed_signal / max_val
        
        abspielen(mixed_signal, max_sample_rate) # Spiele das gemischte Signal ab

class PhantomschallquelleGUI:
    def __init__(self):
        self.delay_ms = 0 # Initialisiere die Laufzeitdifferenz in Millisekunden
        self.pegeldiff_db = 0 # Initialisiere die Pegeldifferenz in Dezibel
        
        self.root = tk.Tk() # Erstelle das Hauptfenster der GUI
        self.root.title("Phantomschallquelle GUI") # Setze den Titel des Fensters
        
        self.setup_gui() # Rufe die Methode zur Einrichtung der GUI auf
        
    def setup_gui(self):
        # Erstelle und packe das Label für die Laufzeitdifferenz
        delay_label = ttk.Label(self.root, text="Laufzeitdifferenz (ms):")
        delay_label.pack()

        # Erstelle und packe den Schieberegler für die Laufzeitdifferenz
        self.delay_scale = tk.Scale(self.root, from_=-4, to=4, orient='horizontal', length=300, command=self.update_delay_label, resolution=0.1)
        self.delay_scale.pack()

        # Erstelle und packe das Label für den aktuellen Wert der Laufzeitdifferenz
        self.delay_value_label = ttk.Label(self.root, text="0.00 ms")
        self.delay_value_label.pack()

        # Erstelle und packe das Label für die Pegeldifferenz
        pegeldiff_label = ttk.Label(self.root, text="Pegeldifferenz (dB):")
        pegeldiff_label.pack()

        # Erstelle und packe den Schieberegler für die Pegeldifferenz
        self.pegeldiff_scale = tk.Scale(self.root, from_=-16, to=16, orient='horizontal', length=300, command=self.update_pegeldiff_label, resolution=0.1)
        self.pegeldiff_scale.pack()

        # Erstelle und packe das Label für den aktuellen Wert der Pegeldifferenz
        self.pegeldiff_value_label = ttk.Label(self.root, text="0.00 dB")
        self.pegeldiff_value_label.pack()

        # Erstelle und packe den "Play"-Button
        play_button = ttk.Button(self.root, text="Play", command=self.process_and_play)
        play_button.pack()

    def update_delay_label(self, value):
        self.delay_ms = float(value) # Aktualisiere die Laufzeitdifferenz
        self.delay_value_label.config(text=f"{self.delay_ms:.2f} ms")

    def update_pegeldiff_label(self, value):
        self.pegeldiff_db = float(value) # Aktualisiere die Pegeldifferenz
        self.pegeldiff_value_label.config(text=f"{self.pegeldiff_db:.2f} dB") # Aktualisiere das Label

    def process_and_play(self):
        sample_rate, audio_data = import_data(import_a) # Importiere die Audiodaten und die Abtastrate
        if sample_rate is not None and audio_data is not None:
            self.teil_a(audio_data, sample_rate, self.delay_ms, self.pegeldiff_db) # Verarbeite und spiele das Audio

    def teil_a(self, audio_data, sample_rate, delay_ms, pegeldiff_db):
        # Laufzeitdifferenz anwenden
        left_channel, right_channel = zeitdifferenz(audio_data, sample_rate, delay_ms)
        
        # Pegeldifferenz anwenden
        left_channel = pegeldifferenz(left_channel, -pegeldiff_db / 2)
        right_channel = pegeldifferenz(right_channel, pegeldiff_db / 2)
        
        # Mixed Signal erstellen
        mixed_signal = np.zeros((min(len(left_channel), len(right_channel)), 2))
        mixed_signal[:, 0] = left_channel[:len(mixed_signal)]
        mixed_signal[:, 1] = right_channel[:len(mixed_signal)]
        
        # Normalisierung
        max_val = np.max(np.abs(mixed_signal))
        if max_val > 0:
            mixed_signal = mixed_signal / max_val
        
        abspielen(mixed_signal, sample_rate) # Spiele das gemischte Signal ab

    def run(self):
        self.root.mainloop() # Starte die Hauptschleife der GUI

if __name__ == "__main__":
    print("\nGUI von Lokilasation von Phantomschalquelle\n")
    gui = PhantomschallquelleGUI()
    gui.run()

    mischpult = Mischpult(import_b)

    # Schlagzeug | Gesang | E-Guitar | Trompete
    # [-0.2, 0.1, -0.4, 0.4]
    print("------------------------------------------")
    print("\nStereomischung mit Laufzeitdifferenzen..")
    time.sleep(2)
    mischpult.mischen_a([-2, 1, -4, 4])  # Beispielwerte für Laufzeitdifferenz in ms
    time.sleep(2)  # 2 Sekunden Pause
    # E-Guitar und Schlahzeug eher nach links
    # Gesang bisschen nach rechts aber noch mittig
    # Trumphete nach rechts, damit mehr Balance mit der E-Guitar

    print("\nStereomischung mit Pegeldifferenzen..")
    mischpult.mischen_b([2, -1, 4, -4])  # Beispielwerte für Pegeldifferenz in dB
    time.sleep(2)  # 2 Sekunden Pause

    print("\nStereomischung mit Laufzeit- und Pegeldifferenzen..")
    mischpult.mischen_c([2.0, 2.0, 2.0, 2.0], [5.0, 5.0, 5.0, 5.0])  # Kombination von Laufzeit- und Pegeldifferenz
    time.sleep(2) # 2 Sekunden Pause
    print("\n------------------------------------------")

    print("\nStereomischung mit BRIRs..")
    mischpult.mischen_brir([brir_files[1], brir_files[0], brir_files[2], brir_files[6]])  # Beispiel BRIR Dateien
    print("\n------------------------------------------")